# Spotify API functions - calls to the API to collect track features

# IMPORTS
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import time

# Spotify Credentials
import spot_creds
clid = spot_creds.client_id
secret = spot_creds.secret

# Authentication - without user
client_credentials_manager = SpotifyClientCredentials(client_id=clid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def get_uri(list_link):
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
    pl_uri = get_uri(playlist_link)
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


def extract_track_feat(track_uri, audio_feat=False):
    """Using the Spotify API, gathers metadata and selected audio features for the given track

    Keyword Arguments:
    track_uri -- string, Spotify's uri for the track

    Returns:
    pandas dataframe with all the metadata and audio features for the track
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
    if audio_feat:
        this_track = extract_audio_feat(track_uri, this_track)

    this_track_df = pd.json_normalize(this_track)

    return this_track_df


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

    for feat in audio_feat_list:
        track_dict[feat] = audio_feat[feat]

    return track_dict


def get_audio_analysis(track_uri):
    """Extracts selected audio analysis from the Spotify audio_features function

    Keyword Arguments:
    track_uri -- string, Spotify's uri for the track

    Returns:
    dictionary with the audio_analysis features for the track, excluding:
    codestring, echoprintstring, synchstring, and rhythmstring
    """

    audio_anal = sp.audio_analysis(track_uri)

    # delete the long track strings - until I figure out how to use them
    del audio_anal['track']['codestring']
    del audio_anal['track']['echoprintstring']
    del audio_anal['track']['synchstring']
    del audio_anal['track']['rhythmstring']

    return audio_anal


def pl_track_features(playlist_link):
    """
    Calls the Spotify API to collect track listings for each playlist.
    Pulls metadata and track data for each track and returns a dataframe with the features

    NOTE: this should be reusable for an album, however, the JSON tags are not in the same place.
    I'm making separate functions to simplify the extraction

    Input: playlist_link - URI for a Spotify playlist
    Returns: pandas dataframe with tracklisting and audio features
    """

    # initialize dataframe for results
    tracks_df = pd.DataFrame()
    # artists_df = pd.DataFrame()

    playlist_uri = get_uri(playlist_link)

    # Loop over tracks to gather info
    track_count = 1
    for track in sp.playlist_items(playlist_uri)["items"]:
        # if track_count % 25 == 0:
        #     print("Sleeping for 60 seconds to avoid rate limit")
        #     time.sleep(60)

        this_track = {}
        # URI
        track_uri = track["track"]["uri"]
        this_track['track_uri'] = track_uri

        # Track name
        this_track['track_name'] = track["track"]["name"]

        # Main Artist
        artist_id = track["track"]["artists"][0]["id"]
        artist_name = track["track"]["artists"][0]["name"]
        this_track['artist_id'] = artist_id
        this_track['artist_name'] = artist_name

        # Add artist info to the artist-bank to minimize API calls and avoid rate limits
        # artists_df = artist_bank(artist_id, artists_df)

        # Name, popularity, genre
        this_track['artist_name'] = track["track"]["artists"][0]["name"]

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
        track_count += 1

    # Merge with Artist data
    # tracks_df = tracks_df.merge(artists_df, how='left', on='artist_id')

    # Make sure there are no duplicates
    tracks_df = tracks_df.drop_duplicates('track_uri')

    return tracks_df


def album_track_features(album_link):
    """
    Calls the Spotify API to collect track listings for an album.
    Pulls metadata and track data for each track and returns a dataframe with the features

    NOTE: this should be reusable for a playlist, however, the JSON tags are not in the same place.
    I'm making separate functions to simplify the extraction

    Input: album_link - URI for a Spotify album
    Returns: pandas dataframe with tracklisting and audio features
    """

    # initialize dataframe for results
    tracks_df = pd.DataFrame()
    # artists_df = pd.DataFrame()

    album_uri = get_uri(album_link)

    # Loop over tracks to gather info
    track_count = 1
    for track in sp.album_tracks(album_uri)["items"]:
        if track_count % 25 == 0:
            print("Sleeping for 60 seconds to avoid rate limit")
            time.sleep(60)

        this_track = {}
        # URI
        track_uri = track["uri"]
        this_track['track_uri'] = track_uri

        # Track name
        this_track['track_name'] = track["name"]

        # Main Artist
        artist_id = track["artists"][0]["id"]
        artist_name = track["artists"][0]["name"]
        this_track['artist_id'] = artist_id
        this_track['artist_name'] = artist_name

        # Add artist info to the artist-bank to minimize API calls and avoid rate limits
        # artists_df = artist_bank(artist_id, artists_df)

        # Album
        album_info = sp.album(album_uri)
        this_track['album'] = album_info["name"]

        # Track Metadata
        this_track['track_pop'] = -1  # not in album info
        this_track['explicit'] = track['explicit']

        # Audio Features
        try:
            this_track = extract_audio_feat(track_uri, this_track)
        except:
            pass

        # Convert to DataFrame
        this_track_df = pd.json_normalize(this_track)

        tracks_df = pd.concat([tracks_df, this_track_df], ignore_index=True)
        track_count += 1

    # Merge with Artist data
    # tracks_df = tracks_df.merge(artists_df, how='left', on='artist_id')

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
    return albums_df


def get_artist_track_features(artist_uri):
    """
    Calls the Spotify API to collect all albums for an artist
    then cycle through all albums to get each track's details
    Input:
        artist_uri - URI for a Spotify artist
        analysis: boolean, if True, then pull Spotify analysis data for each track
    Returns: pandas dataframe with a list of tracks
    """

    albums = get_artist_albums(artist_uri)[['name', 'id']]

    # initialize dataframe for results
    tracks_df = pd.DataFrame()

    for i in range(len(albums)):
        album_id = albums.iloc[i]['id']
        album_name = albums.iloc[i]['name']
        print(f'Getting tracks for {album_name}')

        try:
            album_tracks = album_track_features(album_id)
            time.sleep(60)
            tracks_df = pd.concat([tracks_df, album_tracks])
        except:
            pass

    return tracks_df


def related_artists(artist_uri):
    # calls spotify.artist_related_artists and returns the top 20
    # related artists and basic metadata in a dataframe
    related = sp.artist_related_artists(artist_uri)
    related_df = pd.json_normalize(related['artists'])
    return related_df


def artist_bank(artist_id, artist_df=None):
    # Maintains a cumulative list of artist info to avoid repeated API calls
    # Input:
    #     artist_id - id for a Spotify artist
    #     artist_df: pandas DataFrame containing the cumulative list of artist details

    # Returns: artist_df appended with the new artist details, if not already present
    if artist_df is None:
        artist_df = pd.DataFrame()

    if 'artist_id' in artist_df.columns:
        if artist_id in artist_df.artist_id:
            return artist_df
    else:
        this_artist = sp.artist(artist_id)
        this_artist_df = pd.json_normalize(this_artist)
        this_artist_df = this_artist_df[['genres', 'id', 'name', 'popularity', 'uri', 'followers.total']]
        this_artist_df.columns = ['artist_genres', 'artist_id', 'aritst_name', 'artist_pop', 'artist_uri',
                                  'artist_followers_total']

        # combine with running list
        artist_df = pd.concat([artist_df, this_artist_df])

    return artist_df
