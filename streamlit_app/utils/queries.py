"""Optimized BigQuery queries for Streamlit dashboard."""

import pandas as pd
import streamlit as st

from config.settings import settings
from src.bigquery.client import BigQueryClient


@st.cache_resource
def get_bigquery_client():
    """Get cached BigQuery client instance."""
    return BigQueryClient()


def get_project_and_dataset():
    """Get project and dataset IDs."""
    return settings.bigquery.project_id, settings.bigquery.dataset_id


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_user_stats():
    """Get user statistics."""
    client = get_bigquery_client()
    project_id, dataset_id = get_project_and_dataset()
    query = f"""
    SELECT 
        display_name,
        followers,
        country,
        product
    FROM `{project_id}.{dataset_id}.users`
    LIMIT 1
    """
    return client.query(query).to_dataframe()


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_playlist_count():
    """Get total number of playlists."""
    client = get_bigquery_client()
    project_id, dataset_id = get_project_and_dataset()
    query = f"""
    SELECT COUNT(*) as count
    FROM `{project_id}.{dataset_id}.playlists`
    """
    result = client.query(query)
    return next(result).count


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_track_count():
    """Get total number of tracks."""
    client = get_bigquery_client()
    project_id, dataset_id = get_project_and_dataset()
    query = f"""
    SELECT COUNT(DISTINCT track_id) as count
    FROM `{project_id}.{dataset_id}.tracks`
    """
    result = client.query(query)
    return next(result).count


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_artist_count():
    """Get total number of artists."""
    client = get_bigquery_client()
    project_id, dataset_id = get_project_and_dataset()
    query = f"""
    SELECT COUNT(DISTINCT artist_id) as count
    FROM `{project_id}.{dataset_id}.artists`
    """
    result = client.query(query)
    return next(result).count


@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_top_tracks_by_popularity(limit: int = 20):
    """Get top tracks by popularity."""
    client = get_bigquery_client()
    project_id, dataset_id = get_project_and_dataset()
    query = f"""
    SELECT 
        name,
        popularity,
        duration_ms,
        explicit
    FROM `{project_id}.{dataset_id}.tracks`
    ORDER BY popularity DESC
    LIMIT {limit}
    """
    return client.query(query).to_dataframe()


@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_top_artists_by_followers(limit: int = 20):
    """Get top artists by followers."""
    client = get_bigquery_client()
    project_id, dataset_id = get_project_and_dataset()
    query = f"""
    SELECT 
        name,
        followers,
        popularity,
        ARRAY_LENGTH(genres) as genre_count
    FROM `{project_id}.{dataset_id}.artists`
    ORDER BY followers DESC
    LIMIT {limit}
    """
    return client.query(query).to_dataframe()


@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_audio_features_stats():
    """Get statistics of audio features."""
    client = get_bigquery_client()
    project_id, dataset_id = get_project_and_dataset()
    query = f"""
    SELECT 
        AVG(danceability) as avg_danceability,
        AVG(energy) as avg_energy,
        AVG(valence) as avg_valence,
        AVG(acousticness) as avg_acousticness,
        AVG(tempo) as avg_tempo
    FROM `{project_id}.{dataset_id}.track_audio_features`
    WHERE danceability IS NOT NULL
    """
    result = client.query(query).to_dataframe()
    # Return empty dataframe with correct columns if no data
    if result.empty:
        return pd.DataFrame({
            'avg_danceability': [0.0],
            'avg_energy': [0.0],
            'avg_valence': [0.0],
            'avg_acousticness': [0.0],
            'avg_tempo': [0.0]
        })
    return result


@st.cache_data(ttl=300)  # Cache for 5 minutes (recent data changes frequently)
def get_recently_played_tracks(limit: int = 50):
    """Get recently played tracks."""
    client = get_bigquery_client()
    project_id, dataset_id = get_project_and_dataset()
    try:
        query = f"""
        SELECT 
            t.name as track_name,
            rp.played_at,
            rp.context_type
        FROM `{project_id}.{dataset_id}.recently_played` rp
        JOIN `{project_id}.{dataset_id}.tracks` t
        ON rp.track_id = t.track_id
        ORDER BY rp.played_at DESC
        LIMIT {limit}
        """
        result = client.query(query).to_dataframe()
        # Ensure we always return a DataFrame, even if empty
        if result is None:
            return pd.DataFrame(columns=['track_name', 'played_at', 'context_type'])
        return result
    except Exception:
        # Return empty DataFrame with correct columns on error
        return pd.DataFrame(columns=['track_name', 'played_at', 'context_type'])


def get_recently_played(limit: int = 50):
    """Alias for get_recently_played_tracks for compatibility."""
    return get_recently_played_tracks(limit)


