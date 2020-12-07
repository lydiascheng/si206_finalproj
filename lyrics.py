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
given cur and conn to BeatlesMusic database
creates a table for lyrics with song_id as primary integer key with a column for the lyric and the number of times the lyric shows up (quantity)
"""
def createLyricsTable(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Lyrics (lyric_id INTEGER PRIMARY KEY, lyric TEXT, quantity INTEGER, song_id INTEGER)")
    conn.commit()

"""
given cur to BeatlesMusic database and id for the song in the Tracks
uses the lyrics api to find the lyrics of the song
returns the lyrics for the song as a singular string
"""
def getLyrics(id, cur):
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
returns a dictionary with the keys being the lyric line and the values being the number of times the lyric shows up
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
given cur to BeatlesMusic database
finds the 2 songs that with the highest popularity score, 3 in the middle (middle being nearest to the median), and 2 with the lowest
returns the 7 songs as a list in order of most popular to least popular
"""
def someStats(cur):
    dic = {}
    sample = []

    cur.execute("SELECT song_id, popularity FROM Tracks")
    songs = cur.fetchall()
    
    songs = sorted(songs, key = lambda t : t[1], reverse = True)
    dic['high'] = songs[:2]
    dic['medium'] = songs[len(songs) // 2 - 1: len(songs) // 2 + 2]
    dic['low'] = songs[-2:]

    for category in dic:
        for song in dic[category]:
            sample.append(song[0])

    return sample

"""
given cur to BeatlesMusic database and list returned from someStats()
returns the song id to find lyrics for based on previously gathered lyrics
returns -1 if done gathering lyrics for selected sample of songs
"""
def whichSong(cur, songs):
    all_ids = cur.execute("SELECT song_id FROM Lyrics")
    all_ids = cur.fetchall()

    # finds the song id for the last song that we got lyrics for
    # returns -1 if done and the id for the first song if haven't gotten any song lyrics yet
    if len(all_ids) > 0:
        if all_ids[-1][0] == 76:
            return -1
        end_id = all_ids[-1][0]
    else:
        return songs[0]

    song_id = songs[songs.index(end_id) + 1]
    return song_id

"""
given cur and conn to BeatlesMusic database and list returned from someStats()
uses getLyrics and countLyrics to get the data for the songs in the dict
then puts the data from the getLyrics and countLyrics into their cooresponding columns in Lyrics table
"""
def addIndividualLyrics(cur, conn, songs):
    song = whichSong(cur, songs)
    if song == -1:
        return

    all_lyrics = getLyrics(song, cur)
    
    if len(all_lyrics) > 0:
        lyric_dic = countLyrics(all_lyrics)
        for lyric in lyric_dic.keys():
            cur.execute("INSERT INTO Lyrics (lyric, quantity, song_id) VALUES (?, ?, ?)", (lyric, lyric_dic[lyric], song))

    conn.commit()
            

def main():
    cur, conn = createDatabase("BeatlesMusic.db")
    createLyricsTable(cur, conn)
    songs = someStats(cur)
    addIndividualLyrics(cur, conn, songs)
    conn.close()

if __name__ == "__main__":
    main()