# spoti_pandas
**A wrapper for the Spotify Api and spotipy that gathers mulitple tracks, playlists, etc... and returns data in pandas dataframe format.**

The Spotify API and Spotipy libraries return most of the data in JSON format. This package collects mulitple tracks by user, artist, etc... and returns dataframe(s) with the data on those tracks.

Here are some of the functions intended for this library:

## Playlist
* get_playlist_tracks - given a playlist URI, pull all of the tracks, track meta-data and analysis data and return in a dataframe

## User
* get_playlists - for a given user, pull all playlists
* get_pl_tracks - pulls all tracks for all playlists
* get_liked_tracks - pull all liked tracks

## Artist
* get_artist_tracks - pull the list of tracks for an artist - optional include metadata and analysis data
* get_artist_albums - pulls a list of albums and album metadata

## Album
* get_album_tracks - pull all tracks for an album and append all of the metadata and analysis data

## Genre
* If possible, pull all tracks within a genre
