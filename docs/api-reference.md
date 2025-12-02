# API Reference

Complete API documentation for the Spotify ETL Pipeline.

## Configuration

### Settings (`config/settings.py`)

Centralized configuration management using Pydantic.

#### `Settings`

Main settings class that aggregates all configuration.

**Attributes**:
- `spotify`: SpotifySettings
- `bigquery`: BigQuerySettings
- `limits`: ExtractionLimits
- `app`: AppSettings

**Properties**:
- `extraction_limits`: Returns extraction limits as dictionary

## Spotify Module

### SpotifyClient (`src/spotify/client.py`)

Client for interacting with Spotify Web API.

#### Methods

##### `get_current_user() -> dict`

Get current user profile.

**Returns**: User profile information

##### `get_user_playlists(user_id: str, limit: int = 50) -> list`

Get user playlists with pagination.

**Parameters**:
- `user_id`: Spotify user ID
- `limit`: Maximum number of playlists per page

**Returns**: List of playlists

##### `get_playlist_tracks(playlist_id: str, limit: int = 100) -> list`

Get tracks from a playlist with pagination.

**Parameters**:
- `playlist_id`: Spotify playlist ID
- `limit`: Maximum number of tracks per page

**Returns**: List of tracks

##### `get_track_audio_features(track_ids: list) -> list`

Get audio features for multiple tracks.

**Parameters**:
- `track_ids`: List of track IDs (max 100 per request)

**Returns**: List of audio features

##### `get_artist(artist_id: str) -> dict`

Get artist information.

**Parameters**:
- `artist_id`: Spotify artist ID

**Returns**: Artist information

##### `get_artists(artist_ids: list) -> list`

Get multiple artists information.

**Parameters**:
- `artist_ids`: List of artist IDs (max 50 per request)

**Returns**: List of artist information

##### `get_recently_played(limit: int = 50) -> list`

Get recently played tracks.

**Parameters**:
- `limit`: Maximum number of tracks (max 50)

**Returns**: List of recently played tracks

##### `get_top_tracks(time_range: str = "medium_term", limit: int = 20) -> list`

Get user's top tracks.

**Parameters**:
- `time_range`: Time range (short_term, medium_term, long_term)
- `limit`: Maximum number of tracks (max 50)

**Returns**: List of top tracks

##### `get_top_artists(time_range: str = "medium_term", limit: int = 20) -> list`

Get user's top artists.

**Parameters**:
- `time_range`: Time range (short_term, medium_term, long_term)
- `limit`: Maximum number of artists (max 50)

**Returns**: List of top artists

### SpotifyExtractor (`src/spotify/extractor.py`)

Extract data from Spotify API with limits applied.

#### Methods

##### `extract_user_profile() -> dict`

Extract current user profile.

**Returns**: User profile data

##### `extract_playlists(user_id: str) -> List[dict]`

Extract user playlists (limited by MAX_PLAYLISTS).

**Parameters**:
- `user_id`: Spotify user ID

**Returns**: List of playlists

##### `extract_playlist_tracks(playlist_id: str) -> List[dict]`

Extract tracks from a playlist (limited by MAX_TRACKS_PER_PLAYLIST).

**Parameters**:
- `playlist_id`: Playlist ID

**Returns**: List of playlist tracks

##### `extract_tracks(playlist_tracks: List[dict]) -> List[dict]`

Extract track information from playlist tracks.

**Parameters**:
- `playlist_tracks`: List of playlist track items

**Returns**: List of track data

##### `extract_audio_features(track_ids: List[str]) -> List[dict]`

Extract audio features for tracks (batched).

**Parameters**:
- `track_ids`: List of track IDs

**Returns**: List of audio features

##### `extract_artists(artist_ids: List[str]) -> List[dict]`

Extract artist information.

**Parameters**:
- `artist_ids`: List of artist IDs

**Returns**: List of artist data

##### `extract_recently_played() -> List[dict]`

Extract recently played tracks (limited by MAX_RECENTLY_PLAYED).

**Returns**: List of recently played tracks

##### `extract_top_tracks() -> List[dict]`

Extract top tracks for all time ranges (limited by TOP_ITEMS_LIMIT).

**Returns**: List of top tracks

##### `extract_top_artists() -> List[dict]`

Extract top artists for all time ranges (limited by TOP_ITEMS_LIMIT).

**Returns**: List of top artists

##### `extract_all() -> dict`

Extract all available data from Spotify API.

**Returns**: Dictionary containing all extracted data

### DataTransformer (`src/spotify/transformers.py`)

Transform and validate Spotify data.

#### Methods

