"""BigQuery table schemas definitions."""

from google.cloud.bigquery import SchemaField


# Users table schema
USERS_SCHEMA = [
    SchemaField("user_id", "STRING", mode="REQUIRED", description="Spotify user ID"),
    SchemaField("display_name", "STRING", mode="NULLABLE", description="User display name"),
    SchemaField("followers", "INTEGER", mode="NULLABLE", description="Number of followers"),
    SchemaField("country", "STRING", mode="NULLABLE", description="User country"),
    SchemaField("product", "STRING", mode="NULLABLE", description="Subscription type"),
    SchemaField("extracted_at", "TIMESTAMP", mode="REQUIRED", description="Extraction timestamp"),
]

# Playlists table schema
PLAYLISTS_SCHEMA = [
    SchemaField("playlist_id", "STRING", mode="REQUIRED", description="Spotify playlist ID"),
    SchemaField("name", "STRING", mode="NULLABLE", description="Playlist name"),
    SchemaField("description", "STRING", mode="NULLABLE", description="Playlist description"),
    SchemaField("owner_id", "STRING", mode="NULLABLE", description="Playlist owner ID"),
    SchemaField("public", "BOOLEAN", mode="NULLABLE", description="Is playlist public"),
    SchemaField("collaborative", "BOOLEAN", mode="NULLABLE", description="Is playlist collaborative"),
    SchemaField("followers_count", "INTEGER", mode="NULLABLE", description="Number of followers"),
    SchemaField("tracks_count", "INTEGER", mode="NULLABLE", description="Number of tracks"),
    SchemaField("extracted_at", "TIMESTAMP", mode="REQUIRED", description="Extraction timestamp"),
]

# Tracks table schema
TRACKS_SCHEMA = [
    SchemaField("track_id", "STRING", mode="REQUIRED", description="Spotify track ID"),
    SchemaField("name", "STRING", mode="NULLABLE", description="Track name"),
    SchemaField("artists", "STRING", mode="REPEATED", description="Artist IDs"),
    SchemaField("album_id", "STRING", mode="NULLABLE", description="Album ID"),
    SchemaField("album_name", "STRING", mode="NULLABLE", description="Album name"),
    SchemaField("release_date", "DATE", mode="NULLABLE", description="Release date"),
    SchemaField("duration_ms", "INTEGER", mode="NULLABLE", description="Duration in milliseconds"),
    SchemaField("popularity", "INTEGER", mode="NULLABLE", description="Track popularity (0-100)"),
    SchemaField("explicit", "BOOLEAN", mode="NULLABLE", description="Is track explicit"),
    SchemaField("external_urls", "STRING", mode="NULLABLE", description="Spotify URL"),
    SchemaField("extracted_at", "TIMESTAMP", mode="REQUIRED", description="Extraction timestamp"),
]

# Track audio features schema
TRACK_AUDIO_FEATURES_SCHEMA = [
    SchemaField("track_id", "STRING", mode="REQUIRED", description="Spotify track ID"),
    SchemaField("danceability", "FLOAT", mode="NULLABLE", description="Danceability (0.0-1.0)"),
    SchemaField("energy", "FLOAT", mode="NULLABLE", description="Energy (0.0-1.0)"),
    SchemaField("key", "INTEGER", mode="NULLABLE", description="Musical key (0-11)"),
    SchemaField("loudness", "FLOAT", mode="NULLABLE", description="Loudness in dB"),
    SchemaField("mode", "INTEGER", mode="NULLABLE", description="Mode (0=minor, 1=major)"),
    SchemaField("speechiness", "FLOAT", mode="NULLABLE", description="Speechiness (0.0-1.0)"),
    SchemaField("acousticness", "FLOAT", mode="NULLABLE", description="Acousticness (0.0-1.0)"),
    SchemaField("instrumentalness", "FLOAT", mode="NULLABLE", description="Instrumentalness (0.0-1.0)"),
    SchemaField("liveness", "FLOAT", mode="NULLABLE", description="Liveness (0.0-1.0)"),
    SchemaField("valence", "FLOAT", mode="NULLABLE", description="Valence/positivity (0.0-1.0)"),
    SchemaField("tempo", "FLOAT", mode="NULLABLE", description="Tempo in BPM"),
    SchemaField("time_signature", "INTEGER", mode="NULLABLE", description="Time signature"),
    SchemaField("extracted_at", "TIMESTAMP", mode="REQUIRED", description="Extraction timestamp"),
]

