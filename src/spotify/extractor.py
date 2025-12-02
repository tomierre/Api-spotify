"""Data extraction from Spotify API."""

from datetime import datetime
from typing import Dict, List, Set

from config.settings import settings
from src.spotify.client import SpotifyClient
from src.utils.logger import logger


class SpotifyExtractor:
    """Extract data from Spotify API."""

    def __init__(self):
        """Initialize extractor with Spotify client."""
        self.client = SpotifyClient()
        self.limits = settings.extraction_limits
        self.extracted_at = datetime.utcnow()

    def extract_user_profile(self) -> Dict:
        """
        Extract current user profile.

        Returns:
            User profile data
        """
        logger.info("Extracting user profile...")
        user = self.client.get_current_user()
        return {
            "user_id": user.get("id"),
            "display_name": user.get("display_name"),
            "followers": user.get("followers", {}).get("total", 0),
            "country": user.get("country"),
            "product": user.get("product"),
            "extracted_at": self.extracted_at.isoformat(),
        }

    def extract_playlists(self, user_id: str) -> List[Dict]:
        """
        Extract user playlists with limits.

        Args:
            user_id: Spotify user ID

        Returns:
            List of playlist data
        """
        logger.info("Extracting playlists...")
        all_playlists = self.client.get_user_playlists(user_id)

        # Apply limit
        playlists = all_playlists[: self.limits["max_playlists"]]
        logger.info(f"Extracted {len(playlists)} playlists (limit: {self.limits['max_playlists']})")

        result = []
        for playlist in playlists:
            result.append(
                {
                    "playlist_id": playlist.get("id"),
                    "name": playlist.get("name"),
                    "description": playlist.get("description"),
                    "owner_id": playlist.get("owner", {}).get("id"),
                    "public": playlist.get("public", False),
                    "collaborative": playlist.get("collaborative", False),
                    "followers_count": playlist.get("followers", {}).get("total", 0),
                    "tracks_count": playlist.get("tracks", {}).get("total", 0),
                    "extracted_at": self.extracted_at.isoformat(),
                }
            )

        return result

    def extract_playlist_tracks(self, playlist_id: str) -> List[Dict]:
        """
        Extract tracks from a playlist with limits.

        Args:
            playlist_id: Spotify playlist ID

        Returns:
            List of track data from playlist
        """
        logger.info(f"Extracting tracks from playlist {playlist_id}...")
        all_tracks = self.client.get_playlist_tracks(playlist_id)

        # Apply limit
        tracks = all_tracks[: self.limits["max_tracks_per_playlist"]]
        logger.info(
            f"Extracted {len(tracks)} tracks (limit: {self.limits['max_tracks_per_playlist']})"
        )

        result = []
        for item in tracks:
            track = item.get("track")
            if not track or track.get("is_local"):
                continue

            # Extract artist IDs
            artist_ids = [artist.get("id") for artist in track.get("artists", []) if artist.get("id")]

            result.append(
                {
                    "playlist_id": playlist_id,
                    "track_id": track.get("id"),
                    "added_at": item.get("added_at"),
                    "added_by": item.get("added_by", {}).get("id"),
                    "position": item.get("position"),
                    "extracted_at": self.extracted_at.isoformat(),
                    # Track metadata for later processing
                    "_track_data": {
                        "id": track.get("id"),
                        "name": track.get("name"),
                        "artists": artist_ids,
                        "album": track.get("album", {}),
                        "duration_ms": track.get("duration_ms"),
                        "popularity": track.get("popularity"),
                        "explicit": track.get("explicit"),
                        "external_urls": track.get("external_urls", {}).get("spotify"),
                    },
                }
            )

        return result

    def extract_tracks(self, track_data_list: List[Dict]) -> List[Dict]:
        """
        Extract track information from track data.

        Args:
            track_data_list: List of track data dictionaries

        Returns:
            List of normalized track data
        """
        logger.info(f"Extracting information for {len(track_data_list)} tracks...")
        tracks = []

        for track_data in track_data_list:
            track = track_data.get("_track_data", {})
            if not track.get("id"):
                continue

            album = track.get("album", {})
            tracks.append(
                {
                    "track_id": track.get("id"),
                    "name": track.get("name"),
                    "artists": track.get("artists", []),
                    "album_id": album.get("id"),
                    "album_name": album.get("name"),
                    "release_date": album.get("release_date"),
                    "duration_ms": track.get("duration_ms"),
                    "popularity": track.get("popularity"),
                    "explicit": track.get("explicit", False),
                    "external_urls": track.get("external_urls"),
                    "extracted_at": self.extracted_at.isoformat(),
                }
            )

        return tracks

    def extract_audio_features(self, track_ids: List[str]) -> List[Dict]:
        """
        Extract audio features for tracks.

        Args:
            track_ids: List of track IDs

        Returns:
            List of audio features
        """
        if not track_ids:
            return []

        # Remove duplicates
        unique_track_ids = list(set(track_ids))
        logger.info(f"Extracting audio features for {len(unique_track_ids)} unique tracks...")

        # Process in batches
        batch_size = self.limits["max_audio_features_batch"]
        all_features = []

        for i in range(0, len(unique_track_ids), batch_size):
            batch = unique_track_ids[i : i + batch_size]
            try:
                features = self.client.get_track_audio_features(batch)
            except Exception as e:
                logger.warning(f"Failed to get audio features for batch {i//batch_size + 1}: {e}")
                continue

            for feature in features:
                if feature:
                    all_features.append(
                        {
                            "track_id": feature.get("id"),
                            "danceability": feature.get("danceability"),
                            "energy": feature.get("energy"),
                            "key": feature.get("key"),
                            "loudness": feature.get("loudness"),
                            "mode": feature.get("mode"),
                            "speechiness": feature.get("speechiness"),
                            "acousticness": feature.get("acousticness"),
                            "instrumentalness": feature.get("instrumentalness"),
                            "liveness": feature.get("liveness"),
                            "valence": feature.get("valence"),
                            "tempo": feature.get("tempo"),
                            "time_signature": feature.get("time_signature"),
                            "extracted_at": self.extracted_at.isoformat(),
                        }
                    )

        logger.info(f"Extracted audio features for {len(all_features)} tracks")
        return all_features

    def extract_artists(self, artist_ids: List[str]) -> List[Dict]:
        """
        Extract artist information.

        Args:
            artist_ids: List of artist IDs

        Returns:
            List of artist data
        """
        if not artist_ids:
            return []

        # Remove duplicates
        unique_artist_ids = list(set(artist_ids))
        logger.info(f"Extracting information for {len(unique_artist_ids)} unique artists...")

        try:
            artists = self.client.get_artists(unique_artist_ids)
            if not isinstance(artists, list):
                logger.warning(f"Unexpected response type from get_artists: {type(artists)}")
                return []
        except Exception as e:
            logger.warning(f"Failed to extract artists: {e}. Continuing without artists...")
            return []

        result = []
        for artist in artists:
            if artist is None:
                continue
            result.append(
                {
                    "artist_id": artist.get("id"),
                    "name": artist.get("name"),
                    "genres": artist.get("genres", []),
                    "popularity": artist.get("popularity"),
                    "followers": artist.get("followers", {}).get("total", 0),
                    "external_urls": artist.get("external_urls", {}).get("spotify"),
                    "extracted_at": self.extracted_at.isoformat(),
                }
            )

        return result

    def extract_recently_played(self) -> List[Dict]:
        """
        Extract recently played tracks with limits.

        Returns:
            List of recently played track data
        """
        logger.info("Extracting recently played tracks...")
        try:
            recently_played = self.client.get_recently_played(limit=self.limits["max_recently_played"])
            if recently_played is None:
                logger.warning("No recently played tracks returned. Continuing...")
                return []
        except Exception as e:
            logger.warning(f"Failed to extract recently played tracks: {e}. Continuing...")
            return []

        result = []
        for item in recently_played:
            if item is None:
                continue
            track = item.get("track", {})
            context = item.get("context") or {}

            result.append(
                {
                    "track_id": track.get("id"),
                    "played_at": item.get("played_at"),
                    "context_type": context.get("type"),
                    "context_uri": context.get("uri"),
                    "extracted_at": self.extracted_at.isoformat(),
                }
            )

        logger.info(f"Extracted {len(result)} recently played tracks")
        return result

    def extract_top_tracks(self) -> List[Dict]:
        """
        Extract top tracks for all time ranges.

        Returns:
            List of top track data
        """
        logger.info("Extracting top tracks...")
        time_ranges = ["short_term", "medium_term", "long_term"]
        all_top_tracks = []

        for time_range in time_ranges:
            tracks = self.client.get_top_tracks(
                time_range=time_range, limit=self.limits["top_items_limit"]
            )

            for position, track in enumerate(tracks, start=1):
                all_top_tracks.append(
                    {
                        "track_id": track.get("id"),
                        "time_range": time_range,
                        "position": position,
                        "extracted_at": self.extracted_at.isoformat(),
                    }
                )

        logger.info(f"Extracted top tracks for {len(time_ranges)} time ranges")
        return all_top_tracks

    def extract_top_artists(self) -> List[Dict]:
        """
        Extract top artists for all time ranges.

        Returns:
            List of top artist data
        """
        logger.info("Extracting top artists...")
        time_ranges = ["short_term", "medium_term", "long_term"]
        all_top_artists = []

        for time_range in time_ranges:
            artists = self.client.get_top_artists(
                time_range=time_range, limit=self.limits["top_items_limit"]
            )

            for position, artist in enumerate(artists, start=1):
                all_top_artists.append(
                    {
                        "artist_id": artist.get("id"),
                        "time_range": time_range,
                        "position": position,
                        "extracted_at": self.extracted_at.isoformat(),
                    }
                )

        logger.info(f"Extracted top artists for {len(time_ranges)} time ranges")
        return all_top_artists

    def extract_all(self) -> Dict:
        """
        Extract all available data from Spotify API.

        Returns:
            Dictionary containing all extracted data
        """
        logger.info("Starting complete data extraction from Spotify API...")

        # Extract user profile
        user = self.extract_user_profile()
        user_id = user["user_id"]

        # Extract playlists
        playlists = self.extract_playlists(user_id)

        # Extract tracks from playlists
        all_playlist_tracks = []
        all_track_data = []
        all_artist_ids: Set[str] = set()

        for playlist in playlists:
            playlist_tracks = self.extract_playlist_tracks(playlist["playlist_id"])
            all_playlist_tracks.extend(playlist_tracks)

            # Collect track data and artist IDs
            for pt in playlist_tracks:
                track_data = pt.get("_track_data", {})
                if track_data:
                    all_track_data.append(track_data)
                    all_artist_ids.update(track_data.get("artists", []))

        # Extract tracks
        tracks = self.extract_tracks(all_playlist_tracks)

        # Extract audio features (with error handling)
        track_ids = [t["track_id"] for t in tracks if t.get("track_id")]
        try:
            audio_features = self.extract_audio_features(track_ids)
        except Exception as e:
            logger.warning(f"Failed to extract audio features: {e}. Continuing without audio features...")
            audio_features = []

        # Extract artists
        artists = self.extract_artists(list(all_artist_ids))

        # Extract recently played
        recently_played = self.extract_recently_played()

        # Extract top tracks and artists
        top_tracks = self.extract_top_tracks()
        top_artists = self.extract_top_artists()

        # Prepare playlist_tracks (remove _track_data)
        playlist_tracks = [
            {k: v for k, v in pt.items() if k != "_track_data"} for pt in all_playlist_tracks
        ]

        result = {
            "users": [user],
            "playlists": playlists,
            "tracks": tracks,
            "track_audio_features": audio_features,
            "artists": artists,
            "playlist_tracks": playlist_tracks,
            "recently_played": recently_played,
            "top_tracks": top_tracks,
            "top_artists": top_artists,
        }

        logger.info("Complete data extraction finished")
        return result

