import sqlite3

DB_PATH = 'crisisconnect.db'

SCHEMA_FILE = 'schema.sql'

SAMPLE_RESOURCES = [
    ('Central Shelter', 'shelter', '123 Main St', '94101', 37.7749, -122.4194, 50, 50, '555-0100'),
    ('Downtown Clinic', 'medical', '456 Oak Ave', '94101', 37.7750, -122.4183, 30, 30, '555-0123'),
    ('City Food Bank', 'food', '789 Pine Rd', '94102', 37.7790, -122.4170, 100, 100, '555-0145')
]

SAMPLE_USERS = [
    ('Alice',),
    ('Bob',)
]

def main():
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_FILE) as f:
        conn.executescript(f.read())

    cur = conn.cursor()
    cur.executemany(
        'INSERT INTO resources (name, type, address, zip_code, latitude, longitude, capacity, available, contact) VALUES (?,?,?,?,?,?,?,?,?)',
        SAMPLE_RESOURCES
    )
    cur.executemany('INSERT INTO users (name) VALUES (?)', SAMPLE_USERS)
    conn.commit()
    conn.close()
    print('Database initialized with sample data.')

if __name__ == '__main__':
    main()
