import sqlite3
import os
import requests
import json
import re
from lyrics import createDatabase, getLyrics, countLyrics

""" 
given cur and conn to BeatlesMusic database
creates a table for ALL lyrics with song_id as primary integer key with a column for the lyric and the number of times the lyric shows up (quantity)
"""
def createLyricsMasterTable(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Lyrics_MASTER (lyric_id INTEGER PRIMARY KEY, lyric TEXT, quantity INTEGER, song_id INTEGER)")
    conn.commit()

""" 
given cur and conn to BeatlesMusic database
uses getLyrics and countLyrics to get the data
then puts the data from the getLyrics and countLyrics into their cooresponding columns in Lyrics_MASTER table
"""
def addAllSongLyrics(cur, conn):
    # makes sure that data doesn't repeat
    all_ids = cur.execute("SELECT song_id FROM Lyrics_MASTER")
    all_ids = cur.fetchall()
    if len(all_ids) > 0 and all_ids[-1][0] == 140:
        return

    cur.execute("SELECT song_id FROM Tracks")
    ids = cur.fetchall()

    for id in ids:
        id = id[0]
        all_lyrics = getLyrics(id, cur)

        if len(all_lyrics) > 0:
            lyric_dic = countLyrics(all_lyrics)
            for lyric in lyric_dic.keys():
                cur.execute("INSERT INTO Lyrics_MASTER (lyric, quantity, song_id) VALUES (?, ?, ?)", (lyric, lyric_dic[lyric], id))

    conn.commit()

def main():
    cur, conn = createDatabase("BeatlesMusic.db")
    createLyricsMasterTable(cur, conn)
    addAllSongLyrics(cur, conn)
    conn.close()

if __name__ == "__main__":
    main()