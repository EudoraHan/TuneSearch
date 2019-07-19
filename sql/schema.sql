DROP SCHEMA IF EXISTS proj1 CASCADE;
CREATE SCHEMA IF NOT EXISTS proj1;

CREATE TABLE proj1.artist (
 artist_id INTEGER PRIMARY KEY,
 artist_name VARCHAR(255)
);


CREATE TABLE proj1.token (
 song_id INTEGER,
 token VARCHAR(255),
 count INTEGER,
 PRIMARY KEY (song_id, token)
);

CREATE TABLE proj1.song (
 song_id INTEGER PRIMARY KEY,
 artist_id INTEGER REFERENCES proj1.artist(artist_id),
 song_name VARCHAR(255),
 page_link VARCHAR(1000)
);


