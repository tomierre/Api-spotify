"""Tests for data transformers."""

import pytest
from datetime import datetime

from src.spotify.transformers import DataTransformer


@pytest.fixture
def transformer():
    """Create transformer instance."""
    return DataTransformer()


def test_transform_user(transformer):
    """Test user data transformation."""
    raw_user = {
        "id": "user123",
        "display_name": "Test User",
        "followers": {"total": 100},
        "country": "US",
        "product": "premium",
    }

    result = transformer.transform_user(raw_user)

    assert result["user_id"] == "user123"
    assert result["display_name"] == "Test User"
    assert result["followers"] == 100
    assert result["country"] == "US"
    assert result["product"] == "premium"
    assert "extracted_at" in result


def test_transform_playlist(transformer):
    """Test playlist data transformation."""
    raw_playlist = {
        "id": "playlist123",
        "name": "My Playlist",
        "description": "Test description",
        "owner": {"id": "owner123"},
        "public": True,
        "collaborative": False,
        "followers": {"total": 50},
        "tracks": {"total": 25},
    }

    result = transformer.transform_playlist(raw_playlist)

    assert result["playlist_id"] == "playlist123"
    assert result["name"] == "My Playlist"
    assert result["owner_id"] == "owner123"
    assert result["public"] is True
    assert result["followers_count"] == 50
    assert result["tracks_count"] == 25
    assert "extracted_at" in result


def test_transform_track(transformer):
    """Test track data transformation."""
    raw_track = {
        "id": "track123",
        "name": "Test Track",
        "artists": [{"id": "artist1", "name": "Artist 1"}],
        "album": {
            "id": "album123",
            "name": "Test Album",
            "release_date": "2024-01-01",
        },
        "duration_ms": 180000,
        "popularity": 80,
        "explicit": False,
        "external_urls": {"spotify": "https://open.spotify.com/track/track123"},
    }

    result = transformer.transform_track(raw_track)

    assert result["track_id"] == "track123"
    assert result["name"] == "Test Track"
    assert len(result["artists"]) == 1
    assert result["artists"][0] == "artist1"
    assert result["album_id"] == "album123"
    assert result["duration_ms"] == 180000
    assert result["popularity"] == 80
    assert "extracted_at" in result


def test_transform_audio_features(transformer):
    """Test audio features transformation."""
    raw_features = {
        "id": "track123",
        "danceability": 0.8,
        "energy": 0.7,
        "key": 5,
        "loudness": -5.5,
        "mode": 1,
        "speechiness": 0.1,
        "acousticness": 0.2,
        "instrumentalness": 0.3,
        "liveness": 0.4,
        "valence": 0.6,
        "tempo": 120.0,
        "time_signature": 4,
    }

    result = transformer.transform_audio_features(raw_features)

    assert result["track_id"] == "track123"
    assert result["danceability"] == 0.8
    assert result["energy"] == 0.7
    assert result["key"] == 5
    assert result["tempo"] == 120.0
    assert "extracted_at" in result


def test_transform_artist(transformer):
    """Test artist data transformation."""
    raw_artist = {
        "id": "artist123",
        "name": "Test Artist",
        "genres": ["pop", "rock"],
        "popularity": 85,
        "followers": {"total": 5000},
        "external_urls": {"spotify": "https://open.spotify.com/artist/artist123"},
    }

    result = transformer.transform_artist(raw_artist)

    assert result["artist_id"] == "artist123"
    assert result["name"] == "Test Artist"
    assert len(result["genres"]) == 2
    assert "pop" in result["genres"]
    assert result["popularity"] == 85
    assert result["followers"] == 5000
    assert "extracted_at" in result


def test_transform_all(transformer):
    """Test transformation of all data types."""
    raw_data = {
        "users": [
            {
                "id": "user123",
                "display_name": "Test User",
                "followers": {"total": 100},
            }
        ],
        "playlists": [
            {
                "id": "playlist123",
                "name": "My Playlist",
                "owner": {"id": "owner123"},
            }
        ],
        "tracks": [
            {
                "id": "track123",
                "name": "Test Track",
                "artists": [{"id": "artist1"}],
            }
        ],
        "track_audio_features": [
            {"id": "track123", "danceability": 0.8, "energy": 0.7}
        ],
        "artists": [
            {
                "id": "artist123",
                "name": "Test Artist",
                "genres": ["pop"],
            }
        ],
        "playlist_tracks": [
            {
                "playlist_id": "playlist123",
                "track_id": "track123",
                "added_at": "2024-01-01T00:00:00Z",
            }
        ],
        "recently_played": [
            {
                "track": {"id": "track123"},
                "played_at": "2024-01-01T00:00:00Z",
            }
        ],
        "top_tracks": [
            {
                "track_id": "track123",
                "time_range": "medium_term",
                "position": 1,
            }
        ],
        "top_artists": [
            {
                "artist_id": "artist123",
                "time_range": "medium_term",
                "position": 1,
            }
        ],
    }

    result = transformer.transform_all(raw_data)

    assert "users" in result
    assert "playlists" in result
    assert "tracks" in result
    assert "artists" in result
    assert "track_audio_features" in result
    assert "playlist_tracks" in result
    assert "recently_played" in result
    assert "top_tracks" in result
    assert "top_artists" in result

