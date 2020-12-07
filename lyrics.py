import sqlite3
import os
import requests
import json
import re

""" 
finds the database to use given the name of the database 
returns cur and conn to the database 
"""
def createDatabase(name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+name)
    cur = conn.cursor()
    return cur, conn
    
""" 
given cur and conn for the correct database
creates a table for lyrics with song_id as primary integer key with a column for the lyric and the number of times the lyric shows up (quantity)
"""
def createLyricsTable(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Lyrics (lyric_id INTEGER PRIMARY KEY, lyric TEXT, quantity INTEGER, song_id INTEGER)")
    conn.commit()

"""
given cur and conn to the correct database and id for the song in the Tracks
uses the lyrics api to find the lyrics of the song
returns the lyrics for the song as a singular string
"""
def getLyrics(id, cur, conn):
    cur.execute("SELECT song_name FROM Tracks WHERE song_id = ?", (str(id),))
    name = cur.fetchone()
    name = name[0]
    url = f"https://api.lyrics.ovh/v1/Beatles/{name}"

    try:
        request = requests.get(url)
        response = json.loads(request.text)
        lyrics = response['lyrics']
    except: 
        lyrics = ""

    return lyrics

"""
given a string containing all of the lyrics for a song
finds the number of times the lyric line shows up in the song
returns a dictionary with the key being the lyric line and the value being the number of times the lyric shows up
"""
def countLyrics(all_lyrics):
    lyrics = all_lyrics.split('\n')
    dic = {}
    
    for lyric in lyrics:
        # changes everything to lowercase since there was inconsistent casing and spacing with the lyrics
        lyric = lyric.lower()
        # removed everything in () since people left personal comments in the lyrics
        lyric = re.sub(r'\(.*\)\s?', '', lyric)
        lyric = lyric.strip().strip(".,")

        if lyric != '':
            dic[lyric] = dic.get(lyric, 0) + 1

    return dic

""" 
given cur and conn to the correct database
uses getLyrics and countLyrics to get the data to put into the Lyrics table
then puts the data from the getLyrics and countLyrics into their cooresponding columns
for a max of 25 songs at time
"""
def insertData(cur, conn):
    # finds where last left off
    all_ids = cur.execute("SELECT song_id FROM Lyrics")
    all_ids = cur.fetchall()

    if len(all_ids) > 0:
        if all_ids[-1][0] > 137:
            return
        end_id = all_ids[-1][0]
    else:
        end_id = 0

    # gets the next songs (max 25 songs)
    cur.execute("SELECT song_id FROM Tracks WHERE song_id > ? LIMIT 25", (end_id,))
    ids = cur.fetchall()

    for id in ids:
        id = id[0]
        all_lyrics = getLyrics(id, cur, conn)

        if len(all_lyrics) > 0:
            lyric_dic = countLyrics(all_lyrics)
            for lyric in lyric_dic.keys():
                cur.execute("INSERT INTO Lyrics (lyric, quantity, song_id) VALUES (?, ?, ?)", (lyric, lyric_dic[lyric], id))

    conn.commit()
            

def main():
    cur, conn = createDatabase("BeatlesMusic.db")
    createLyricsTable(cur, conn)
    insertData(cur, conn)
    conn.close()

if __name__ == "__main__":
    main()