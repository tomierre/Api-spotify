"""Tests for BigQuery loader."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.bigquery.loader import BigQueryLoader


@pytest.fixture
def mock_bigquery_client():
    """Create a mock BigQuery client."""
    client = Mock()
    client.project = "test-project"
    client.dataset.return_value = Mock()
    return client


@pytest.fixture
def loader(mock_bigquery_client):
    """Create loader with mocked client."""
    with patch("src.bigquery.loader.BigQueryClient") as mock_client_class:
        mock_client_class.return_value = mock_bigquery_client
        loader = BigQueryLoader()
        loader.client = mock_bigquery_client
        return loader


def test_load_users(loader, mock_bigquery_client):
    """Test loading users to BigQuery."""
    users = [
        {
            "user_id": "user123",
            "display_name": "Test User",
            "followers": 100,
            "extracted_at": "2024-01-01T00:00:00Z",
        }
    ]

    # Mock table and load job
    mock_table = Mock()
    mock_bigquery_client.get_table.return_value = mock_table
    mock_job = Mock()
    mock_job.result.return_value = None
    mock_bigquery_client.load_table_from_json.return_value = mock_job

    loader.load_users(users)

    # Verify load was called
    assert mock_bigquery_client.load_table_from_json.called


def test_load_playlists(loader, mock_bigquery_client):
    """Test loading playlists to BigQuery."""
    playlists = [
        {
            "playlist_id": "playlist123",
            "name": "My Playlist",
            "extracted_at": "2024-01-01T00:00:00Z",
        }
    ]

    mock_table = Mock()
    mock_bigquery_client.get_table.return_value = mock_table
    mock_job = Mock()
    mock_job.result.return_value = None
    mock_bigquery_client.load_table_from_json.return_value = mock_job

    loader.load_playlists(playlists)

    assert mock_bigquery_client.load_table_from_json.called


def test_load_tracks(loader, mock_bigquery_client):
    """Test loading tracks to BigQuery."""
    tracks = [
        {
            "track_id": "track123",
            "name": "Test Track",
            "extracted_at": "2024-01-01T00:00:00Z",
        }
    ]

    mock_table = Mock()
    mock_bigquery_client.get_table.return_value = mock_table
    mock_job = Mock()
    mock_job.result.return_value = None
    mock_bigquery_client.load_table_from_json.return_value = mock_job

    loader.load_tracks(tracks)

    assert mock_bigquery_client.load_table_from_json.called


def test_load_audio_features(loader, mock_bigquery_client):
    """Test loading audio features to BigQuery."""
    features = [
        {
            "track_id": "track123",
            "danceability": 0.8,
            "energy": 0.7,
            "extracted_at": "2024-01-01T00:00:00Z",
        }
    ]

    mock_table = Mock()
    mock_bigquery_client.get_table.return_value = mock_table
    mock_job = Mock()
    mock_job.result.return_value = None
    mock_bigquery_client.load_table_from_json.return_value = mock_job

    loader.load_audio_features(features)

    assert mock_bigquery_client.load_table_from_json.called


def test_load_artists(loader, mock_bigquery_client):
    """Test loading artists to BigQuery."""
    artists = [
        {
            "artist_id": "artist123",
            "name": "Test Artist",
            "extracted_at": "2024-01-01T00:00:00Z",
        }
    ]

    mock_table = Mock()
    mock_bigquery_client.get_table.return_value = mock_table
    mock_job = Mock()
    mock_job.result.return_value = None
    mock_bigquery_client.load_table_from_json.return_value = mock_job

    loader.load_artists(artists)

    assert mock_bigquery_client.load_table_from_json.called


def test_load_playlist_tracks(loader, mock_bigquery_client):
    """Test loading playlist tracks to BigQuery."""
    playlist_tracks = [
        {
            "playlist_id": "playlist123",
            "track_id": "track123",
            "extracted_at": "2024-01-01T00:00:00Z",
        }
    ]

    mock_table = Mock()
    mock_bigquery_client.get_table.return_value = mock_table
    mock_job = Mock()
    mock_job.result.return_value = None
    mock_bigquery_client.load_table_from_json.return_value = mock_job

    loader.load_playlist_tracks(playlist_tracks)

    assert mock_bigquery_client.load_table_from_json.called


def test_load_recently_played(loader, mock_bigquery_client):
    """Test loading recently played to BigQuery."""
    recently_played = [
        {
            "track_id": "track123",
            "played_at": "2024-01-01T00:00:00Z",
            "extracted_at": "2024-01-01T00:00:00Z",
        }
    ]

    mock_table = Mock()
    mock_bigquery_client.get_table.return_value = mock_table
    mock_job = Mock()
    mock_job.result.return_value = None
    mock_bigquery_client.load_table_from_json.return_value = mock_job

    loader.load_recently_played(recently_played)

    assert mock_bigquery_client.load_table_from_json.called


def test_load_top_tracks(loader, mock_bigquery_client):
    """Test loading top tracks to BigQuery."""
    top_tracks = [
        {
            "track_id": "track123",
            "time_range": "medium_term",
            "position": 1,
            "extracted_at": "2024-01-01T00:00:00Z",
        }
    ]

    mock_table = Mock()
    mock_bigquery_client.get_table.return_value = mock_table
    mock_job = Mock()
    mock_job.result.return_value = None
    mock_bigquery_client.load_table_from_json.return_value = mock_job

    loader.load_top_tracks(top_tracks)

    assert mock_bigquery_client.load_table_from_json.called


def test_load_top_artists(loader, mock_bigquery_client):
    """Test loading top artists to BigQuery."""
    top_artists = [
        {
            "artist_id": "artist123",
            "time_range": "medium_term",
            "position": 1,
            "extracted_at": "2024-01-01T00:00:00Z",
        }
    ]

    mock_table = Mock()
    mock_bigquery_client.get_table.return_value = mock_table
    mock_job = Mock()
    mock_job.result.return_value = None
    mock_bigquery_client.load_table_from_json.return_value = mock_job

    loader.load_top_artists(top_artists)

    assert mock_bigquery_client.load_table_from_json.called


def test_load_all(loader):
    """Test loading all data types."""
    data = {
        "users": [{"user_id": "user123", "extracted_at": "2024-01-01T00:00:00Z"}],
        "playlists": [
            {"playlist_id": "playlist123", "extracted_at": "2024-01-01T00:00:00Z"}
        ],
        "tracks": [{"track_id": "track123", "extracted_at": "2024-01-01T00:00:00Z"}],
        "artists": [
            {"artist_id": "artist123", "extracted_at": "2024-01-01T00:00:00Z"}
        ],
        "track_audio_features": [
            {"track_id": "track123", "extracted_at": "2024-01-01T00:00:00Z"}
        ],
        "playlist_tracks": [
            {
                "playlist_id": "playlist123",
                "track_id": "track123",
                "extracted_at": "2024-01-01T00:00:00Z",
            }
        ],
        "recently_played": [
            {
                "track_id": "track123",
                "played_at": "2024-01-01T00:00:00Z",
                "extracted_at": "2024-01-01T00:00:00Z",
            }
        ],
        "top_tracks": [
            {
                "track_id": "track123",
                "time_range": "medium_term",
                "position": 1,
                "extracted_at": "2024-01-01T00:00:00Z",
            }
        ],
        "top_artists": [
            {
                "artist_id": "artist123",
                "time_range": "medium_term",
                "position": 1,
                "extracted_at": "2024-01-01T00:00:00Z",
            }
        ],
    }

    # Should not raise any exceptions
    loader.load_all(data)

