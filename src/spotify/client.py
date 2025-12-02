"""Spotify API client with OAuth2 authentication."""

import time
from typing import Optional
from urllib.parse import urlencode

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException

from config.settings import settings
from src.utils.logger import logger


class SpotifyClient:
    """Client for interacting with Spotify Web API."""

    def __init__(self):
        """Initialize Spotify client with OAuth2."""
        self.client_id = settings.spotify.client_id
        self.client_secret = settings.spotify.client_secret
        self.redirect_uri = settings.spotify.redirect_uri
        self.scope = settings.spotify.scope

        # Initialize OAuth manager
        self.auth_manager = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
            cache_path=".spotify_cache",
        )

        # Initialize Spotipy client
        self.client: Optional[spotipy.Spotify] = None
        self._authenticate()

    def _authenticate(self) -> None:
        """Authenticate with Spotify API."""
        try:
            token_info = self.auth_manager.get_cached_token()

            if not token_info or self.auth_manager.is_token_expired(token_info):
                # Get new token
                token_info = self.auth_manager.get_access_token(check_cache=True)

            if token_info:
                self.client = spotipy.Spotify(auth=token_info["access_token"])
                logger.info("Successfully authenticated with Spotify API")
            else:
                # Need user authorization
                auth_url = self.auth_manager.get_authorize_url()
                logger.warning(
                    f"Authorization required. Please visit: {auth_url}\n"
                    f"After authorization, you will be redirected to: {self.redirect_uri}"
                )
                raise ValueError(
                    "Spotify authorization required. Please run the authentication flow first."
                )

        except Exception as e:
            logger.error(f"Failed to authenticate with Spotify API: {e}")
            raise

    def _handle_rate_limit(self, func, *args, **kwargs):
        """
        Execute function with rate limit handling and retries.

        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Function result
        """
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except SpotifyException as e:
                if e.http_status == 429:  # Rate limit exceeded
                    retry_after = int(e.headers.get("Retry-After", retry_delay))
                    logger.warning(
                        f"Rate limit exceeded. Waiting {retry_after} seconds before retry..."
                    )
                    time.sleep(retry_after)
                    retry_delay *= 2
                elif e.http_status == 401:  # Unauthorized - token expired
                    logger.warning("Token expired. Refreshing authentication...")
                    self._authenticate()
                else:
                    logger.error(f"Spotify API error: {e}")
                    raise

            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(retry_delay)
                retry_delay *= 2

        raise Exception("Max retries exceeded")

    def get_current_user(self) -> dict:
        """
        Get current user profile.

        Returns:
            User profile information
        """
        logger.info("Fetching current user profile...")
        return self._handle_rate_limit(self.client.current_user)

    def get_user_playlists(self, user_id: str, limit: int = 50) -> list:
        """
        Get user playlists with pagination.

        Args:
            user_id: Spotify user ID
            limit: Maximum number of playlists to fetch per page

        Returns:
            List of playlists
        """
        logger.info(f"Fetching playlists for user {user_id}...")
        playlists = []
        offset = 0

        while True:
            results = self._handle_rate_limit(
                self.client.user_playlists, user_id, limit=limit, offset=offset
            )
            playlists.extend(results.get("items", []))

            if not results.get("next"):
                break
            offset += limit

        logger.info(f"Fetched {len(playlists)} playlists")
        return playlists

    def get_playlist_tracks(self, playlist_id: str, limit: int = 100) -> list:
        """
        Get tracks from a playlist with pagination.

        Args:
            playlist_id: Spotify playlist ID
            limit: Maximum number of tracks to fetch per page

        Returns:
            List of tracks
        """
        logger.info(f"Fetching tracks from playlist {playlist_id}...")
        tracks = []
        offset = 0

        while True:
            results = self._handle_rate_limit(
                self.client.playlist_tracks, playlist_id, limit=limit, offset=offset
            )
            tracks.extend(results.get("items", []))

            if not results.get("next"):
                break
            offset += limit

        logger.info(f"Fetched {len(tracks)} tracks from playlist")
        return tracks

    def get_track_audio_features(self, track_ids: list) -> list:
        """
        Get audio features for multiple tracks.

        Args:
            track_ids: List of track IDs (max 100 per request)

        Returns:
            List of audio features
        """
        logger.info(f"Fetching audio features for {len(track_ids)} tracks...")
        all_features = []
        batch_size = 100

        for i in range(0, len(track_ids), batch_size):
            batch = track_ids[i : i + batch_size]
            features = self._handle_rate_limit(
                self.client.audio_features, batch
            )
            # Filter out None values (tracks without features)
            all_features.extend([f for f in features if f])

        logger.info(f"Fetched audio features for {len(all_features)} tracks")
        return all_features

    def get_artist(self, artist_id: str) -> dict:
        """
        Get artist information.

        Args:
            artist_id: Spotify artist ID

        Returns:
            Artist information
        """
        return self._handle_rate_limit(self.client.artist, artist_id)

    def get_artists(self, artist_ids: list) -> list:
        """
        Get multiple artists information.

        Args:
            artist_ids: List of artist IDs (max 50 per request)

        Returns:
            List of artist information
        """
        logger.info(f"Fetching information for {len(artist_ids)} artists...")
        all_artists = []
        batch_size = 50

        for i in range(0, len(artist_ids), batch_size):
            batch = artist_ids[i : i + batch_size]
            artists = self._handle_rate_limit(self.client.artists, batch)
            all_artists.extend(artists.get("artists", []))

        return all_artists

    def get_recently_played(self, limit: int = 50) -> list:
        """
        Get recently played tracks.

        Args:
            limit: Maximum number of tracks to fetch (max 50)

        Returns:
            List of recently played tracks
        """
        logger.info(f"Fetching {limit} recently played tracks...")
        results = self._handle_rate_limit(
            self.client.current_user_recently_played, limit=limit
        )
        return results.get("items", [])

    def get_top_tracks(self, time_range: str = "medium_term", limit: int = 20) -> list:
        """
        Get user's top tracks.

        Args:
            time_range: Time range (short_term, medium_term, long_term)
            limit: Maximum number of tracks (max 50)

        Returns:
            List of top tracks
        """
        logger.info(f"Fetching top {limit} tracks ({time_range})...")
        results = self._handle_rate_limit(
            self.client.current_user_top_tracks, time_range=time_range, limit=limit
        )
        return results.get("items", [])

    def get_top_artists(self, time_range: str = "medium_term", limit: int = 20) -> list:
        """
        Get user's top artists.

        Args:
            time_range: Time range (short_term, medium_term, long_term)
            limit: Maximum number of artists (max 50)

        Returns:
            List of top artists
        """
        logger.info(f"Fetching top {limit} artists ({time_range})...")
        results = self._handle_rate_limit(
            self.client.current_user_top_artists, time_range=time_range, limit=limit
        )
        return results.get("items", [])

