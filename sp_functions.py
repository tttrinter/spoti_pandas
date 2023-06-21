# Spotify API functions - calls to the API to collect track features

# IMPORTS
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import numpy as np

# Spotify Credentials
import spot_creds

clid = spot_creds.client_id
secret = spot_creds.secret

#Authentication - without user
client_credentials_manager = SpotifyClientCredentials(client_id=clid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)


def extract_track_feat(track_uri):
    """Using the Spotify API, gathers metadata and selected audio features for the given track

    Keyword Arguments:
    track_uri -- string, Spotify's uri for the track

    Returns:
    pandas dataframe with all of the metadata and audiofeatures for the track
    """
    this_track = {}
    # URI
    this_track['track_uri'] = track_uri

    track = sp.track(track_uri)

    # Track name
    this_track['track_name'] = track["name"]

    # Main Artist
    artist_uri = track["artists"][0]["uri"]
    this_track['artist_uri'] = artist_uri
    artist_info = sp.artist(artist_uri)

    # Name, popularity, genre
    this_track['artist_name'] = track["artists"][0]["name"]
    this_track['artist_pop'] = artist_info["popularity"]
    this_track['artist_genres'] = artist_info["genres"]

    # Album
    this_track['album'] = track["album"]["name"]

    # Track Metadata
    this_track['track_pop'] = track["popularity"]
    this_track['explicit'] = track['explicit']

    # Audio Features
    this_track = extract_audio_feat(track_uri, this_track)

    this_track_df = pd.json_normalize(this_track)

    return (this_track_df)

def extract_audio_feat(track_uri, track_dict):
    """Extracts selected audio features from the Spotify audio_features function and
    adds it to the input track_dict

    Keyword Arguments:
    track_uri -- string, Spotify's uri for the track
    track_dict -- dictionary containing the higher level metadata for the track

    Returns:
    updated dictionary for the track including the added audio features
    """
    # Audio Features
    audio_feat_list = ['acousticness',
                       'danceability',
                       'energy',
                       'instrumentalness',
                       'key',
                       'liveness',
                       'loudness',
                       'mode',
                       'speechiness',
                       'tempo',
                       'time_signature',
                       'valence']

    audio_feat = sp.audio_features(track_uri)[0]

    audio_feat_list = ['acousticness',
                       'danceability',
                       'energy',
                       'instrumentalness',
                       'key',
                       'liveness',
                       'loudness',
                       'mode',
                       'speechiness',
                       'tempo',
                       'time_signature',
                       'valence']

    for feat in audio_feat_list:
        track_dict[feat] = audio_feat[feat]

    return track_dict


def get_audio_analysis(track_uri):
    """Extracts selected audio analysis from the Spotify audio_features function

    Keyword Arguments:
    track_uri -- string, Spotify's uri for the track

    Returns:
    dictionary with all of the audio_analysis features for the track, excluding:
    codestring, echoprintstring, synchstring, and rhythmstring
    """

    audio_anal = sp.audio_analysis(track_uri)

    # delete the long track strings - until I figure out how to use them
    del audio_anal['track']['codestring']
    del audio_anal['track']['echoprintstring']
    del audio_anal['track']['synchstring']
    del audio_anal['track']['rhythmstring']

    return(audio_anal)


def pl_track_features(playlist_link):
    """
    Calls the Spotify API to collect track listings for each playlist.
    Pulls meta data and track data for each track and returns a dataframe with all of the features

    Input: playlist_link - URI for a Spotify playlist
    Returns: pandas dataframe with tracklisting and audio features
    """

    # initialize dataframe for results
    tracks_df = pd.DataFrame()

    playlist_URI = get_playlist_URI(playlist_link)

    # Loop over tracks to gather info
    for track in sp.playlist_tracks(playlist_URI)["items"]:
        this_track = {}
        # URI
        track_uri = track["track"]["uri"]
        this_track['track_uri'] = track_uri

        # Track name
        this_track['track_name'] = track["track"]["name"]

        # Main Artist
        artist_uri = track["track"]["artists"][0]["uri"]
        this_track['artist_uri'] = artist_uri
        artist_info = sp.artist(artist_uri)

        # Name, popularity, genre
        this_track['artist_name'] = track["track"]["artists"][0]["name"]
        this_track['artist_pop'] = artist_info["popularity"]
        this_track['artist_genres'] = artist_info["genres"]

        # Album
        this_track['album'] = track["track"]["album"]["name"]

        # Track Metadata
        this_track['track_pop'] = track["track"]["popularity"]
        this_track['explicit'] = track["track"]['explicit']

        # Audio Features
        try:
            this_track = extract_audio_feat(track_uri, this_track)
        except:
            pass

        # Convert to DataFrame
        this_track_df = pd.json_normalize(this_track)

        tracks_df = pd.concat([tracks_df, this_track_df], ignore_index=True)

    # Make sure there are no duplicates
    tracks_df = tracks_df.drop_duplicates('track_uri')

    return tracks_df
# Testing
# track_uri = '1kGQzSasZr4HY5CzjHqCPG'
# track_details = extract_track_feat(track_uri)
# len(track_details)
