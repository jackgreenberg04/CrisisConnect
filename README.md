# CrisisConnect

CrisisConnect is a prototype web service that helps users locate nearby emergency resources such as shelters, medical centers and food banks.

This repository contains a small Flask application backed by a SQLite database. It demonstrates how SQL can be used to manage resources, reviews and reservations.

## Setup

1. Ensure Python 3 is installed.
2. Install requirements:
   ```bash
   pip install flask
   ```
3. Initialize the database and insert sample data:
   ```bash
   python3 setup_db.py
   ```
4. Start the development server:
   ```bash
   python3 app.py
   ```
5. The API will be available at `http://localhost:5000`.

## API Endpoints

- `GET /api/resources?zip=<ZIP>&type=<TYPE>&lat=<lat>&lon=<lon>` – list resources filtered by ZIP and type. If latitude and longitude are provided, results are sorted by distance.
- `POST /api/resources` – create a new resource. JSON body must include fields `name`, `type`, `address`, `zip_code`, `latitude`, `longitude`, `capacity`, and `available`.
- `PUT /api/resources/<id>` – update an existing resource.
- `DELETE /api/resources/<id>` – remove a resource.
- `GET /api/resources/<id>/reviews` – list reviews for a resource.
- `POST /api/resources/<id>/reviews` – add a new review. JSON body requires `user_id` and `rating`.

## Database Schema

The schema is defined in [`schema.sql`](schema.sql). It includes:

- `users` – application users.
- `resources` – emergency resource locations.
- `reviews` – user ratings and comments.
- `reservations` – tracks reservations of limited resources.

Triggers automatically decrement available spots when a reservation is created and increment when a reservation is removed.

Indexes on ZIP code/type and resource reviews help performance.

## Example Query

```
curl 'http://localhost:5000/api/resources?zip=94101&type=shelter&lat=37.77&lon=-122.41'
```

This returns a JSON array of resources ordered by proximity, availability and rating.

