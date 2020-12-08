import os
import plotly.graph_objects as go
from lyrics import createDatabase
from data_calculation import getUniqueLinesLyrics, getPopularityAndMostRepeatedLineQty

""" creates a line graph for popularity vs. max times a lyric repeats per song for each beatles song"""
def lineVisualization(cur, conn):
    popularity = []
    max_repeats = []
    songs = sorted(getPopularityAndMostRepeatedLineQty(cur, conn))
    for song in songs:
        popularity.append(song[0])
        max_repeats.append(song[1])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x = popularity,
        y = max_repeats
    ))

    fig.update_layout(
        title = "Popularity vs. Max Times a Lyric Repeats per Song for Beatles Songs",
        xaxis_title = "Popularity (Spotify Popularity Score)",
        yaxis_title = "Max Times a Lyric Repeats per Song",
    ) 

    fig.show()

""" creates a bar graph for the number of unique lyrics for selected Beatles songs based on popularity category"""
def barVisualization(cur, conn):
    dic = getUniqueLinesLyrics(cur, conn)
    song = tuple(dic.keys())
    unique = tuple(dic.values())

    fig = go.Figure(data = [
        go.Bar(name = "Low", x = song[5:], y = unique[5:]),
        go.Bar(name = "Medium", x = song[2:5], y = unique[2:5]),
        go.Bar(name = "High", x = song[:2], y = unique[:2])]
    )

    fig.update_layout(
        title = "Number of Unique Lyrics for Beatles Songs Based on Category",
        xaxis_title="Song Title",
        yaxis_title="Quantity of Unique Lyrics",
        legend_title="Popularity",
        barmode="group",
    )

    fig.show()

def main():
    cur, conn = createDatabase("BeatlesMusic.db")
    lineVisualization(cur, conn)
    barVisualization(cur, conn)

if __name__ == "__main__":
    main()