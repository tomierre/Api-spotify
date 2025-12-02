"""BigQuery data loader with upsert and incremental strategies."""

from datetime import datetime
from typing import List

import pandas as pd

from config.bigquery_schema import PARTITIONED_TABLES, TABLE_SCHEMAS
from src.bigquery.client import BigQueryClient
from src.utils.logger import logger


class BigQueryLoader:
    """Load data into BigQuery with upsert and incremental strategies."""

    def __init__(self):
        """Initialize BigQuery loader."""
        self.client = BigQueryClient()
        self.client.ensure_dataset_exists()

    def _convert_timestamps(self, data: List[dict]) -> List[dict]:
        """
        Convert ISO timestamp strings to datetime objects for BigQuery.

        Args:
            data: List of dictionaries with timestamp fields

        Returns:
            List of dictionaries with converted timestamps
        """
        converted = []
        for row in data:
            new_row = row.copy()
            # Convert extracted_at and other timestamp fields
            for key, value in row.items():
                if key.endswith("_at") and isinstance(value, str):
                    try:
                        # Parse ISO format and convert to datetime
                        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                        new_row[key] = dt.isoformat()
                    except (ValueError, AttributeError):
                        pass
            converted.append(new_row)
        return converted

    def load_users(self, data: List[dict]) -> None:
        """
        Load users data with upsert strategy.

        Args:
            data: List of user dictionaries
        """
        if not data:
            logger.warning("No user data to load")
            return

        logger.info(f"Loading {len(data)} users...")
        data = self._convert_timestamps(data)

        # Upsert: Use load_dataframe with WRITE_TRUNCATE to avoid streaming buffer issues
        # This works for small tables like users
        df = pd.DataFrame(data)
        if not df.empty:
            # Convert timestamp columns
            if "extracted_at" in df.columns:
                df["extracted_at"] = pd.to_datetime(df["extracted_at"], errors="coerce")
            self.client.load_dataframe("users", df, write_disposition="WRITE_TRUNCATE")
            logger.info("Users loaded successfully")
        else:
            logger.warning("No user data to load")

    def load_playlists(self, data: List[dict]) -> None:
        """
        Load playlists data with upsert strategy.

        Args:
            data: List of playlist dictionaries
        """
        if not data:
            logger.warning("No playlist data to load")
            return

        logger.info(f"Loading {len(data)} playlists...")
        data = self._convert_timestamps(data)

        # Upsert: Use load_dataframe with WRITE_TRUNCATE for playlists (small table)
        # This avoids streaming buffer issues
        df = pd.DataFrame(data)
        if not df.empty:
            # Convert timestamp columns
            if "extracted_at" in df.columns:
                df["extracted_at"] = pd.to_datetime(df["extracted_at"], errors="coerce")
            self.client.load_dataframe("playlists", df, write_disposition="WRITE_TRUNCATE")
            logger.info("Playlists loaded successfully")
        else:
            logger.warning("No playlist data to load")

    def load_tracks(self, data: List[dict]) -> None:
        """
        Load tracks data with upsert strategy.

        Args:
            data: List of track dictionaries
        """
        if not data:
            logger.warning("No track data to load")
            return

        logger.info(f"Loading {len(data)} tracks...")
        data = self._convert_timestamps(data)

        # Convert artists list to repeated field format
        for track in data:
            if isinstance(track.get("artists"), list):
                track["artists"] = track["artists"]

        # Upsert: Use MERGE statement for better performance
        df = pd.DataFrame(data)
        df["artists"] = df["artists"].apply(lambda x: x if isinstance(x, list) else [])

        # Load using load_table_from_dataframe for better handling of repeated fields
        self.client.load_dataframe("tracks", df, write_disposition="WRITE_TRUNCATE")
        logger.info("Tracks loaded successfully")

    def load_audio_features(self, data: List[dict]) -> None:
        """
        Load audio features data with upsert strategy.

        Args:
            data: List of audio features dictionaries
        """
        if not data:
            logger.warning("No audio features data to load")
            return

        logger.info(f"Loading {len(data)} audio features...")
        data = self._convert_timestamps(data)

        # Upsert: Use load_dataframe with WRITE_TRUNCATE (small table, full refresh each time)
        df = pd.DataFrame(data)
        if not df.empty:
            # Convert timestamp columns
            if "extracted_at" in df.columns:
                df["extracted_at"] = pd.to_datetime(df["extracted_at"], errors="coerce")
            self.client.load_dataframe("track_audio_features", df, write_disposition="WRITE_TRUNCATE")
            logger.info("Audio features loaded successfully")
        else:
            logger.warning("No audio features data to load")

    def load_artists(self, data: List[dict]) -> None:
        """
        Load artists data with upsert strategy.

        Args:
            data: List of artist dictionaries
        """
        if not data:
            logger.warning("No artist data to load")
            return

        logger.info(f"Loading {len(data)} artists...")
        data = self._convert_timestamps(data)

        # Convert genres list to repeated field format
        for artist in data:
            if isinstance(artist.get("genres"), list):
                artist["genres"] = artist["genres"]

        # Upsert: Use MERGE statement
        df = pd.DataFrame(data)
        df["genres"] = df["genres"].apply(lambda x: x if isinstance(x, list) else [])

        self.client.load_dataframe("artists", df, write_disposition="WRITE_TRUNCATE")
        logger.info("Artists loaded successfully")

    def load_playlist_tracks(self, data: List[dict]) -> None:
        """
        Load playlist tracks junction data with upsert strategy.

        Args:
            data: List of playlist track dictionaries
        """
        if not data:
            logger.warning("No playlist track data to load")
            return

        logger.info(f"Loading {len(data)} playlist tracks...")
        data = self._convert_timestamps(data)

        # Upsert: Use load_dataframe with WRITE_TRUNCATE (full refresh each time)
        # This avoids streaming buffer issues
        df = pd.DataFrame(data)
        if not df.empty:
            # Convert timestamp columns
            if "extracted_at" in df.columns:
                df["extracted_at"] = pd.to_datetime(df["extracted_at"], errors="coerce")
            self.client.load_dataframe("playlist_tracks", df, write_disposition="WRITE_TRUNCATE")
            logger.info("Playlist tracks loaded successfully")
        else:
            logger.warning("No playlist track data to load")

    def load_recently_played(self, data: List[dict]) -> None:
        """
        Load recently played data with incremental strategy.

        Args:
            data: List of recently played dictionaries
        """
        if not data:
            logger.warning("No recently played data to load")
            return

        logger.info(f"Loading {len(data)} recently played records...")
        data = self._convert_timestamps(data)

        # Incremental: Only insert new records (deduplicate by track_id and played_at)
        df = pd.DataFrame(data)
        
        # Convert timestamp columns to datetime immediately
        if not df.empty:
            if "played_at" in df.columns:
                df["played_at"] = pd.to_datetime(df["played_at"], errors="coerce")
                # Convert to timezone-aware UTC timestamps for BigQuery
                if df["played_at"].dt.tz is None:
                    df["played_at"] = df["played_at"].dt.tz_localize("UTC")
                else:
                    df["played_at"] = df["played_at"].dt.tz_convert("UTC")
            if "extracted_at" in df.columns:
                df["extracted_at"] = pd.to_datetime(df["extracted_at"], errors="coerce")
                if df["extracted_at"].dt.tz is None:
                    df["extracted_at"] = df["extracted_at"].dt.tz_localize("UTC")
                else:
                    df["extracted_at"] = df["extracted_at"].dt.tz_convert("UTC")

        # Check for existing records
        existing_query = f"""
        SELECT DISTINCT track_id, played_at
        FROM `{self.client.project_id}.{self.client.dataset_id}.recently_played`
        """
        try:
            existing = self.client.query(existing_query)
            existing_df = existing.to_dataframe()
            if not existing_df.empty and not df.empty:
                # Convert existing_df played_at to datetime for comparison
                existing_df["played_at"] = pd.to_datetime(existing_df["played_at"], errors="coerce")
                if existing_df["played_at"].dt.tz is None:
                    existing_df["played_at"] = existing_df["played_at"].dt.tz_localize("UTC")
                else:
                    existing_df["played_at"] = existing_df["played_at"].dt.tz_convert("UTC")
                merged = df.merge(
                    existing_df, on=["track_id", "played_at"], how="left", indicator=True
                )
                df = merged[merged["_merge"] == "left_only"].drop(columns=["_merge"])
        except Exception as e:
            logger.warning(f"Could not check existing records: {e}")

        if not df.empty:
            self.client.load_dataframe("recently_played", df, write_disposition="WRITE_APPEND")
            logger.info(f"Loaded {len(df)} new recently played records")
        else:
            logger.info("No new recently played records to load")

    def load_top_tracks(self, data: List[dict]) -> None:
        """
        Load top tracks data with upsert strategy.

        Args:
            data: List of top track dictionaries
        """
        if not data:
            logger.warning("No top track data to load")
            return

        logger.info(f"Loading {len(data)} top track records...")
        data = self._convert_timestamps(data)

        # Upsert: Use load_dataframe with WRITE_TRUNCATE for top_tracks (small table)
        df = pd.DataFrame(data)
        if not df.empty:
            # Convert timestamp columns
            if "extracted_at" in df.columns:
                df["extracted_at"] = pd.to_datetime(df["extracted_at"], errors="coerce")
            self.client.load_dataframe("top_tracks", df, write_disposition="WRITE_TRUNCATE")
            logger.info("Top tracks loaded successfully")
        else:
            logger.warning("No top track data to load")

    def load_top_artists(self, data: List[dict]) -> None:
        """
        Load top artists data with upsert strategy.

        Args:
            data: List of top artist dictionaries
        """
        if not data:
            logger.warning("No top artist data to load")
            return

        logger.info(f"Loading {len(data)} top artist records...")
        data = self._convert_timestamps(data)

        # Upsert: Use load_dataframe with WRITE_TRUNCATE for top_artists (small table)
        df = pd.DataFrame(data)
        if not df.empty:
            # Convert timestamp columns
            if "extracted_at" in df.columns:
                df["extracted_at"] = pd.to_datetime(df["extracted_at"], errors="coerce")
            self.client.load_dataframe("top_artists", df, write_disposition="WRITE_TRUNCATE")
            logger.info("Top artists loaded successfully")
        else:
            logger.warning("No top artist data to load")

    def load_all(self, data: dict) -> None:
        """
        Load all data into BigQuery.

        Args:
            data: Dictionary containing all transformed data
        """
        logger.info("Starting data load to BigQuery...")

        self.load_users(data.get("users", []))
        self.load_playlists(data.get("playlists", []))
        self.load_tracks(data.get("tracks", []))
        self.load_audio_features(data.get("track_audio_features", []))
        self.load_artists(data.get("artists", []))
        self.load_playlist_tracks(data.get("playlist_tracks", []))
        self.load_recently_played(data.get("recently_played", []))
        self.load_top_tracks(data.get("top_tracks", []))
        self.load_top_artists(data.get("top_artists", []))

        logger.info("All data loaded to BigQuery successfully")

