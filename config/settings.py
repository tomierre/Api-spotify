"""Configuration settings for the Spotify ETL pipeline."""

import os
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class SpotifySettings(BaseSettings):
    """Spotify API configuration."""

    client_id: str = Field(..., alias="SPOTIFY_CLIENT_ID")
    client_secret: str = Field(..., alias="SPOTIFY_CLIENT_SECRET")
    redirect_uri: str = Field(
        default="http://localhost:8888/callback", alias="SPOTIFY_REDIRECT_URI"
    )
    scope: str = Field(
        default="user-read-recently-played,user-top-read,user-library-read,playlist-read-private",
        alias="SPOTIFY_SCOPE",
    )

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


class BigQuerySettings(BaseSettings):
    """BigQuery configuration."""

    project_id: str = Field(..., alias="BIGQUERY_PROJECT_ID")
    dataset_id: str = Field(default="spotify_data", alias="BIGQUERY_DATASET_ID")
    credentials_path: str = Field(..., alias="GOOGLE_APPLICATION_CREDENTIALS")

    @field_validator("credentials_path")
    @classmethod
    def validate_credentials_path(cls, v: str) -> str:
        """Validate that credentials file exists."""
        if not os.path.exists(v):
            raise ValueError(f"Credentials file not found: {v}")
        return v

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


class ExtractionLimits(BaseSettings):
    """Limits for data extraction to optimize costs."""

    max_playlists: int = Field(default=20, alias="MAX_PLAYLISTS")
    max_tracks_per_playlist: int = Field(default=100, alias="MAX_TRACKS_PER_PLAYLIST")
    max_recently_played: int = Field(default=50, alias="MAX_RECENTLY_PLAYED")
    top_items_limit: int = Field(default=20, alias="TOP_ITEMS_LIMIT")
    max_audio_features_batch: int = Field(
        default=100, alias="MAX_AUDIO_FEATURES_BATCH"
    )

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


class AppSettings(BaseSettings):
    """Application configuration."""

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", alias="LOG_LEVEL"
    )
    environment: Literal["development", "production", "testing"] = Field(
        default="development", alias="ENVIRONMENT"
    )

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


class Settings:
    """Main settings class that aggregates all configuration."""

    def __init__(self):
        """Initialize all settings."""
        self.spotify = SpotifySettings()
        self.bigquery = BigQuerySettings()
        self.limits = ExtractionLimits()
        self.app = AppSettings()

    @property
    def extraction_limits(self) -> dict:
        """Get extraction limits as dictionary."""
        return {
            "max_playlists": self.limits.max_playlists,
            "max_tracks_per_playlist": self.limits.max_tracks_per_playlist,
            "max_recently_played": self.limits.max_recently_played,
            "top_items_limit": self.limits.top_items_limit,
            "max_audio_features_batch": self.limits.max_audio_features_batch,
        }


# Global settings instance
settings = Settings()

