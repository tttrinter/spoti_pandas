# Spotify API functions - calls to the API to collect track features

# IMPORTS
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd

# Spotify Credentials
import spot_creds
clid = spot_creds.client_id
secret = spot_creds.secret

#Authentication - without user
client_credentials_manager = SpotifyClientCredentials(client_id=clid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

def get_URI(list_link):
    """Extracts URI from playlist or album link"""
    uri = list_link.split("/")[-1].split("?")[0]
    return uri


def get_pl_tracks(playlist_link):
    """Get the list of tracks from a Spotify playlist.

    Args:
        playlist_link: string, web-link
    Returns:
        list of track uris
    """
    pl_uri = get_URI(playlist_link)
    tracks = sp.playlist_items(pl_uri)["items"]
    return tracks


def get_album_tracks(album_link):
    """Get the list of tracks from an album

    Args:
        album_link: string, web-link
    Returns:
        list of track uris
    """
    tracks = sp.album_tracks(album_link)["items"]
    return tracks

def extract_track_feat(track_uri, audio_feat = False):
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
    if audio_feat==True:
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

    NOTE: this should be reusable for an album, however, the JSON tags are not in the same place
    so I'm making separate functions to simplify the extraction

    Input: playlist_link - URI for a Spotify playlist
    Returns: pandas dataframe with tracklisting and audio features
    """

    # initialize dataframe for results
    tracks_df = pd.DataFrame()

    playlist_URI = get_URI(playlist_link)

    # Loop over tracks to gather info
    for track in sp.playlist_items(playlist_URI)["items"]:
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


def album_track_features(album_link):
    """
    Calls the Spotify API to collect track listings for an album.
    Pulls meta data and track data for each track and returns a dataframe with all of the features

    NOTE: this should be reusable for an playlist, however, the JSON tags are not in the same place
    so I'm making separate functions to simplify the extraction

    Input: album_link - URI for a Spotify album
    Returns: pandas dataframe with tracklisting and audio features
    """

    # initialize dataframe for results
    tracks_df = pd.DataFrame()

    album_uri = get_URI(album_link)

    # Loop over tracks to gather info
    for track in sp.album_tracks(album_uri)["items"]:
        this_track = {}
        # URI
        track_uri = track["uri"]
        this_track['track_uri'] = track_uri

        # Track name
        this_track['track_name'] = track["name"]

        # Main Artist
        artist_uri = track["artists"][0]["uri"]
        this_track['artist_uri'] = artist_uri
        artist_info = sp.artist(artist_uri)

        # Name, popularity, genre
        this_track['artist_name'] =artist_info["name"]
        this_track['artist_pop'] = artist_info["popularity"]
        this_track['artist_genres'] = artist_info["genres"]

        # Album
        album_info = sp.album(album_uri)
        this_track['album'] = album_info["name"]

        # Track Metadata
        this_track['track_pop'] = -1 # not in album info
        this_track['explicit'] = track['explicit']

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


def get_artist_albums(artist_uri):
    """
    Calls the Spotify API to collect all albums for an artist
    Input: artist_uri - URI for a Spotify artist
    Returns: pandas dataframe with a list of albums
    """
    albums = sp.artist_albums(artist_uri)

    # data columns to keep
    album_cols = ['name',
                  'album_type',
                  'href',
                  'id',
                  'release_date',
                  'total_tracks']

    albums_df = pd.json_normalize(albums["items"])[album_cols]
    return(albums_df)


def get_artist_track_features(artist_uri):
    """
    Calls the Spotify API to collect all albums for an artist
    then cycle through all albums to get each track's details
    Input:
        artist_uri - URI for a Spotify artist
        analysis: boolean, if True, then pull Spotify analysis data for each track
    Returns: pandas dataframe with a list of tracks
    """

    albums = get_artist_albums(artist_uri)[['name','id']]

    # initialize dataframe for results
    tracks_df = pd.DataFrame()

    for album_id in albums['id']:
        album_tracks = album_track_features(album_id)
        tracks_df = pd.concat([tracks_df, album_tracks])

    return tracks_df


def related_artists(artist_uri):
    # calls spotify.artist_related_artists and returns the top 20
    # related artists and basic metadata in a dataframe
    related = sp.artist_related_artists(artist_uri)
    related_df = pd.json_normalize(related)
    return related_df


