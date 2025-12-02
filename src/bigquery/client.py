"""BigQuery client for data operations."""

import os
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from google.oauth2 import service_account

from config.settings import settings
from src.utils.logger import logger


class BigQueryClient:
    """Client for interacting with BigQuery."""

    def __init__(self):
        """Initialize BigQuery client."""
        self.project_id = settings.bigquery.project_id
        self.dataset_id = settings.bigquery.dataset_id
        
        # Use explicit credentials from file
        credentials_path = settings.bigquery.credentials_path
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/bigquery"]
        )
        
        self.client = bigquery.Client(project=self.project_id, credentials=credentials)
        self.dataset_ref = self.client.dataset(self.dataset_id)

    def ensure_dataset_exists(self) -> None:
        """Create dataset if it doesn't exist."""
        try:
            self.client.get_dataset(self.dataset_ref)
            logger.info(f"Dataset {self.dataset_id} already exists")
        except NotFound:
            logger.info(f"Creating dataset {self.dataset_id}...")
            dataset = bigquery.Dataset(self.dataset_ref)
            dataset.location = "US"  # Set location
            dataset = self.client.create_dataset(dataset, exists_ok=True)
            logger.info(f"Dataset {self.dataset_id} created successfully")

    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists.

        Args:
            table_name: Name of the table

        Returns:
            True if table exists, False otherwise
        """
        table_ref = self.dataset_ref.table(table_name)
        try:
            self.client.get_table(table_ref)
            return True
        except NotFound:
            return False

    def create_table(self, table_name: str, schema: list, partitioned_by: str = None) -> None:
        """
        Create a table with the given schema.

        Args:
            table_name: Name of the table
            schema: List of SchemaField objects
            partitioned_by: Field name to partition by (optional)
        """
        table_ref = self.dataset_ref.table(table_name)

        if self.table_exists(table_name):
            logger.info(f"Table {table_name} already exists")
            return

        logger.info(f"Creating table {table_name}...")
        table = bigquery.Table(table_ref, schema=schema)

        # Set partitioning if specified
        if partitioned_by:
            table.time_partitioning = bigquery.TimePartitioning(
                field=partitioned_by,
                type_=bigquery.TimePartitioningType.DAY,
            )
            logger.info(f"Table {table_name} will be partitioned by {partitioned_by}")

        table = self.client.create_table(table)
        logger.info(f"Table {table_name} created successfully")

    def get_table(self, table_name: str):
        """
        Get table object.

        Args:
            table_name: Name of the table

        Returns:
            Table object
        """
        table_ref = self.dataset_ref.table(table_name)
        return self.client.get_table(table_ref)

    def query(self, query: str, use_legacy_sql: bool = False):
        """
        Execute a query.

        Args:
            query: SQL query string
            use_legacy_sql: Whether to use legacy SQL

        Returns:
            Query results
        """
        job_config = bigquery.QueryJobConfig(use_legacy_sql=use_legacy_sql)
        query_job = self.client.query(query, job_config=job_config)
        return query_job.result()

    def insert_rows(self, table_name: str, rows: list) -> None:
        """
        Insert rows into a table.

        Args:
            table_name: Name of the table
            rows: List of dictionaries representing rows
        """
        if not rows:
            logger.warning(f"No rows to insert into {table_name}")
            return

        table_ref = self.dataset_ref.table(table_name)
        errors = self.client.insert_rows_json(table_ref, rows)

        if errors:
            logger.error(f"Errors inserting rows into {table_name}: {errors}")
            raise Exception(f"Failed to insert rows: {errors}")

        logger.info(f"Successfully inserted {len(rows)} rows into {table_name}")

    def load_dataframe(self, table_name: str, dataframe, write_disposition: str = "WRITE_APPEND"):
        """
        Load a pandas DataFrame into a table.

        Args:
            table_name: Name of the table
            dataframe: Pandas DataFrame
            write_disposition: Write disposition (WRITE_APPEND, WRITE_TRUNCATE, WRITE_EMPTY)
        """
        if dataframe.empty:
            logger.warning(f"No data to load into {table_name}")
            return

        table_ref = self.dataset_ref.table(table_name)
        job_config = bigquery.LoadJobConfig(
            write_disposition=write_disposition,
        )

        logger.info(f"Loading {len(dataframe)} rows into {table_name}...")
        job = self.client.load_table_from_dataframe(dataframe, table_ref, job_config=job_config)
        job.result()  # Wait for job to complete

        logger.info(f"Successfully loaded {len(dataframe)} rows into {table_name}")

    def delete_table(self, table_name: str) -> None:
        """
        Delete a table.

        Args:
            table_name: Name of the table
        """
        table_ref = self.dataset_ref.table(table_name)
        self.client.delete_table(table_ref, not_found_ok=True)
        logger.info(f"Table {table_name} deleted")

    def get_table_size(self, table_name: str) -> int:
        """
        Get table size in bytes.

        Args:
            table_name: Name of the table

        Returns:
            Table size in bytes
        """
        table = self.get_table(table_name)
        return table.num_bytes

    def get_row_count(self, table_name: str) -> int:
        """
        Get number of rows in a table.

        Args:
            table_name: Name of the table

        Returns:
            Number of rows
        """
        query = f"SELECT COUNT(*) as count FROM `{self.project_id}.{self.dataset_id}.{table_name}`"
        results = self.query(query)
        return next(results).count

