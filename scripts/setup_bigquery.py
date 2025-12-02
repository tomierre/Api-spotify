#!/usr/bin/env python3
"""Setup script to create BigQuery tables."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.bigquery_schema import PARTITIONED_TABLES, TABLE_SCHEMAS
from src.bigquery.client import BigQueryClient
from src.utils.logger import logger


def main():
    """Create all BigQuery tables with their schemas."""
    logger.info("Setting up BigQuery tables...")

    client = BigQueryClient()
    client.ensure_dataset_exists()

    # Create all tables
    for table_name, schema in TABLE_SCHEMAS.items():
        partitioned_by = PARTITIONED_TABLES.get(table_name)
        client.create_table(table_name, schema, partitioned_by=partitioned_by)

    logger.info("BigQuery setup completed successfully!")


if __name__ == "__main__":
    main()

