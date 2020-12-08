import sqlite3
import os
import numpy as np
from lyrics import createDatabase

""" Joins the Tracks and Lyrics tables to return song names and popularity scores from 2 most popular, 2 lease popular, and 3 median popular songs"""
def getSongNamesAndPopularity(cur, conn):
    cur.execute("SELECT Tracks.popularity, Tracks.song_name FROM Tracks join Lyrics ON Tracks.song_id = Lyrics.song_id")
    titles_and_popularity = {}
    for song in cur:
        titles_and_popularity[song[1]] = song[0]
    song_titles = list(titles_and_popularity.keys())
    return(f"From the 105 Beatles songs in the database, the two most popular songs according to Spotify's Popularity metric are {song_titles[0]} and {song_titles[1]} with a respective popularity score of {titles_and_popularity[song_titles[0]]} and {titles_and_popularity[song_titles[1]]}. \nThe three songs with an average popularity based on the median popularity score out of all of the songs are {song_titles[2]}, {song_titles[3]}, and {song_titles[4]} with a respective popularity score of {titles_and_popularity[song_titles[2]]}, {titles_and_popularity[song_titles[3]]}, and {titles_and_popularity[song_titles[4]]}.\nThe two least popular songs are {song_titles[5]} and {song_titles[6]} with a respective popularity score of {titles_and_popularity[song_titles[5]]} and {titles_and_popularity[song_titles[6]]}. \n")

""" Return average number of unique lines from songs in database"""
def getAverageUniqueLinesMaster(cur, conn):
    song_ids = []
    cur.execute("SELECT song_id From Lyrics_MASTER")
    for song_id in cur:
        if song_id[0] not in song_ids:
            song_ids.append(song_id[0])
    unique_lines = []
    for song_id in song_ids:
        cur.execute(f"SELECT count(*) from Lyrics_MASTER where song_id = {song_id}")
        for count in cur:
            unique_lines.append(int(count[0]))
    avg_unique_lines = np.mean(unique_lines)
    return(avg_unique_lines)

""" Returns dictionary of song titles from Lyrics table as keys and number of unique lines as values"""
def getUniqueLinesLyrics(cur, conn):
    song_ids = []
    cur.execute("SELECT song_id From Lyrics")
    for song_id in cur:
        if song_id[0] not in song_ids:
            song_ids.append(song_id[0])
    cur.execute("SELECT Tracks.song_name FROM Tracks join Lyrics ON Tracks.song_id=Lyrics.song_id")
    song_names = []
    for song in cur:
        if song[0] not in song_names:
            song_names.append(song[0])
    lines_count = []
    for song_id in song_ids:
        cur.execute(f"SELECT count (*) FROM Lyrics where song_id = {song_id}")
        for value in cur:
            count = value[0]
            lines_count.append(count)
    uniqueLinesDict = {}
    for i in range(len(song_names)):
        uniqueLinesDict[song_names[i]] = lines_count[i]
    return(uniqueLinesDict)

""" Returns a list of tuples with each tuple in the format (song's popularity score, quantity of song's most repeated song lyric) """
def getPopularityAndMostRepeatedLineQty(cur, conn):
    popularity_tuples = []
    popularities = []
    song_ids = []
    cur.execute("SELECT Tracks.popularity, Lyrics_MASTER.song_id FROM Tracks join Lyrics_MASTER ON Tracks.song_id = Lyrics_MASTER.song_id")
    for item in cur:
        if item not in popularity_tuples:
            popularity_tuples.append(item)
    for item in popularity_tuples:
        popularities.append(item[0])
        song_ids.append(item[1])
    quantities = []
    for song_id in song_ids:
        cur.execute(f"SELECT quantity FROM Lyrics_MASTER where song_id = {song_id}")
        quantity_list = []
        for quantity in cur:
            quantity_list.append(quantity[0])
        highest_qty = max(quantity_list)
        quantities.append(highest_qty)
    popularities_and_qtys = []
    for i in range(len(popularities)):
        popularities_and_qtys.append((popularities[i], quantities[i]))
    return(popularities_and_qtys)

""" Returns string with how much the number of lines in the 7 songs in the Lyrics table differs from the average number of lines from all the songs"""
def getAverageSongDifference(cur, conn):
    avg_unique_lines = getAverageUniqueLinesMaster(cur, conn)
    unique_lines_dict = getUniqueLinesLyrics(cur, conn)
    unique_lines_differences = unique_lines_dict.copy()
    song_names = list(unique_lines_differences.keys())
    output_list = [] 
    for song in song_names:
        unique_lines_differences[song] = round(unique_lines_differences[song] - avg_unique_lines, 2)
        output = f"The song {song} differs from the average number of unique lines per song by {unique_lines_differences[song]} lines.\n"
        output_list.append(output)
    final_output = str(''.join(output_list))
    return(final_output)

""" Find correlation coefficient between Beatles song popularity and number of times the song's most repetitive lyric was sung"""
def getCorrelationCoefficient(cur, conn):
    values = getPopularityAndMostRepeatedLineQty(cur, conn)
    scores = []
    quantities = []
    for item in values:
        scores.append(item[0])
        quantities.append(item[1])
    x = np.array(scores)
    y = np.array(quantities)
    r = np.corrcoef(x,y)
    r_value = r[0,1]
    return(f"\nWe found that there does not seem to be a strong correlation between a Beatles song's popularity and how repetitive that Beatles song is, which aligns with the data shown above since there are not any noticeable patterns.\nThe correlation coefficient, or r value, between a Beatles song from our database's popularity and the number of times that song's most repetitive lyric was sung is {r_value}.\nThis value is not big enough to signify any notable correlation.")

"""Writes data to txt file"""
def writeToFile(cur, conn, filename):
    f = open(filename, 'w')
    f.write(getSongNamesAndPopularity(cur,conn))
    avg_unique_lines = getAverageUniqueLinesMaster(cur, conn)
    f.write(f"\nFrom the 100 songs in our database with lyrics found in the API, the average number of unique lines per song is {avg_unique_lines}.\n")
    f.write("\nThe following shows how much the number of unique lines in the 7 selected songs (2 most popular, 3 medium popular, and 2 least popular) differs from the average from all of the others.\n")
    f.write(getAverageSongDifference(cur,conn))
    f.write(getCorrelationCoefficient(cur, conn))
    f.close()

def main():
    cur, conn = createDatabase("BeatlesMusic.db")
    writeToFile(cur, conn, "BeatlesAnalysis.txt")

if __name__ == "__main__":
    main()

