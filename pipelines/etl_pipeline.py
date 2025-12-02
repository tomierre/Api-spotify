"""ETL pipeline for Spotify data extraction, transformation, and loading."""

from src.bigquery.loader import BigQueryLoader
from src.spotify.extractor import SpotifyExtractor
from src.spotify.transformers import DataTransformer
from src.utils.logger import logger


class ETLPipeline:
    """Main ETL pipeline orchestrating extraction, transformation, and loading."""

    def __init__(self):
        """Initialize ETL pipeline components."""
        self.extractor = SpotifyExtractor()
        self.transformer = DataTransformer()
        self.loader = BigQueryLoader()

    def run(self) -> dict:
        """
        Execute the complete ETL pipeline.

        Returns:
            Dictionary with execution results
        """
        logger.info("=" * 60)
        logger.info("Starting ETL Pipeline")
        logger.info("=" * 60)

        try:
            # Extract
            logger.info("Step 1: Extracting data from Spotify API...")
            raw_data = self.extractor.extract_all()
            logger.info(f"Extracted data: {len(raw_data.get('users', []))} users, "
                       f"{len(raw_data.get('playlists', []))} playlists, "
                       f"{len(raw_data.get('tracks', []))} tracks")

            # Transform
            logger.info("Step 2: Transforming and validating data...")
            transformed_data = self.transformer.transform_all(raw_data)
            logger.info("Data transformation completed successfully")

            # Load
            logger.info("Step 3: Loading data to BigQuery...")
            self.loader.load_all(transformed_data)
            logger.info("Data loaded to BigQuery successfully")

            # Summary
            summary = {
                "status": "success",
                "users": len(transformed_data.get("users", [])),
                "playlists": len(transformed_data.get("playlists", [])),
                "tracks": len(transformed_data.get("tracks", [])),
                "artists": len(transformed_data.get("artists", [])),
                "audio_features": len(transformed_data.get("track_audio_features", [])),
                "recently_played": len(transformed_data.get("recently_played", [])),
                "top_tracks": len(transformed_data.get("top_tracks", [])),
                "top_artists": len(transformed_data.get("top_artists", [])),
            }

            logger.info("=" * 60)
            logger.info("ETL Pipeline Completed Successfully")
            logger.info("=" * 60)
            logger.info(f"Summary: {summary}")

            return summary

        except Exception as e:
            logger.error(f"ETL Pipeline failed: {e}", exc_info=True)
            raise

