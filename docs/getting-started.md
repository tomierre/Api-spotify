# Getting Started

This guide will help you set up and run the Spotify ETL Pipeline from scratch.

## Prerequisites

Before you begin, ensure you have:

1. **Python 3.11 or higher** installed
2. **Spotify Developer Account** with an app created
3. **Google Cloud Platform account** with BigQuery enabled
4. **GCP Service Account** with BigQuery permissions

## Step 1: Clone and Setup Project

```bash
# Clone the repository
git clone <repository-url>
cd Spotify-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

## Step 2: Configure Spotify API

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Note your **Client ID** and **Client Secret**
4. Add redirect URI: `http://localhost:8888/callback`
5. Select **Web API** in the API/SDKs section

## Step 3: Configure Google Cloud Platform

1. Create a new GCP project or use an existing one
2. Enable BigQuery API
3. Create a Service Account:
   - Go to IAM & Admin → Service Accounts
   - Create new service account
   - Grant "BigQuery Data Editor" and "BigQuery Job User" roles
   - Create and download JSON key file

## Step 4: Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
```

Update `.env` with:

```env
# Spotify API
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
SPOTIFY_SCOPE=user-read-recently-played,user-top-read,user-library-read,playlist-read-private

# Google Cloud / BigQuery
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
BIGQUERY_PROJECT_ID=your-gcp-project-id
BIGQUERY_DATASET_ID=spotify_data

# Extraction Limits (optional - defaults shown)
MAX_PLAYLISTS=20
MAX_TRACKS_PER_PLAYLIST=100
MAX_RECENTLY_PLAYED=50
TOP_ITEMS_LIMIT=20
MAX_AUDIO_FEATURES_BATCH=100

# Application Configuration
LOG_LEVEL=INFO
ENVIRONMENT=development
```

## Step 5: Authenticate with Spotify

On first run, you'll need to authenticate with Spotify:

1. Run any script that uses Spotify API (e.g., `python scripts/run_etl.py`)
2. You'll see a URL in the console
3. Open the URL in your browser
4. Authorize the application
5. You'll be redirected to `http://localhost:8888/callback`
6. Copy the full URL from your browser
7. The token will be cached in `.spotify_cache` for future use

## Step 6: Setup BigQuery Tables

```bash
python scripts/setup_bigquery.py
```

This will:
- Create the BigQuery dataset (if it doesn't exist)
- Create all required tables with proper schemas
- Configure partitioning for time-series tables

## Step 7: Run ETL Pipeline

```bash
python scripts/run_etl.py
```

This will:
1. Extract data from Spotify API
2. Transform and validate the data
3. Load data into BigQuery

## Step 8: Launch Streamlit Dashboard

```bash
streamlit run streamlit_app/main.py
```

Open your browser to `http://localhost:8501` to view the dashboard.

## Step 9: Monitor Costs (Optional)

```bash
python scripts/monitor_costs.py
```

This will show:
- Current storage usage
- Query usage for the last 30 days
- Projections for monthly usage
- Warnings if approaching free tier limits

## Troubleshooting

### Spotify Authentication Issues

- Ensure redirect URI matches exactly in Spotify app settings
- Clear `.spotify_cache` file and re-authenticate
- Check that scopes are correctly set

### BigQuery Connection Issues

- Verify `GOOGLE_APPLICATION_CREDENTIALS` path is correct
- Ensure service account has proper permissions
- Check that BigQuery API is enabled in GCP

### Import Errors

- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again
- Check Python version: `python --version` (should be 3.11+)

## Next Steps

- Read the [Architecture](architecture.md) guide to understand the system design
- Check the [API Reference](api-reference.md) for code documentation
- Review [Deployment](deployment.md) for production setup and cost monitoring
