"""Data validators using Pydantic models."""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class UserValidator(BaseModel):
    """Validator for user data."""

    user_id: str
    display_name: Optional[str] = None
    followers: Optional[int] = None
    country: Optional[str] = None
    product: Optional[str] = None

    @field_validator("followers")
    @classmethod
    def validate_followers(cls, v: Optional[int]) -> Optional[int]:
        """Validate followers is non-negative."""
        if v is not None and v < 0:
            raise ValueError("Followers must be non-negative")
        return v


class PlaylistValidator(BaseModel):
    """Validator for playlist data."""

    playlist_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    owner_id: Optional[str] = None
    public: Optional[bool] = None
    collaborative: Optional[bool] = None
    followers_count: Optional[int] = None
    tracks_count: Optional[int] = None

    @field_validator("followers_count", "tracks_count")
    @classmethod
    def validate_counts(cls, v: Optional[int]) -> Optional[int]:
        """Validate counts are non-negative."""
        if v is not None and v < 0:
            raise ValueError("Counts must be non-negative")
        return v


class TrackValidator(BaseModel):
    """Validator for track data."""

    track_id: str
    name: Optional[str] = None
    artists: List[str] = Field(default_factory=list)
    album_id: Optional[str] = None
    album_name: Optional[str] = None
    release_date: Optional[str] = None
    duration_ms: Optional[int] = None
    popularity: Optional[int] = Field(None, ge=0, le=100)
    explicit: Optional[bool] = None
    external_urls: Optional[str] = None

    @field_validator("duration_ms")
    @classmethod
    def validate_duration(cls, v: Optional[int]) -> Optional[int]:
        """Validate duration is positive."""
        if v is not None and v <= 0:
            raise ValueError("Duration must be positive")
        return v


class AudioFeaturesValidator(BaseModel):
    """Validator for audio features data."""

    track_id: str
    danceability: Optional[float] = Field(None, ge=0.0, le=1.0)
    energy: Optional[float] = Field(None, ge=0.0, le=1.0)
    key: Optional[int] = Field(None, ge=0, le=11)
    loudness: Optional[float] = None
    mode: Optional[int] = Field(None, ge=0, le=1)
    speechiness: Optional[float] = Field(None, ge=0.0, le=1.0)
    acousticness: Optional[float] = Field(None, ge=0.0, le=1.0)
    instrumentalness: Optional[float] = Field(None, ge=0.0, le=1.0)
    liveness: Optional[float] = Field(None, ge=0.0, le=1.0)
    valence: Optional[float] = Field(None, ge=0.0, le=1.0)
    tempo: Optional[float] = Field(None, gt=0.0)
    time_signature: Optional[int] = Field(None, ge=3, le=7)


class ArtistValidator(BaseModel):
    """Validator for artist data."""

    artist_id: str
    name: Optional[str] = None
    genres: List[str] = Field(default_factory=list)
    popularity: Optional[int] = Field(None, ge=0, le=100)
    followers: Optional[int] = None
    external_urls: Optional[str] = None

    @field_validator("followers")
    @classmethod
    def validate_followers(cls, v: Optional[int]) -> Optional[int]:
        """Validate followers is non-negative."""
        if v is not None and v < 0:
            raise ValueError("Followers must be non-negative")
        return v

