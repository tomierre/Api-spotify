# Spotify API Guide

This guide explains how to use the Spotify Web API endpoints in this project.

## Authentication

The project uses OAuth2 authentication with the following flow:

1. User authorizes the application
2. Receive authorization code
3. Exchange code for access token
4. Use access token for API requests
5. Refresh token when expired

### Required Scopes

- `user-read-recently-played`: Read recently played tracks
- `user-top-read`: Read user's top tracks and artists
- `user-library-read`: Read user's saved tracks and albums
- `playlist-read-private`: Read user's private playlists

## Endpoints Used

### User Profile

**Endpoint**: `GET /v1/me`

**Usage**: Get current user's profile information

**Response Fields**:
- `id`: User ID
- `display_name`: Display name
- `followers`: Followers count
- `country`: Country code
- `product`: Subscription type (free/premium)

### User Playlists

**Endpoint**: `GET /v1/users/{user_id}/playlists`

**Usage**: Get user's playlists

**Pagination**: Supports `limit` and `offset` parameters

**Response Fields**:
- `id`: Playlist ID
- `name`: Playlist name
- `description`: Playlist description
- `owner`: Owner information
- `public`: Public/private status
- `collaborative`: Collaborative status
- `followers`: Followers count
- `tracks`: Tracks information

### Playlist Tracks

**Endpoint**: `GET /v1/playlists/{playlist_id}/tracks`

**Usage**: Get tracks from a playlist

**Pagination**: Supports `limit` and `offset` parameters

**Response Fields**:
- `track`: Track object
- `added_at`: When track was added
- `added_by`: User who added the track

### Track Audio Features

**Endpoint**: `GET /v1/audio-features`

**Usage**: Get audio features for multiple tracks

**Limits**: Maximum 100 track IDs per request

**Response Fields**:
- `danceability`: 0.0-1.0
- `energy`: 0.0-1.0
- `key`: 0-11 (musical key)
- `loudness`: dB value
- `mode`: 0 (minor) or 1 (major)
- `speechiness`: 0.0-1.0
- `acousticness`: 0.0-1.0
- `instrumentalness`: 0.0-1.0
- `liveness`: 0.0-1.0
- `valence`: 0.0-1.0 (positivity)
- `tempo`: BPM
- `time_signature`: 3-7

### Artist Information

**Endpoint**: `GET /v1/artists`

**Usage**: Get information for multiple artists

**Limits**: Maximum 50 artist IDs per request

**Response Fields**:
- `id`: Artist ID
- `name`: Artist name
- `genres`: List of genres
- `popularity`: 0-100
- `followers`: Followers count
- `external_urls`: Spotify URLs

### Recently Played Tracks

**Endpoint**: `GET /v1/me/player/recently-played`

**Usage**: Get recently played tracks

**Limits**: Maximum 50 tracks per request

**Response Fields**:
- `track`: Track object
- `played_at`: Timestamp when played
- `context`: Playback context

### Top Tracks

**Endpoint**: `GET /v1/me/top/tracks`

**Usage**: Get user's top tracks

**Parameters**:
- `time_range`: `short_term` (4 weeks), `medium_term` (6 months), `long_term` (all time)
- `limit`: Maximum 50

**Response Fields**:
- `id`: Track ID
- `name`: Track name
- `artists`: Artist information
- `popularity`: Popularity score
- `album`: Album information

### Top Artists

**Endpoint**: `GET /v1/me/top/artists`

**Usage**: Get user's top artists

**Parameters**:
- `time_range`: `short_term`, `medium_term`, `long_term`
- `limit`: Maximum 50

**Response Fields**:
- `id`: Artist ID
- `name`: Artist name
- `genres`: Genres
- `popularity`: Popularity score
- `followers`: Followers count

## Rate Limiting

Spotify API has rate limits:

- **30 requests per second** per application
- Rate limit headers in responses:
  - `X-RateLimit-Limit`: Requests allowed
  - `X-RateLimit-Remaining`: Requests remaining
  - `Retry-After`: Seconds to wait if rate limited

The client automatically handles rate limiting with exponential backoff.

## Error Handling

### Common Error Codes

- `400 Bad Request`: Invalid parameters
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource doesn't exist
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Spotify server error

### Error Response Format

```json
{
  "error": {
    "status": 401,
    "message": "Invalid access token"
  }
}
```

## Best Practices

1. **Cache Tokens**: Store tokens securely and refresh before expiration
2. **Handle Pagination**: Always check for `next` field in paginated responses
3. **Batch Requests**: Use batch endpoints when available (audio features, artists)
4. **Respect Rate Limits**: Implement exponential backoff
5. **Error Handling**: Handle all error cases gracefully
6. **Data Validation**: Validate all API responses before processing

## Data Extraction Limits

To optimize costs and stay within free tier, the project implements limits:

- **Playlists**: Maximum 20 playlists
- **Tracks per Playlist**: Maximum 100 tracks
- **Recently Played**: Last 50 tracks
- **Top Items**: Top 20 tracks/artists per time range
- **Audio Features**: Batched in groups of 100

These limits can be adjusted in `.env` file.

## References

- [Spotify Web API Documentation](https://developer.spotify.com/documentation/web-api)
- [Spotify Web API Reference](https://developer.spotify.com/documentation/web-api/reference)
- [Authorization Guide](https://developer.spotify.com/documentation/general/guides/authorization)

