CREATE TABLE lot (
id TEXT PRIMARY KEY,
available INTEGER NOT NULL CHECK(available>=0),
expires INTEGER NOT NULL CHECK(expires>available),
units INTEGER NOT NULL CHECK(units>=0)
);