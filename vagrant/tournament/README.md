# P2 Tournament Results

This is made to be run in a VM which includes PostgreSQL, Python, and pyscopg2

## Getting started

In order to run the tests for this application:

Make sure you're in the `tournament` folder

Start psql:

```
psql
```
In psql, import this SQL file to create the database and the schema, and then use ctrl-D to exit

```
\i tournament.sql
^D
```
Run the tests
```
python tournament_test.py
```
