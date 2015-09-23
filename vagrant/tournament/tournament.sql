-- Table definitions for the tournament project.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.


-- We don't care about old data when running these tests, so delete the old database
DROP DATABASE IF EXISTS tournament;

-- Create the database, but it only supports one tournament at a time for now
CREATE DATABASE tournament;

-- Tell psql to change to the newly-created tournament database
\c tournament;

-- Create the players table.  Two players can have the same name, but will have different IDs
CREATE TABLE players(
	id serial PRIMARY KEY,
	name varchar(100) NOT NULL
);

-- Create the matches table.  We don't need IDs here, as we don't use the sequence or refer to specific matches
CREATE TABLE matches(
	winner integer NOT NULL,
	loser integer NOT NULL
);
