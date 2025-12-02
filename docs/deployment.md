# Deployment Guide

This guide covers deployment, cost monitoring, and optimization strategies for the Spotify ETL Pipeline.

## Production Setup

### Environment Configuration

1. **Set Environment Variables**:
   ```bash
   export SPOTIFY_CLIENT_ID="your_client_id"
   export SPOTIFY_CLIENT_SECRET="your_client_secret"
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
   export BIGQUERY_PROJECT_ID="your-project-id"
   export ENVIRONMENT="production"
   export LOG_LEVEL="INFO"
   ```

2. **Secure Credentials**:
   - Never commit `.env` file to version control
   - Use secret management services in production
   - Rotate credentials regularly

### BigQuery Setup

1. **Create Dataset**:
   ```bash
   python scripts/setup_bigquery.py
   ```

2. **Verify Tables**:
   - Check that all tables are created
   - Verify schemas are correct
   - Confirm partitioning is set up

### Scheduled Execution

#### Using Cron (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Run ETL daily at 2 AM
0 2 * * * cd /path/to/Spotify-api && /path/to/venv/bin/python scripts/run_etl.py >> logs/cron.log 2>&1
```

#### Using Cloud Scheduler (GCP)

1. Create Cloud Function or Cloud Run service
2. Schedule with Cloud Scheduler
3. Set appropriate timezone and frequency

## Cost Monitoring

### BigQuery Free Tier

BigQuery offers a free tier with:

- **10 GB** of storage per month
- **1 TB** of queries per month
- **1 GB** of streaming inserts per month

### Monitoring Script

Run the cost monitoring script regularly:

```bash
python scripts/monitor_costs.py
```

This script shows:
- Current storage usage
- Query usage for last 30 days
- Monthly projections
- Warnings if approaching limits

### Setting Up Budget Alerts in GCP

1. **Navigate to Billing**:
   - Go to [GCP Console](https://console.cloud.google.com)
   - Select your project
   - Go to Billing → Budgets & alerts

2. **Create Budget**:
   - Click "Create Budget"
   - Set amount: **$1 USD/month**
   - Select your billing account
   - Choose project scope

3. **Configure Alerts**:
   - Add alert at **50%** of budget
   - Add alert at **90%** of budget
   - Add alert at **100%** of budget
   - Add email notifications

4. **Save Budget**:
   - Review settings
   - Create budget

### Monitoring BigQuery Usage

#### Storage Usage

1. Go to BigQuery Console
2. Select your dataset
3. View table sizes in the UI
4. Check "Storage" tab for total usage

#### Query Usage

1. Go to BigQuery Console
2. Click "Job history"
3. Filter by date range
4. View "Bytes processed" column

#### Using Information Schema

Query usage can be checked with:

```sql
SELECT
  SUM(total_bytes_processed) / POW(1024, 4) as total_tb
FROM
  `project-id.region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
WHERE
  creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  AND job_type = 'QUERY'
```

## Cost Optimization Strategies

### Storage Optimization

1. **Data Retention Policies**:
   - Implement retention for time-series data
   - Delete old `recently_played` records (>90 days)
   - Archive or delete old `top_tracks`/`top_artists` snapshots

2. **Efficient Data Types**:
   - Use STRING instead of TEXT
   - Use INT64 instead of FLOAT where possible
   - Avoid storing redundant data

3. **Partitioning**:
   - Only partition time-series tables
   - Use date partitioning for `recently_played`
   - Partition `top_tracks` and `top_artists` by `extracted_at`

### Query Optimization

1. **Limit Extraction**:
   - Extract only necessary data
   - Use extraction limits (MAX_PLAYLISTS, etc.)
   - Avoid full table scans

2. **Incremental Loading**:
   - Only load new/changed data
   - Use timestamps to track last extraction
   - Implement checkpoint system

3. **Streamlit Caching**:
   - Use `@st.cache_data` for queries
   - Set appropriate TTL
   - Cache aggregated results

4. **Query Best Practices**:
   - Always use LIMIT clauses
   - Filter early with WHERE
   - Use SELECT specific columns
   - Avoid SELECT *

### Example: Data Retention Script

```python
from google.cloud import bigquery

client = bigquery.Client()
dataset_id = "spotify_data"
table_id = "recently_played"

# Delete records older than 90 days
query = f"""
DELETE FROM `{client.project}.{dataset_id}.{table_id}`
WHERE played_at < TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
"""

job = client.query(query)
job.result()
```

## Troubleshooting

### High Storage Usage

**Symptoms**: Storage approaching 10 GB limit

**Solutions**:
1. Implement data retention policies
2. Review table sizes
3. Delete unnecessary historical data
4. Archive old data to Cloud Storage

### High Query Usage

**Symptoms**: Query usage approaching 1 TB limit

**Solutions**:
1. Review Streamlit dashboard queries
2. Add more aggressive caching
3. Optimize queries (add LIMIT, WHERE clauses)
4. Reduce dashboard refresh frequency
5. Limit data extraction frequency

### Authentication Issues

**Symptoms**: 401 Unauthorized errors

**Solutions**:
1. Check token expiration
2. Re-authenticate with Spotify
3. Verify credentials in `.env`
4. Check service account permissions

### Rate Limiting

**Symptoms**: 429 Too Many Requests errors

**Solutions**:
1. Reduce extraction frequency
2. Implement longer delays between requests
3. Batch requests more efficiently
4. Check rate limit headers

## Best Practices

1. **Regular Monitoring**: Run `monitor_costs.py` weekly
2. **Set Alerts**: Configure GCP budget alerts
3. **Review Usage**: Check BigQuery console monthly
4. **Optimize Queries**: Review and optimize slow queries
5. **Data Retention**: Implement and maintain retention policies
6. **Documentation**: Keep deployment notes updated

## Scaling Considerations

### Current Limitations

- Single user extraction
- Manual or scheduled execution
- Suitable for personal use

### Future Scaling

If you need to scale:

1. **Multi-User Support**:
   - Store tokens per user
   - Track extraction per user
   - Partition data by user_id

2. **Increased Volume**:
   - Consider paid BigQuery tier
   - Implement more aggressive caching
   - Use Cloud Functions for processing

3. **Real-Time Updates**:
   - Use streaming inserts
   - Implement change data capture
   - Use Pub/Sub for events

## Support

For issues or questions:

1. Check logs in `logs/spotify_etl.log`
2. Review error messages
3. Check GCP console for BigQuery errors
4. Review Spotify API status

## References

- [BigQuery Pricing](https://cloud.google.com/bigquery/pricing)
- [BigQuery Free Tier](https://cloud.google.com/free/docs/free-cloud-features#bigquery)
- [GCP Budget Alerts](https://cloud.google.com/billing/docs/how-to/budgets)
