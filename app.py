from flask import Flask, request, jsonify, abort
import sqlite3
import math

DB_PATH = 'crisisconnect.db'

app = Flask(__name__)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


@app.route('/api/resources')
def list_resources():
    zip_code = request.args.get('zip')
    r_type = request.args.get('type')
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)

    if not zip_code and (lat is None or lon is None):
        abort(400, 'zip or lat/lon required')

    conn = get_db()
    cur = conn.cursor()
    query = "SELECT r.*, IFNULL(avg_rev.avg_rating, 0) AS rating FROM resources r " \
            "LEFT JOIN (SELECT resource_id, AVG(rating) AS avg_rating FROM reviews GROUP BY resource_id) avg_rev " \
            "ON r.id = avg_rev.resource_id WHERE 1=1"
    params = []
    if zip_code:
        query += " AND r.zip_code = ?"
        params.append(zip_code)
    if r_type:
        query += " AND r.type = ?"
        params.append(r_type)

    cur.execute(query, params)
    resources = []
    for row in cur.fetchall():
        distance = None
        if lat is not None and lon is not None:
            distance = haversine(lat, lon, row['latitude'], row['longitude'])
        resources.append({
            'id': row['id'],
            'name': row['name'],
            'type': row['type'],
            'address': row['address'],
            'zip_code': row['zip_code'],
            'capacity': row['capacity'],
            'available': row['available'],
            'contact': row['contact'],
            'rating': row['rating'],
            'distance_km': distance
        })

    # sort by distance (if provided), availability desc, rating desc
    def sort_key(res):
        return (
            res['distance_km'] if res['distance_km'] is not None else float('inf'),
            -res['available'],
            -res['rating']
        )

    resources.sort(key=sort_key)
    return jsonify(resources)


@app.route('/api/resources', methods=['POST'])
def create_resource():
    data = request.json
    required = ['name', 'type', 'address', 'zip_code', 'latitude', 'longitude', 'capacity', 'available']
    if not all(k in data for k in required):
        abort(400, 'missing fields')

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO resources (name, type, address, zip_code, latitude, longitude, capacity, available, contact)\n'
        'VALUES (?,?,?,?,?,?,?,?,?)',
        (
            data['name'], data['type'], data['address'], data['zip_code'], data['latitude'],
            data['longitude'], data['capacity'], data['available'], data.get('contact')
        )
    )
    conn.commit()
    return jsonify({'id': cur.lastrowid}), 201


@app.route('/api/resources/<int:resource_id>', methods=['PUT'])
def update_resource(resource_id):
    data = request.json
    fields = ['name', 'type', 'address', 'zip_code', 'latitude', 'longitude', 'capacity', 'available', 'contact']
    sets = []
    values = []
    for f in fields:
        if f in data:
            sets.append(f"{f} = ?")
            values.append(data[f])
    if not sets:
        abort(400, 'no fields to update')

    values.append(resource_id)
    conn = get_db()
    conn.execute(f"UPDATE resources SET {', '.join(sets)} WHERE id = ?", values)
    conn.commit()
    return '', 204


@app.route('/api/resources/<int:resource_id>', methods=['DELETE'])
def delete_resource(resource_id):
    conn = get_db()
    conn.execute('DELETE FROM resources WHERE id = ?', (resource_id,))
    conn.commit()
    return '', 204


@app.route('/api/resources/<int:resource_id>/reviews')
def list_reviews(resource_id):
    conn = get_db()
    cur = conn.execute('SELECT users.name as user_name, rating, comment, created_at FROM reviews JOIN users ON reviews.user_id = users.id WHERE resource_id = ? ORDER BY created_at DESC', (resource_id,))
    return jsonify([dict(row) for row in cur.fetchall()])


@app.route('/api/resources/<int:resource_id>/reviews', methods=['POST'])
def add_review(resource_id):
    data = request.json
    if not {'user_id', 'rating'} <= data.keys():
        abort(400, 'user_id and rating required')
    conn = get_db()
    conn.execute('INSERT INTO reviews (user_id, resource_id, rating, comment) VALUES (?,?,?,?)',
                 (data['user_id'], resource_id, data['rating'], data.get('comment')))
    conn.commit()
    return '', 201


if __name__ == '__main__':
    app.run(debug=True)
