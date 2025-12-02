# Referencia de API

Documentación completa de la API del Pipeline ETL de Spotify.

## Configuración

### Settings (`config/settings.py`)

Gestión centralizada de configuración usando Pydantic.

#### `Settings`

Clase principal de configuración que agrega toda la configuración.

**Atributos**:
- `spotify`: SpotifySettings
- `bigquery`: BigQuerySettings
- `limits`: ExtractionLimits
- `app`: AppSettings

**Propiedades**:
- `extraction_limits`: Retorna los límites de extracción como diccionario

## Módulo Spotify

### SpotifyClient (`src/spotify/client.py`)

Cliente para interactuar con la API Web de Spotify.

#### Métodos

##### `get_current_user() -> dict`

Obtener el perfil del usuario actual.

**Retorna**: Información del perfil de usuario

##### `get_user_playlists(user_id: str, limit: int = 50) -> list`

Obtener playlists del usuario con paginación.

**Parámetros**:
- `user_id`: ID de usuario de Spotify
- `limit`: Número máximo de playlists por página

**Retorna**: Lista de playlists

##### `get_playlist_tracks(playlist_id: str, limit: int = 100) -> list`

Obtener tracks de una playlist con paginación.

**Parámetros**:
- `playlist_id`: ID de playlist de Spotify
- `limit`: Número máximo de tracks por página

**Retorna**: Lista de tracks

##### `get_track_audio_features(track_ids: list) -> list`

Obtener características de audio para múltiples tracks.

**Parámetros**:
- `track_ids`: Lista de IDs de tracks (máximo 100 por solicitud)

**Retorna**: Lista de características de audio

##### `get_artist(artist_id: str) -> dict`

Obtener información de un artista.

**Parámetros**:
- `artist_id`: ID de artista de Spotify

**Retorna**: Información del artista

##### `get_artists(artist_ids: list) -> list`

Obtener información de múltiples artistas.

**Parámetros**:
- `artist_ids`: Lista de IDs de artistas (máximo 50 por solicitud)

**Retorna**: Lista de información de artistas

##### `get_recently_played(limit: int = 50) -> list`

Obtener tracks reproducidos recientemente.

**Parámetros**:
- `limit`: Número máximo de tracks (máximo 50)

**Retorna**: Lista de tracks reproducidos recientemente

##### `get_top_tracks(time_range: str = "medium_term", limit: int = 20) -> list`

Obtener los tracks más escuchados del usuario.

**Parámetros**:
- `time_range`: Rango de tiempo (short_term, medium_term, long_term)
- `limit`: Número máximo de tracks (máximo 50)

**Retorna**: Lista de tracks más escuchados

##### `get_top_artists(time_range: str = "medium_term", limit: int = 20) -> list`

Obtener los artistas más escuchados del usuario.

**Parámetros**:
- `time_range`: Rango de tiempo (short_term, medium_term, long_term)
- `limit`: Número máximo de artistas (máximo 50)

**Retorna**: Lista de artistas más escuchados

### SpotifyExtractor (`src/spotify/extractor.py`)

Extraer datos de la API de Spotify con límites aplicados.

#### Métodos

##### `extract_user_profile() -> dict`

Extraer el perfil del usuario actual.

**Retorna**: Datos del perfil de usuario

##### `extract_playlists(user_id: str) -> List[dict]`

Extraer playlists del usuario (limitado por MAX_PLAYLISTS).

**Parámetros**:
- `user_id`: ID de usuario de Spotify

**Retorna**: Lista de playlists

##### `extract_playlist_tracks(playlist_id: str) -> List[dict]`

Extraer tracks de una playlist (limitado por MAX_TRACKS_PER_PLAYLIST).

**Parámetros**:
- `playlist_id`: ID de playlist

**Retorna**: Lista de tracks de playlist

##### `extract_tracks(playlist_tracks: List[dict]) -> List[dict]`

Extraer información de tracks desde tracks de playlist.

**Parámetros**:
- `playlist_tracks`: Lista de items de tracks de playlist

**Retorna**: Lista de datos de tracks

##### `extract_audio_features(track_ids: List[str]) -> List[dict]`

Extraer características de audio para tracks (por lotes).

**Parámetros**:
- `track_ids`: Lista de IDs de tracks

**Retorna**: Lista de características de audio

##### `extract_artists(artist_ids: List[str]) -> List[dict]`

Extraer información de artistas.

**Parámetros**:
- `artist_ids`: Lista de IDs de artistas

**Retorna**: Lista de datos de artistas

##### `extract_recently_played() -> List[dict]`

Extraer tracks reproducidos recientemente (limitado por MAX_RECENTLY_PLAYED).

**Retorna**: Lista de tracks reproducidos recientemente

##### `extract_top_tracks() -> List[dict]`

Extraer tracks más escuchados para todos los rangos de tiempo (limitado por TOP_ITEMS_LIMIT).

**Retorna**: Lista de tracks más escuchados

##### `extract_top_artists() -> List[dict]`

Extraer artistas más escuchados para todos los rangos de tiempo (limitado por TOP_ITEMS_LIMIT).

**Retorna**: Lista de artistas más escuchados

##### `extract_all() -> dict`

Extraer todos los datos disponibles de la API de Spotify.

**Retorna**: Diccionario que contiene todos los datos extraídos

### DataTransformer (`src/spotify/transformers.py`)