@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_top_tracks_by_time_range(time_range: str = "medium_term"):
    """Get top tracks for a specific time range."""
    client = get_bigquery_client()
    project_id, dataset_id = get_project_and_dataset()
    query = f"""
    SELECT 
        t.name as track_name,
        t.popularity,
        tt.position
    FROM `{project_id}.{dataset_id}.top_tracks` tt
    JOIN `{project_id}.{dataset_id}.tracks` t
    ON tt.track_id = t.track_id
    WHERE tt.time_range = '{time_range}'
    ORDER BY tt.position ASC
    LIMIT 20
    """
    return client.query(query).to_dataframe()


@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_top_artists_by_time_range(time_range: str = "medium_term"):
    """Get top artists for a specific time range."""
    client = get_bigquery_client()
    project_id, dataset_id = get_project_and_dataset()
    query = f"""
    SELECT 
        a.name as artist_name,
        a.followers,
        a.popularity,
        ta.position
    FROM `{project_id}.{dataset_id}.top_artists` ta
    JOIN `{project_id}.{dataset_id}.artists` a
    ON ta.artist_id = a.artist_id
    WHERE ta.time_range = '{time_range}'
    ORDER BY ta.position ASC
    LIMIT 20
    """
    return client.query(query).to_dataframe()


@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_genre_distribution(limit: int = 20):
    """Get genre distribution."""
    client = get_bigquery_client()
    project_id, dataset_id = get_project_and_dataset()
    query = f"""
    SELECT 
        genre,
        COUNT(*) as count
    FROM `{project_id}.{dataset_id}.artists`,
    UNNEST(genres) as genre
    GROUP BY genre
    ORDER BY count DESC
    LIMIT {limit}
    """
    return client.query(query).to_dataframe()


@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_tracks_by_audio_feature(feature: str, limit: int = 20):
    """Get tracks sorted by audio feature."""
    client = get_bigquery_client()
    project_id, dataset_id = get_project_and_dataset()
    # Validate feature name to prevent SQL injection
    valid_features = ['danceability', 'energy', 'valence', 'acousticness', 'tempo', 
                     'instrumentalness', 'liveness', 'speechiness', 'loudness']
    if feature not in valid_features:
        feature = 'danceability'
    
    query = f"""
    SELECT 
        t.name as track_name,
        af.{feature}
    FROM `{project_id}.{dataset_id}.track_audio_features` af
    JOIN `{project_id}.{dataset_id}.tracks` t
    ON af.track_id = t.track_id
    WHERE af.{feature} IS NOT NULL
    ORDER BY af.{feature} DESC
    LIMIT {limit}
    """
    return client.query(query).to_dataframe()


@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_trends_over_time(days: int = 30):
    """Get trends in recently played tracks over time."""
    client = get_bigquery_client()
    project_id, dataset_id = get_project_and_dataset()
    query = f"""
    SELECT 
        DATE(rp.played_at) as date,
        COUNT(DISTINCT rp.track_id) as unique_tracks,
        COUNT(*) as total_plays
    FROM `{project_id}.{dataset_id}.recently_played` rp
    WHERE rp.played_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
    GROUP BY date
    ORDER BY date DESC
    """
    return client.query(query).to_dataframe()


# Mantener compatibilidad con código existente usando una clase wrapper
class BigQueryQueries:
    """Wrapper class for backward compatibility."""
    
    def __init__(self):
        """Initialize queries wrapper."""
        pass
    
    def get_user_stats(self):
        """Get user statistics."""
        return get_user_stats()
    
    def get_playlist_count(self):
        """Get total number of playlists."""
        return get_playlist_count()
    
    def get_track_count(self):
        """Get total number of tracks."""
        return get_track_count()
    
    def get_artist_count(self):
        """Get total number of artists."""
        return get_artist_count()
    
    def get_top_tracks_by_popularity(self, limit: int = 20):
        """Get top tracks by popularity."""
        return get_top_tracks_by_popularity(limit)
    
    def get_top_artists_by_followers(self, limit: int = 20):
        """Get top artists by followers."""
        return get_top_artists_by_followers(limit)
    
    def get_audio_features_stats(self):
        """Get statistics of audio features."""
        return get_audio_features_stats()
    
    def get_recently_played_tracks(self, limit: int = 50):
        """Get recently played tracks."""
        return get_recently_played_tracks(limit)
    
    def get_recently_played(self, limit: int = 50):
        """Alias for get_recently_played_tracks for compatibility."""
        return get_recently_played(limit)
    
    def get_top_tracks_by_time_range(self, time_range: str = "medium_term"):
        """Get top tracks for a specific time range."""
        return get_top_tracks_by_time_range(time_range)
    
    def get_top_artists_by_time_range(self, time_range: str = "medium_term"):
        """Get top artists for a specific time range."""
        return get_top_artists_by_time_range(time_range)
    
    def get_genre_distribution(self, limit: int = 20):
        """Get genre distribution."""
        return get_genre_distribution(limit)
    
    def get_tracks_by_audio_feature(self, feature: str, limit: int = 20):
        """Get tracks sorted by audio feature."""
        return get_tracks_by_audio_feature(feature, limit)
    
    def get_trends_over_time(self, days: int = 30):
        """Get trends in recently played tracks over time."""
        return get_trends_over_time(days)
