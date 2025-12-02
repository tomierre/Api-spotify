#!/usr/bin/env python3
"""Script to monitor BigQuery usage and costs."""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.cloud import bigquery
from config.settings import settings
from src.utils.logger import logger


def get_storage_usage(client: bigquery.Client) -> dict:
    """
    Get storage usage for all tables in the dataset.

    Args:
        client: BigQuery client

    Returns:
        Dictionary with storage information
    """
    dataset_id = settings.bigquery.dataset_id
    project_id = settings.bigquery.project_id
    dataset_ref = client.dataset(dataset_id, project=project_id)

    storage_info = {
        "total_bytes": 0,
        "total_gb": 0.0,
        "tables": {},
    }

    try:
        tables = list(client.list_tables(dataset_ref))
        for table in tables:
            table_ref = dataset_ref.table(table.table_id)
            table_obj = client.get_table(table_ref)
            size_bytes = table_obj.num_bytes
            size_gb = size_bytes / (1024 ** 3)

            storage_info["total_bytes"] += size_bytes
            storage_info["total_gb"] += size_gb
            storage_info["tables"][table.table_id] = {
                "bytes": size_bytes,
                "gb": round(size_gb, 4),
                "rows": table_obj.num_rows,
            }
    except Exception as e:
        logger.error(f"Error getting storage usage: {e}")
        return storage_info

    storage_info["total_gb"] = round(storage_info["total_gb"], 4)
    return storage_info


def get_query_usage(client: bigquery.Client, days: int = 30) -> dict:
    """
    Get query usage statistics for the last N days.

    Args:
        client: BigQuery client
        days: Number of days to look back

    Returns:
        Dictionary with query usage information
    """
    project_id = settings.bigquery.project_id
    dataset_id = settings.bigquery.dataset_id

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    query = f"""
    SELECT
        SUM(total_bytes_processed) as total_bytes,
        SUM(total_bytes_processed) / POW(1024, 4) as total_tb,
        COUNT(*) as query_count,
        AVG(total_bytes_processed) / POW(1024, 4) as avg_tb_per_query
    FROM
        `{project_id}.region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
    WHERE
        creation_time >= TIMESTAMP('{start_date.isoformat()}')
        AND creation_time < TIMESTAMP('{end_date.isoformat()}')
        AND job_type = 'QUERY'
        AND statement_type = 'SELECT'
    """

    try:
        query_job = client.query(query)
        results = query_job.result()
        row = next(results, None)

        if row and row.total_bytes:
            return {
                "total_bytes": row.total_bytes,
                "total_tb": round(row.total_tb, 4),
                "query_count": row.query_count,
                "avg_tb_per_query": round(row.avg_tb_per_query, 6),
                "days": days,
            }
        else:
            return {
                "total_bytes": 0,
                "total_tb": 0.0,
                "query_count": 0,
                "avg_tb_per_query": 0.0,
                "days": days,
            }
    except Exception as e:
        logger.warning(f"Could not fetch query usage (may require billing API): {e}")
        return {
            "total_bytes": 0,
            "total_tb": 0.0,
            "query_count": 0,
            "avg_tb_per_query": 0.0,
            "days": days,
            "error": str(e),
        }


def check_free_tier_limits(storage_gb: float, queries_tb: float) -> dict:
    """
    Check if usage is within free tier limits.

    Args:
        storage_gb: Storage used in GB
        queries_tb: Queries processed in TB

    Returns:
        Dictionary with limit status
    """
    FREE_STORAGE_GB = 10.0
    FREE_QUERIES_TB = 1.0

    storage_percent = (storage_gb / FREE_STORAGE_GB) * 100
    queries_percent = (queries_tb / FREE_QUERIES_TB) * 100

    return {
        "storage": {
            "used_gb": storage_gb,
            "limit_gb": FREE_STORAGE_GB,
            "percent": round(storage_percent, 2),
            "within_limit": storage_gb < FREE_STORAGE_GB,
            "warning": storage_percent > 50,
        },
        "queries": {
            "used_tb": queries_tb,
            "limit_tb": FREE_QUERIES_TB,
            "percent": round(queries_percent, 2),
            "within_limit": queries_tb < FREE_QUERIES_TB,
            "warning": queries_percent > 50,
        },
    }