##### `transform_user(user_data: dict) -> dict`

Transform user profile data.

**Parameters**:
- `user_data`: Raw user data from API

**Returns**: Transformed user data

##### `transform_playlist(playlist_data: dict) -> dict`

Transform playlist data.

**Parameters**:
- `playlist_data`: Raw playlist data from API

**Returns**: Transformed playlist data

##### `transform_track(track_data: dict) -> dict`

Transform track data.

**Parameters**:
- `track_data`: Raw track data from API

**Returns**: Transformed track data

##### `transform_audio_features(features_data: dict) -> dict`

Transform audio features data.

**Parameters**:
- `features_data`: Raw audio features from API

**Returns**: Transformed audio features

##### `transform_artist(artist_data: dict) -> dict`

Transform artist data.

**Parameters**:
- `artist_data`: Raw artist data from API

**Returns**: Transformed artist data

##### `transform_all(raw_data: dict) -> dict`

Transform all extracted data.

**Parameters**:
- `raw_data`: Dictionary with all raw extracted data

**Returns**: Dictionary with all transformed data

## BigQuery Module

### BigQueryClient (`src/bigquery/client.py`)

Client for BigQuery operations.

#### Methods

##### `ensure_dataset_exists() -> None`

Ensure the BigQuery dataset exists, create if it doesn't.

##### `create_table(table_name: str, schema: list, partitioned_by: str = None) -> None`

Create a BigQuery table with schema.

**Parameters**:
- `table_name`: Name of the table
- `schema`: List of SchemaField objects
- `partitioned_by`: Field name for partitioning (optional)

### BigQueryLoader (`src/bigquery/loader.py`)

Load data into BigQuery with upsert strategy.

#### Methods

##### `load_users(users: List[dict]) -> None`

Load user data to BigQuery.

**Parameters**:
- `users`: List of user dictionaries

##### `load_playlists(playlists: List[dict]) -> None`

Load playlist data to BigQuery.

**Parameters**:
- `playlists`: List of playlist dictionaries

##### `load_tracks(tracks: List[dict]) -> None`

Load track data to BigQuery.

**Parameters**:
- `tracks`: List of track dictionaries

##### `load_audio_features(features: List[dict]) -> None`

Load audio features to BigQuery.

**Parameters**:
- `features`: List of audio feature dictionaries

##### `load_artists(artists: List[dict]) -> None`

Load artist data to BigQuery.

**Parameters**:
- `artists`: List of artist dictionaries

##### `load_playlist_tracks(playlist_tracks: List[dict]) -> None`

Load playlist-track relationships to BigQuery.

**Parameters**:
- `playlist_tracks`: List of playlist-track relationship dictionaries

##### `load_recently_played(recently_played: List[dict]) -> None`

Load recently played tracks to BigQuery.

**Parameters**:
- `recently_played`: List of recently played track dictionaries

##### `load_top_tracks(top_tracks: List[dict]) -> None`

Load top tracks to BigQuery.

**Parameters**:
- `top_tracks`: List of top track dictionaries

##### `load_top_artists(top_artists: List[dict]) -> None`

Load top artists to BigQuery.

**Parameters**:
- `top_artists`: List of top artist dictionaries

##### `load_all(data: dict) -> None`

Load all transformed data to BigQuery.

**Parameters**:
- `data`: Dictionary with all transformed data

## Pipeline Module

### ETLPipeline (`pipelines/etl_pipeline.py`)

Main ETL pipeline orchestrator.

#### Methods

##### `run() -> dict`

Execute the complete ETL pipeline.

**Returns**: Dictionary with execution summary including:
- `status`: "success" or "error"
- `users`: Number of users loaded
- `playlists`: Number of playlists loaded
- `tracks`: Number of tracks loaded
- `artists`: Number of artists loaded
- `audio_features`: Number of audio features loaded
- `recently_played`: Number of recently played records loaded
- `top_tracks`: Number of top tracks loaded
- `top_artists`: Number of top artists loaded

## Utilities

### Logger (`src/utils/logger.py`)

Centralized logging configuration.

#### Functions

##### `setup_logger(name: str = "spotify_etl") -> logging.Logger`

Set up and configure a logger instance.

**Parameters**:
- `name`: Name of the logger

**Returns**: Configured logger instance

### Validators (`src/utils/validators.py`)

Pydantic models for data validation.

#### Models

- `UserValidator`: Validates user data
- `PlaylistValidator`: Validates playlist data
- `TrackValidator`: Validates track data
- `AudioFeaturesValidator`: Validates audio features
- `ArtistValidator`: Validates artist data
