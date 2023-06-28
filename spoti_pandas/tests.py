# from spoti_pandas import sp_functions as sppd
import spoti_pandas.sp_functions as sppd

pl_link = '"https://open.spotify.com/playlist/7eWWLoTfmLUcD0viBP6Hr0?si=e8b0760749404749"'

# Test get playlist tracks
pl_tracks = sppd.get_pl_tracks(pl_link)
print(f"{len(pl_tracks)} tracks found")

# Test playlist track details
# pl_tracks_df = sppd.pl_track_features(pl_link)
# print(f"{len(pl_tracks_df)} tracks found")

# Test get albums
artist_uri = '2pXFmyqPm7wHJ1HGAwyR3L' #HCTM
artist_albums = sppd.get_artist_albums(artist_uri)
print(f"{len(artist_albums)} albums found.")

# Test get tracks from album
album_uri = artist_albums.iloc[0]['id']
album_link = artist_albums.iloc[0]['href']
album_tracks = sppd.get_album_tracks(album_uri)
print(f"{len(album_tracks)} tracks")

# Test get album track features
album_tracks_df = sppd.album_track_features(album_link)
print(f"{len(album_tracks_df)} tracks found")

# Test all tracks for artist
artist_tracks_df = sppd.get_artist_track_features(artist_uri)