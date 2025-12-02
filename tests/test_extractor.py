"""Tests for Spotify data extractor."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.spotify.extractor import SpotifyExtractor
from config.settings import settings


@pytest.fixture
def mock_spotify_client():
    """Create a mock Spotify client."""
    client = Mock()
    client.get_current_user.return_value = {
        "id": "test_user_id",
        "display_name": "Test User",
        "followers": {"total": 100},
        "country": "US",
        "product": "premium",
    }
    client.get_user_playlists.return_value = [
        {"id": "playlist1", "name": "Playlist 1"},
        {"id": "playlist2", "name": "Playlist 2"},
    ]
    client.get_playlist_tracks.return_value = [
        {
            "track": {
                "id": "track1",
                "name": "Track 1",
                "artists": [{"id": "artist1", "name": "Artist 1"}],
            },
            "added_at": "2024-01-01T00:00:00Z",
        }
    ]
    client.get_track_audio_features.return_value = [
        {
            "id": "track1",
            "danceability": 0.8,
            "energy": 0.7,
            "valence": 0.6,
        }
    ]
    client.get_artists.return_value = {
        "artists": [
            {
                "id": "artist1",
                "name": "Artist 1",
                "genres": ["pop"],
                "popularity": 80,
                "followers": {"total": 1000},
            }
        ]
    }
    client.get_recently_played.return_value = [
        {
            "track": {"id": "track1", "name": "Track 1"},
            "played_at": "2024-01-01T00:00:00Z",
        }
    ]
    client.get_top_tracks.return_value = {
        "items": [{"id": "track1", "name": "Top Track 1"}]
    }
    client.get_top_artists.return_value = {
        "items": [{"id": "artist1", "name": "Top Artist 1"}]
    }
    return client


@pytest.fixture
def extractor(mock_spotify_client):
    """Create extractor with mocked client."""
    with patch("src.spotify.extractor.SpotifyClient") as mock_client_class:
        mock_client_class.return_value = mock_spotify_client
        extractor = SpotifyExtractor()
        extractor.client = mock_spotify_client
        return extractor


def test_extract_user_profile(extractor, mock_spotify_client):
    """Test user profile extraction."""
    result = extractor.extract_user_profile()

    assert result["user_id"] == "test_user_id"
    assert result["display_name"] == "Test User"
    assert result["followers"] == 100
    mock_spotify_client.get_current_user.assert_called_once()


def test_extract_playlists(extractor, mock_spotify_client):
    """Test playlist extraction with limits."""
    user_id = "test_user_id"
    result = extractor.extract_playlists(user_id)

    assert len(result) <= settings.limits.max_playlists
    assert result[0]["playlist_id"] == "playlist1"
    mock_spotify_client.get_user_playlists.assert_called()


def test_extract_playlist_tracks(extractor, mock_spotify_client):
    """Test playlist tracks extraction with limits."""
    playlist_id = "playlist1"
    result = extractor.extract_playlist_tracks(playlist_id)

    assert len(result) <= settings.limits.max_tracks_per_playlist
    mock_spotify_client.get_playlist_tracks.assert_called()


def test_extract_tracks(extractor):
    """Test track extraction from playlist tracks."""
    playlist_tracks = [
        {
            "track": {
                "id": "track1",
                "name": "Track 1",
                "artists": [{"id": "artist1", "name": "Artist 1"}],
                "album": {"id": "album1", "name": "Album 1"},
            }
        }
    ]

    result = extractor.extract_tracks(playlist_tracks)

    assert len(result) > 0
    assert result[0]["track_id"] == "track1"


def test_extract_audio_features(extractor, mock_spotify_client):
    """Test audio features extraction."""
    track_ids = ["track1", "track2"]
    result = extractor.extract_audio_features(track_ids)

    assert len(result) > 0
    mock_spotify_client.get_track_audio_features.assert_called()


def test_extract_artists(extractor, mock_spotify_client):
    """Test artist extraction."""
    artist_ids = ["artist1", "artist2"]
    result = extractor.extract_artists(artist_ids)

    assert len(result) > 0
    mock_spotify_client.get_artists.assert_called()


def test_extract_recently_played(extractor, mock_spotify_client):
    """Test recently played extraction with limits."""
    result = extractor.extract_recently_played()

    assert len(result) <= settings.limits.max_recently_played
    mock_spotify_client.get_recently_played.assert_called()


def test_extract_top_tracks(extractor, mock_spotify_client):
    """Test top tracks extraction with limits."""
    result = extractor.extract_top_tracks()

    # Should have tracks for all time ranges
    assert len(result) > 0
    assert all(
        item["position"] <= settings.limits.top_items_limit for item in result
    )
    mock_spotify_client.get_top_tracks.assert_called()


def test_extract_top_artists(extractor, mock_spotify_client):
    """Test top artists extraction with limits."""
    result = extractor.extract_top_artists()

    # Should have artists for all time ranges
    assert len(result) > 0
    assert all(
        item["position"] <= settings.limits.top_items_limit for item in result
    )
    mock_spotify_client.get_top_artists.assert_called()


def test_extract_all(extractor):
    """Test complete extraction."""
    result = extractor.extract_all()

    assert "users" in result
    assert "playlists" in result
    assert "tracks" in result
    assert "artists" in result
    assert "track_audio_features" in result
    assert "recently_played" in result
    assert "top_tracks" in result
    assert "top_artists" in result

