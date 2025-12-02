#!/usr/bin/env python3
"""Script to run the ETL pipeline."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipelines.etl_pipeline import ETLPipeline
from src.utils.logger import logger


def main():
    """Execute the ETL pipeline."""
    try:
        pipeline = ETLPipeline()
        results = pipeline.run()

        print("\n" + "=" * 60)
        print("ETL Pipeline Execution Summary")
        print("=" * 60)
        print(f"Status: {results['status']}")
        print(f"Users: {results['users']}")
        print(f"Playlists: {results['playlists']}")
        print(f"Tracks: {results['tracks']}")
        print(f"Artists: {results['artists']}")
        print(f"Audio Features: {results['audio_features']}")
        print(f"Recently Played: {results['recently_played']}")
        print(f"Top Tracks: {results['top_tracks']}")
        print(f"Top Artists: {results['top_artists']}")
        print("=" * 60)

    except Exception as e:
        logger.error(f"ETL pipeline execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

