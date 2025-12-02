# Architecture

This document describes the architecture and design of the Spotify ETL Pipeline.

## System Overview

The pipeline follows a traditional ETL (Extract, Transform, Load) architecture with the following components:

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────────┐
│  Spotify   │─────▶│   Extract    │─────▶│ Transform   │─────▶│    Load      │
│    API     │      │              │      │              │      │  BigQuery    │
└────────────┘      └──────────────┘      └─────────────┘      └──────────────┘
                                                      │
                                                      ▼
                                            ┌──────────────┐
                                            │  Streamlit   │
                                            │  Dashboard   │
                                            └──────────────┘
```

## Components

### 1. Spotify Client (`src/spotify/client.py`)

**Responsibility**: Authentication and API communication

- Handles OAuth2 authentication flow
- Manages token refresh and caching
- Implements rate limiting and retry logic
- Provides methods for all Spotify API endpoints

**Key Features**:
- Automatic token refresh
- Exponential backoff for rate limits
- Error handling and retries

### 2. Data Extractor (`src/spotify/extractor.py`)

**Responsibility**: Extract data from Spotify API

- Extracts user profile information
- Fetches playlists with pagination
- Retrieves tracks and audio features
- Gets artist information
- Fetches recently played tracks
- Retrieves top tracks and artists

**Extraction Limits** (for cost optimization):
- Maximum 20 playlists
- Maximum 100 tracks per playlist
- Last 50 recently played tracks
- Top 20 tracks/artists per time range

### 3. Data Transformer (`src/spotify/transformers.py`)

**Responsibility**: Transform and validate data

- Normalizes data from different endpoints
- Validates data using Pydantic models
- Enriches data with timestamps
- Cleans and standardizes formats

**Validation Models**:
- `UserModel` - User profile data
- `PlaylistModel` - Playlist information
- `TrackModel` - Track details
- `AudioFeaturesModel` - Audio features
- `ArtistModel` - Artist information

### 4. BigQuery Client (`src/bigquery/client.py`)

**Responsibility**: BigQuery connection and dataset management

- Manages BigQuery client connection
- Ensures dataset exists
- Creates tables with schemas
- Handles table operations

### 5. BigQuery Loader (`src/bigquery/loader.py`)

**Responsibility**: Load data into BigQuery

- Implements upsert strategy (merge)
- Handles incremental loading
- Manages batch inserts
- Deduplicates data

**Loading Strategy**:
- Upsert for existing records
- Insert for new records
- Batch processing for efficiency

### 6. ETL Pipeline (`pipelines/etl_pipeline.py`)

**Responsibility**: Orchestrate the complete ETL process

- Coordinates extraction, transformation, and loading
- Handles errors and logging
- Provides execution summary

## Data Flow

### Extraction Phase

1. Authenticate with Spotify API
2. Extract user profile
3. Extract user playlists (limited to 20)
4. For each playlist, extract tracks (limited to 100 per playlist)
5. Extract audio features for unique tracks
6. Extract artist information for unique artists
7. Extract recently played tracks (last 50)
8. Extract top tracks and artists (top 20 each)

### Transformation Phase

1. Normalize data structures
2. Validate data with Pydantic models
3. Add extraction timestamps
4. Clean and standardize formats
5. Prepare data for BigQuery schemas

### Loading Phase

1. Connect to BigQuery
2. For each table:
   - Check if records exist
   - Perform upsert (merge) operation
   - Insert new records
   - Update existing records

## Database Schema

### Tables

1. **users** - User profile information
2. **playlists** - Playlist metadata
3. **tracks** - Track information
4. **track_audio_features** - Audio analysis features
5. **artists** - Artist information
6. **playlist_tracks** - Many-to-many relationship
7. **recently_played** - Playback history (partitioned by date)
8. **top_tracks** - User's top tracks by time range (partitioned)
9. **top_artists** - User's top artists by time range (partitioned)

### Partitioning Strategy

- **recently_played**: Partitioned by `played_at` (date)
- **top_tracks**: Partitioned by `extracted_at` (date)
- **top_artists**: Partitioned by `extracted_at` (date)

This allows efficient querying of time-series data and helps with data retention policies.

## Cost Optimization

### Storage Optimization

- Use appropriate data types (STRING instead of TEXT)
- Partition only time-series tables
- Implement data retention policies (90 days for recently_played)

### Query Optimization

- Limit extraction to necessary data only
- Use incremental loading (only new/changed data)
- Implement caching in Streamlit dashboard
- Use LIMIT clauses in queries

### Free Tier Limits

- **Storage**: 10 GB/month (free)
- **Queries**: 1 TB/month (free)

The pipeline is designed to stay well within these limits.

## Error Handling

### Retry Logic

- Automatic retry with exponential backoff for rate limits
- Token refresh on authentication errors
- Maximum 3 retries for transient errors

### Logging

- Centralized logging configuration
- Different log levels (DEBUG, INFO, WARNING, ERROR)
- File logging in production environment

## Security

### Credentials Management

- Environment variables for sensitive data
- `.env` file (not committed to git)
- Service account JSON for GCP (stored securely)

### OAuth2 Flow

- Secure token storage in `.spotify_cache`
- Automatic token refresh
- No hardcoded credentials

## Scalability Considerations

### Current Design

- Single-user extraction
- Manual execution
- Suitable for personal data analysis

### Future Enhancements

- Multi-user support
- Scheduled execution (cron, Cloud Scheduler)
- Parallel processing for large datasets
- Streaming data updates

## Monitoring

### Cost Monitoring

- Script to check BigQuery usage
- Alerts for approaching free tier limits
- Monthly projections

### Pipeline Monitoring

- Detailed logging at each step
- Execution summaries
- Error tracking

## Testing Strategy

### Unit Tests

- Test each component independently
- Mock external APIs (Spotify, BigQuery)
- Validate data transformations

### Integration Tests

- End-to-end pipeline testing
- Test with test data
- Verify BigQuery schemas