Transformar y validar datos de Spotify.

#### Métodos

##### `transform_user(user_data: dict) -> dict`

Transformar datos del perfil de usuario.

**Parámetros**:
- `user_data`: Datos brutos de usuario de la API

**Retorna**: Datos de usuario transformados

##### `transform_playlist(playlist_data: dict) -> dict`

Transformar datos de playlist.

**Parámetros**:
- `playlist_data`: Datos brutos de playlist de la API

**Retorna**: Datos de playlist transformados

##### `transform_track(track_data: dict) -> dict`

Transformar datos de track.

**Parámetros**:
- `track_data`: Datos brutos de track de la API

**Retorna**: Datos de track transformados

##### `transform_audio_features(features_data: dict) -> dict`

Transformar datos de características de audio.

**Parámetros**:
- `features_data`: Características de audio brutas de la API

**Retorna**: Características de audio transformadas

##### `transform_artist(artist_data: dict) -> dict`

Transformar datos de artista.

**Parámetros**:
- `artist_data`: Datos brutos de artista de la API

**Retorna**: Datos de artista transformados

##### `transform_all(raw_data: dict) -> dict`

Transformar todos los datos extraídos.

**Parámetros**:
- `raw_data`: Diccionario con todos los datos brutos extraídos

**Retorna**: Diccionario con todos los datos transformados

## Módulo BigQuery

### BigQueryClient (`src/bigquery/client.py`)

Cliente para operaciones de BigQuery.

#### Métodos

##### `ensure_dataset_exists() -> None`

Asegurar que el dataset de BigQuery exista, crearlo si no existe.

##### `create_table(table_name: str, schema: list, partitioned_by: str = None) -> None`

Crear una tabla de BigQuery con esquema.

**Parámetros**:
- `table_name`: Nombre de la tabla
- `schema`: Lista de objetos SchemaField
- `partitioned_by`: Nombre del campo para particionado (opcional)

### BigQueryLoader (`src/bigquery/loader.py`)

Cargar datos en BigQuery con estrategia upsert.

#### Métodos

##### `load_users(users: List[dict]) -> None`

Cargar datos de usuarios en BigQuery.

**Parámetros**:
- `users`: Lista de diccionarios de usuarios

##### `load_playlists(playlists: List[dict]) -> None`

Cargar datos de playlists en BigQuery.

**Parámetros**:
- `playlists`: Lista de diccionarios de playlists

##### `load_tracks(tracks: List[dict]) -> None`

Cargar datos de tracks en BigQuery.

**Parámetros**:
- `tracks`: Lista de diccionarios de tracks

##### `load_audio_features(features: List[dict]) -> None`

Cargar características de audio en BigQuery.

**Parámetros**:
- `features`: Lista de diccionarios de características de audio

##### `load_artists(artists: List[dict]) -> None`

Cargar datos de artistas en BigQuery.

**Parámetros**:
- `artists`: Lista de diccionarios de artistas

##### `load_playlist_tracks(playlist_tracks: List[dict]) -> None`

Cargar relaciones playlist-track en BigQuery.

**Parámetros**:
- `playlist_tracks`: Lista de diccionarios de relaciones playlist-track

##### `load_recently_played(recently_played: List[dict]) -> None`

Cargar tracks reproducidos recientemente en BigQuery.

**Parámetros**:
- `recently_played`: Lista de diccionarios de tracks reproducidos recientemente

##### `load_top_tracks(top_tracks: List[dict]) -> None`

Cargar tracks más escuchados en BigQuery.

**Parámetros**:
- `top_tracks`: Lista de diccionarios de tracks más escuchados

##### `load_top_artists(top_artists: List[dict]) -> None`

Cargar artistas más escuchados en BigQuery.

**Parámetros**:
- `top_artists`: Lista de diccionarios de artistas más escuchados

##### `load_all(data: dict) -> None`

Cargar todos los datos transformados en BigQuery.

**Parámetros**:
- `data`: Diccionario con todos los datos transformados

## Módulo Pipeline

### ETLPipeline (`pipelines/etl_pipeline.py`)

Orquestador principal del pipeline ETL.

#### Métodos

##### `run() -> dict`

Ejecutar el pipeline ETL completo.

**Retorna**: Diccionario con resumen de ejecución incluyendo:
- `status`: "success" o "error"
- `users`: Número de usuarios cargados
- `playlists`: Número de playlists cargadas
- `tracks`: Número de tracks cargados
- `artists`: Número de artistas cargados
- `audio_features`: Número de características de audio cargadas
- `recently_played`: Número de registros de reproducción reciente cargados
- `top_tracks`: Número de tracks más escuchados cargados
- `top_artists`: Número de artistas más escuchados cargados

## Utilidades

### Logger (`src/utils/logger.py`)

Configuración centralizada de logging.

#### Funciones

##### `setup_logger(name: str = "spotify_etl") -> logging.Logger`

Configurar e inicializar una instancia de logger.

**Parámetros**:
- `name`: Nombre del logger

**Retorna**: Instancia de logger configurada

### Validators (`src/utils/validators.py`)

Modelos Pydantic para validación de datos.

#### Modelos

- `UserValidator`: Valida datos de usuario
- `PlaylistValidator`: Valida datos de playlist
- `TrackValidator`: Valida datos de track
- `AudioFeaturesValidator`: Valida características de audio
- `ArtistValidator`: Valida datos de artista