def print_report(storage_info: dict, query_info: dict, limits: dict):
    """Print formatted cost monitoring report."""
    print("\n" + "=" * 70)
    print("BIGQUERY COST MONITORING REPORT")
    print("=" * 70)
    print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project: {settings.bigquery.project_id}")
    print(f"Dataset: {settings.bigquery.dataset_id}")
    print()

    # Storage section
    print("-" * 70)
    print("STORAGE USAGE")
    print("-" * 70)
    storage = limits["storage"]
    status = "✓" if storage["within_limit"] else "✗"
    warning = "⚠ WARNING" if storage["warning"] else ""
    print(f"Status: {status} {warning}")
    print(f"Used: {storage['used_gb']:.4f} GB / {storage['limit_gb']} GB")
    print(f"Percentage: {storage['percent']:.2f}%")
    print()

    if storage_info["tables"]:
        print("Storage by table:")
        for table_name, info in sorted(
            storage_info["tables"].items(), key=lambda x: x[1]["gb"], reverse=True
        ):
            print(f"  {table_name:30s} {info['gb']:8.4f} GB ({info['rows']:,} rows)")
    print()

    # Query usage section
    print("-" * 70)
    print("QUERY USAGE (Last 30 days)")
    print("-" * 70)
    queries = limits["queries"]
    status = "✓" if queries["within_limit"] else "✗"
    warning = "⚠ WARNING" if queries["warning"] else ""
    print(f"Status: {status} {warning}")
    print(f"Used: {queries['used_tb']:.4f} TB / {queries['limit_tb']} TB")
    print(f"Percentage: {queries['percent']:.2f}%")
    if query_info.get("query_count"):
        print(f"Total queries: {query_info['query_count']:,}")
        print(f"Avg per query: {query_info['avg_tb_per_query']:.6f} TB")
    if query_info.get("error"):
        print(f"Note: {query_info['error']}")
    print()

    # Projections
    print("-" * 70)
    print("MONTHLY PROJECTIONS")
    print("-" * 70)
    days_elapsed = query_info["days"]
    if days_elapsed > 0:
        daily_query_tb = queries["used_tb"] / days_elapsed
        projected_monthly_tb = daily_query_tb * 30
        print(f"Daily query usage: {daily_query_tb:.6f} TB/day")
        print(f"Projected monthly: {projected_monthly_tb:.4f} TB/month")
        if projected_monthly_tb > queries["limit_tb"]:
            print("⚠ WARNING: Projected usage exceeds free tier limit!")
    print()

    # Recommendations
    print("-" * 70)
    print("RECOMMENDATIONS")
    print("-" * 70)
    recommendations = []
    if storage["warning"]:
        recommendations.append(
            f"⚠ Storage usage is at {storage['percent']:.1f}% - consider data retention policies"
        )
    if queries["warning"]:
        recommendations.append(
            f"⚠ Query usage is at {queries['percent']:.1f}% - optimize queries and use caching"
        )
    if not recommendations:
        recommendations.append("✓ All usage is well within free tier limits")
    for rec in recommendations:
        print(f"  {rec}")
    print()

    print("=" * 70)


def main():
    """Main function to monitor BigQuery costs."""
    try:
        logger.info("Starting BigQuery cost monitoring...")

        client = bigquery.Client(
            project=settings.bigquery.project_id,
        )

        # Get storage usage
        logger.info("Fetching storage usage...")
        storage_info = get_storage_usage(client)

        # Get query usage
        logger.info("Fetching query usage...")
        query_info = get_query_usage(client, days=30)

        # Check limits
        limits = check_free_tier_limits(
            storage_info["total_gb"], query_info["total_tb"]
        )

        # Print report
        print_report(storage_info, query_info, limits)

        # Exit with error code if over limits
        if not limits["storage"]["within_limit"] or not limits["queries"]["within_limit"]:
            logger.warning("Usage exceeds free tier limits!")
            sys.exit(1)

        logger.info("Cost monitoring completed successfully")

    except Exception as e:
        logger.error(f"Cost monitoring failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

