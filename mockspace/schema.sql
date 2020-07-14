-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS service;
DROP TABLE IF EXISTS method;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE service (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE method (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  service_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  status_code NOT NULL DEFAULT 200,
  delay NOT NULL DEFAULT 0,
  supported_method NOT NULL DEFAULT 'GET',
  headers,
  FOREIGN KEY (author_id) REFERENCES user (id),
  FOREIGN KEY (service_id) REFERENCES service (id)
);