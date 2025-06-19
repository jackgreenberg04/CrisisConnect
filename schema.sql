-- Schema for CrisisConnect SQLite database

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    address TEXT NOT NULL,
    zip_code TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    capacity INTEGER NOT NULL,
    available INTEGER NOT NULL,
    contact TEXT
);

CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    resource_id INTEGER NOT NULL,
    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(resource_id) REFERENCES resources(id)
);

CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    resource_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(resource_id) REFERENCES resources(id)
);

-- Trigger to reduce availability when a reservation is made
CREATE TRIGGER IF NOT EXISTS reserve_resource
AFTER INSERT ON reservations
BEGIN
    UPDATE resources SET available = available - 1
    WHERE id = NEW.resource_id AND available > 0;
END;

-- Trigger to increase availability when a reservation is cancelled
CREATE TRIGGER IF NOT EXISTS release_resource
AFTER DELETE ON reservations
BEGIN
    UPDATE resources SET available = available + 1
    WHERE id = OLD.resource_id;
END;

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_resources_zip_type ON resources(zip_code, type);
CREATE INDEX IF NOT EXISTS idx_reviews_resource ON reviews(resource_id);

