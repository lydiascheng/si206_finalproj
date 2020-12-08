from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import sqlite3
import os
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="fff67bdb82444b0e83669f60152a06ac",
                                                           client_secret="538bc3d2fe0c41138a2abfbaea1b0144"))

""" Function to create database to store our API data"""
def createDatabase(name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+name)
    cur = conn.cursor()
    return cur, conn

""" Function to set up tracklist and popularity score table in database for The Beatles songs"""
def createTracksTable(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Tracks (song_id INTEGER PRIMARY KEY, song_name TEXT, popularity INTEGER)")
    conn.commit()

""" Function to populate Tracks table"""
def populateTracksTable(cur, conn):
    playlist_id = "1N908JjGGIXfOEYUKs90e6"
    cur.execute("SELECT COUNT(*) FROM Tracks")
    #sets count to end
    count = 141
    #updates count based on where last api call left off
    #105 songs is how many should be in the database
    for row in cur:
        if row[0] == 105:
            break
        else:
            count = row[0]
    results = sp.playlist_tracks(playlist_id, limit=25, offset=count)
    for item in results['items']:
        track = item['track']['name']
        track_split = track.split('-')
        trackname = track_split[0].strip()
        popularity = item['track']['popularity']
        cur.execute("INSERT INTO Tracks (song_name, popularity) VALUES (?, ?)", (str(trackname), int(popularity)))
    conn.commit()

""" Delete track table rows with no popularity score"""
def deleteZeroPopularityTracks(cur, conn):
    cur.execute("DELETE FROM Tracks WHERE popularity = 0")
    cur.execute("DELETE FROM Tracks WHERE popularity = 1")
    conn.commit()

def main():
    cur, conn = createDatabase("BeatlesMusic.db")
    createTracksTable(cur, conn)
    populateTracksTable(cur, conn)
    cur.execute("SELECT COUNT (*) FROM Tracks")
    for row in cur:
        count = row[0]
    #delete scores with zero popularity scores once database is populated with all songs from playlist
    if count == 141:
        deleteZeroPopularityTracks(cur, conn)
    conn.close()

if __name__ == "__main__":
    main()
