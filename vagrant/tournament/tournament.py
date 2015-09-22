#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM matches;")
    conn.commit()
    cursor.close()
    conn.close()


def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM players;")
    conn.commit()
    cursor.close()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(name) FROM players;")
    player_count = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return player_count


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO players (name) VALUES (%s);", (name,))
    conn.commit()
    cursor.close()
    conn.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a
    player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = connect()
    cursor = conn.cursor()
    # Get two SQL queries (one for wins and one for losses) and join them together to get all four columns
    cursor.execute("SELECT wins.id, wins.name, wins.wins, wins.wins+losses.losses FROM (SELECT players.id AS id, players.name AS name, COUNT(matches.winner) AS wins FROM players LEFT JOIN matches ON players.id = matches.winner GROUP BY players.name, players.id ORDER BY wins DESC) wins LEFT JOIN (SELECT players.id AS id, players.name AS name, COUNT(matches.loser) AS losses FROM players LEFT JOIN matches ON players.id = matches.loser GROUP BY players.name, players.id) losses ON wins.id = losses.id ORDER BY wins.wins DESC;")
    return_value = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return return_value


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO matches (winner, loser) VALUES (%s, %s);", (winner, loser))
    conn.commit()
    cursor.close()
    conn.close()
 
 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    standings = playerStandings()
    pairs = []
    # There may be a better way to loop through the standings in pairs, but this works for now
    for pair in range(len(standings)/2):
        pairs.append((standings[2*pair][0], standings[2*pair][1],standings[2*pair+1][0], standings[2*pair+1][1]))
    return pairs