# Artists table schema
ARTISTS_SCHEMA = [
    SchemaField("artist_id", "STRING", mode="REQUIRED", description="Spotify artist ID"),
    SchemaField("name", "STRING", mode="NULLABLE", description="Artist name"),
    SchemaField("genres", "STRING", mode="REPEATED", description="Artist genres"),
    SchemaField("popularity", "INTEGER", mode="NULLABLE", description="Artist popularity (0-100)"),
    SchemaField("followers", "INTEGER", mode="NULLABLE", description="Number of followers"),
    SchemaField("external_urls", "STRING", mode="NULLABLE", description="Spotify URL"),
    SchemaField("extracted_at", "TIMESTAMP", mode="REQUIRED", description="Extraction timestamp"),
]

# Playlist tracks junction table
PLAYLIST_TRACKS_SCHEMA = [
    SchemaField("playlist_id", "STRING", mode="REQUIRED", description="Playlist ID"),
    SchemaField("track_id", "STRING", mode="REQUIRED", description="Track ID"),
    SchemaField("added_at", "TIMESTAMP", mode="NULLABLE", description="When track was added"),
    SchemaField("added_by", "STRING", mode="NULLABLE", description="User who added the track"),
    SchemaField("position", "INTEGER", mode="NULLABLE", description="Position in playlist"),
    SchemaField("extracted_at", "TIMESTAMP", mode="REQUIRED", description="Extraction timestamp"),
]

# Recently played tracks schema
RECENTLY_PLAYED_SCHEMA = [
    SchemaField("track_id", "STRING", mode="REQUIRED", description="Track ID"),
    SchemaField("played_at", "TIMESTAMP", mode="REQUIRED", description="When track was played"),
    SchemaField("context_type", "STRING", mode="NULLABLE", description="Context type (playlist, album, etc.)"),
    SchemaField("context_uri", "STRING", mode="NULLABLE", description="Context URI"),
    SchemaField("extracted_at", "TIMESTAMP", mode="REQUIRED", description="Extraction timestamp"),
]

# Top tracks schema
TOP_TRACKS_SCHEMA = [
    SchemaField("track_id", "STRING", mode="REQUIRED", description="Track ID"),
    SchemaField("time_range", "STRING", mode="REQUIRED", description="Time range (short_term, medium_term, long_term)"),
    SchemaField("position", "INTEGER", mode="REQUIRED", description="Position in ranking"),
    SchemaField("extracted_at", "TIMESTAMP", mode="REQUIRED", description="Extraction timestamp"),
]

# Top artists schema
TOP_ARTISTS_SCHEMA = [
    SchemaField("artist_id", "STRING", mode="REQUIRED", description="Artist ID"),
    SchemaField("time_range", "STRING", mode="REQUIRED", description="Time range (short_term, medium_term, long_term)"),
    SchemaField("position", "INTEGER", mode="REQUIRED", description="Position in ranking"),
    SchemaField("extracted_at", "TIMESTAMP", mode="REQUIRED", description="Extraction timestamp"),
]

# Table schemas mapping
TABLE_SCHEMAS = {
    "users": USERS_SCHEMA,
    "playlists": PLAYLISTS_SCHEMA,
    "tracks": TRACKS_SCHEMA,
    "track_audio_features": TRACK_AUDIO_FEATURES_SCHEMA,
    "artists": ARTISTS_SCHEMA,
    "playlist_tracks": PLAYLIST_TRACKS_SCHEMA,
    "recently_played": RECENTLY_PLAYED_SCHEMA,
    "top_tracks": TOP_TRACKS_SCHEMA,
    "top_artists": TOP_ARTISTS_SCHEMA,
}

# Partitioning configuration (only for time-series tables)
PARTITIONED_TABLES = {
    "recently_played": "played_at",
    "top_tracks": "extracted_at",
    "top_artists": "extracted_at",
}

