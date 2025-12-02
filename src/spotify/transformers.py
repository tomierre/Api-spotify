"""Data transformation and validation with Pydantic."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from src.utils.logger import logger


class UserModel(BaseModel):
    """User data model."""

    user_id: str
    display_name: Optional[str] = None
    followers: Optional[int] = 0
    country: Optional[str] = None
    product: Optional[str] = None
    extracted_at: str

    @field_validator("extracted_at")
    @classmethod
    def validate_extracted_at(cls, v: str) -> str:
        """Ensure extracted_at is a valid ISO timestamp."""
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("extracted_at must be a valid ISO timestamp")
        return v


class PlaylistModel(BaseModel):
    """Playlist data model."""

    playlist_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    owner_id: Optional[str] = None
    public: Optional[bool] = False
    collaborative: Optional[bool] = False
    followers_count: Optional[int] = 0
    tracks_count: Optional[int] = 0
    extracted_at: str


class TrackModel(BaseModel):
    """Track data model."""

    track_id: str
    name: Optional[str] = None
    artists: List[str] = Field(default_factory=list)
    album_id: Optional[str] = None
    album_name: Optional[str] = None
    release_date: Optional[str] = None
    duration_ms: Optional[int] = None
    popularity: Optional[int] = Field(None, ge=0, le=100)
    explicit: Optional[bool] = False
    external_urls: Optional[str] = None
    extracted_at: str

    @field_validator("release_date")
    @classmethod
    def validate_release_date(cls, v: Optional[str]) -> Optional[str]:
        """Validate release date format."""
        if v is None:
            return v
        # Spotify dates can be YYYY, YYYY-MM, or YYYY-MM-DD
        parts = v.split("-")
        if len(parts) == 1:
            # Just year, add default month and day
            return f"{v}-01-01"
        elif len(parts) == 2:
            # Year and month, add default day
            return f"{v}-01"
        return v


class TrackAudioFeaturesModel(BaseModel):
    """Track audio features model."""

    track_id: str
    danceability: Optional[float] = Field(None, ge=0.0, le=1.0)
    energy: Optional[float] = Field(None, ge=0.0, le=1.0)
    key: Optional[int] = Field(None, ge=-1, le=11)
    loudness: Optional[float] = None
    mode: Optional[int] = Field(None, ge=0, le=1)
    speechiness: Optional[float] = Field(None, ge=0.0, le=1.0)
    acousticness: Optional[float] = Field(None, ge=0.0, le=1.0)
    instrumentalness: Optional[float] = Field(None, ge=0.0, le=1.0)
    liveness: Optional[float] = Field(None, ge=0.0, le=1.0)
    valence: Optional[float] = Field(None, ge=0.0, le=1.0)
    tempo: Optional[float] = Field(None, ge=0.0)
    time_signature: Optional[int] = Field(None, ge=3, le=7)
    extracted_at: str


class ArtistModel(BaseModel):
    """Artist data model."""

    artist_id: str
    name: Optional[str] = None
    genres: List[str] = Field(default_factory=list)
    popularity: Optional[int] = Field(None, ge=0, le=100)
    followers: Optional[int] = 0
    external_urls: Optional[str] = None
    extracted_at: str


class PlaylistTrackModel(BaseModel):
    """Playlist track junction model."""

    playlist_id: str
    track_id: str
    added_at: Optional[str] = None
    added_by: Optional[str] = None
    position: Optional[int] = None
    extracted_at: str


class RecentlyPlayedModel(BaseModel):
    """Recently played track model."""

    track_id: str
    played_at: str
    context_type: Optional[str] = None
    context_uri: Optional[str] = None
    extracted_at: str


class TopTrackModel(BaseModel):
    """Top track model."""

    track_id: str
    time_range: str = Field(..., pattern="^(short_term|medium_term|long_term)$")
    position: int = Field(..., ge=1)
    extracted_at: str


class TopArtistModel(BaseModel):
    """Top artist model."""

    artist_id: str
    time_range: str = Field(..., pattern="^(short_term|medium_term|long_term)$")
    position: int = Field(..., ge=1)
    extracted_at: str


class DataTransformer:
    """Transform and validate extracted data."""

    @staticmethod
    def transform_users(data: List[dict]) -> List[dict]:
        """
        Transform and validate user data.

        Args:
            data: List of user dictionaries

        Returns:
            List of validated user dictionaries
        """
        validated = []
        for item in data:
            try:
                user = UserModel(**item)
                validated.append(user.model_dump())
            except Exception as e:
                logger.warning(f"Failed to validate user data: {e}")
        return validated

    @staticmethod
    def transform_playlists(data: List[dict]) -> List[dict]:
        """
        Transform and validate playlist data.

        Args:
            data: List of playlist dictionaries

        Returns:
            List of validated playlist dictionaries
        """
        validated = []
        for item in data:
            try:
                playlist = PlaylistModel(**item)
                validated.append(playlist.model_dump())
            except Exception as e:
                logger.warning(f"Failed to validate playlist data: {e}")
        return validated

    @staticmethod
    def transform_tracks(data: List[dict]) -> List[dict]:
        """
        Transform and validate track data.

        Args:
            data: List of track dictionaries

        Returns:
            List of validated track dictionaries
        """
        validated = []
        for item in data:
            try:
                track = TrackModel(**item)
                validated.append(track.model_dump())
            except Exception as e:
                logger.warning(f"Failed to validate track data: {e}")
        return validated

    @staticmethod
    def transform_audio_features(data: List[dict]) -> List[dict]:
        """
        Transform and validate audio features data.

        Args:
            data: List of audio features dictionaries

        Returns:
            List of validated audio features dictionaries
        """
        validated = []
        for item in data:
            try:
                features = TrackAudioFeaturesModel(**item)
                validated.append(features.model_dump())
            except Exception as e:
                logger.warning(f"Failed to validate audio features data: {e}")
        return validated

    @staticmethod
    def transform_artists(data: List[dict]) -> List[dict]:
        """
        Transform and validate artist data.

        Args:
            data: List of artist dictionaries

        Returns:
            List of validated artist dictionaries
        """
        validated = []
        for item in data:
            try:
                artist = ArtistModel(**item)
                validated.append(artist.model_dump())
            except Exception as e:
                logger.warning(f"Failed to validate artist data: {e}")
        return validated

    @staticmethod
    def transform_playlist_tracks(data: List[dict]) -> List[dict]:
        """
        Transform and validate playlist tracks data.

        Args:
            data: List of playlist track dictionaries

        Returns:
            List of validated playlist track dictionaries
        """
        validated = []
        for item in data:
            try:
                pt = PlaylistTrackModel(**item)
                validated.append(pt.model_dump())
            except Exception as e:
                logger.warning(f"Failed to validate playlist track data: {e}")
        return validated

    @staticmethod
    def transform_recently_played(data: List[dict]) -> List[dict]:
        """
        Transform and validate recently played data.

        Args:
            data: List of recently played dictionaries

        Returns:
            List of validated recently played dictionaries
        """
        validated = []
        for item in data:
            try:
                rp = RecentlyPlayedModel(**item)
                validated.append(rp.model_dump())
            except Exception as e:
                logger.warning(f"Failed to validate recently played data: {e}")
        return validated

    @staticmethod
    def transform_top_tracks(data: List[dict]) -> List[dict]:
        """
        Transform and validate top tracks data.

        Args:
            data: List of top track dictionaries

        Returns:
            List of validated top track dictionaries
        """
        validated = []
        for item in data:
            try:
                tt = TopTrackModel(**item)
                validated.append(tt.model_dump())
            except Exception as e:
                logger.warning(f"Failed to validate top track data: {e}")
        return validated

    @staticmethod
    def transform_top_artists(data: List[dict]) -> List[dict]:
        """
        Transform and validate top artists data.

        Args:
            data: List of top artist dictionaries

        Returns:
            List of validated top artist dictionaries
        """
        validated = []
        for item in data:
            try:
                ta = TopArtistModel(**item)
                validated.append(ta.model_dump())
            except Exception as e:
                logger.warning(f"Failed to validate top artist data: {e}")
        return validated

    @staticmethod
    def transform_all(data: dict) -> dict:
        """
        Transform and validate all extracted data.

        Args:
            data: Dictionary containing all extracted data

        Returns:
            Dictionary containing all validated data
        """
        logger.info("Transforming and validating all data...")

        return {
            "users": DataTransformer.transform_users(data.get("users", [])),
            "playlists": DataTransformer.transform_playlists(data.get("playlists", [])),
            "tracks": DataTransformer.transform_tracks(data.get("tracks", [])),
            "track_audio_features": DataTransformer.transform_audio_features(
                data.get("track_audio_features", [])
            ),
            "artists": DataTransformer.transform_artists(data.get("artists", [])),
            "playlist_tracks": DataTransformer.transform_playlist_tracks(
                data.get("playlist_tracks", [])
            ),
            "recently_played": DataTransformer.transform_recently_played(
                data.get("recently_played", [])
            ),
            "top_tracks": DataTransformer.transform_top_tracks(data.get("top_tracks", [])),
            "top_artists": DataTransformer.transform_top_artists(data.get("top_artists", [])),
        }

