# P2 Tournament Results

This is made to be run in a VM which includes PostgreSQL, Python, and pyscopg2

## Getting started

In order to run the tests for this application:

0. Make sure you're in the `tournament` folder

1. Start psql:

```
psql
```
2. In psql, import this SQL file to create the database, and then use ctrl-D to exit

```
\i tournament.sql
^D
```
3. Run the tests
```
python tournament_test.py
```
