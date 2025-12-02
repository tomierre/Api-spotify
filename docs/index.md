# Spotify ETL Pipeline Documentation

Welcome to the Spotify ETL Pipeline documentation! This project provides a complete solution for extracting data from Spotify API, transforming it, and loading it into BigQuery for analysis.

> **Note:** This documentation is automatically deployed via GitHub Actions.

## Overview

The Spotify ETL Pipeline is designed to:

- **Extract** data from Spotify Web API (user profile, playlists, tracks, artists, audio features)
- **Transform** and validate data using Pydantic models
- **Load** data into BigQuery with optimized schemas and incremental updates
- **Visualize** data through an interactive Streamlit dashboard
- **Optimize costs** to stay within BigQuery's free tier limits

## Key Features

- 🔐 **OAuth2 Authentication** with Spotify API
- 📊 **Comprehensive Data Extraction** from multiple Spotify endpoints
- ✅ **Data Validation** using Pydantic models
- 🚀 **Efficient BigQuery Loading** with upsert/incremental strategies
- 📈 **Interactive Dashboard** with Streamlit
- 💰 **Cost Optimization** to maintain free tier usage
- 📚 **Complete Documentation** with MkDocs

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Setup BigQuery**:
   ```bash
   python scripts/setup_bigquery.py
   ```

4. **Run ETL Pipeline**:
   ```bash
   python scripts/run_etl.py
   ```

5. **Launch Dashboard**:
   ```bash
   streamlit run streamlit_app/main.py
   ```

## Project Structure

```
Spotify-api/
├── config/              # Configuration and schemas
├── src/                 # Source code
│   ├── spotify/        # Spotify API client and extractors
│   ├── bigquery/       # BigQuery client and loader
│   └── utils/          # Utilities (logging, validators)
├── pipelines/          # ETL pipelines
├── streamlit_app/      # Streamlit dashboard
├── tests/              # Unit tests
├── scripts/            # Executable scripts
└── docs/               # Documentation
```

## Documentation Sections

- **[Getting Started](getting-started.md)** - Installation and setup guide
- **[Architecture](architecture.md)** - System architecture and design
- **[API Reference](api-reference.md)** - Code documentation
- **[Spotify API Guide](spotify-api-guide.md)** - Spotify API endpoints and usage
- **[Deployment](deployment.md)** - Deployment and cost monitoring

## Requirements

- Python 3.11+
- Spotify Developer Account (Client ID and Secret)
- Google Cloud Platform account with BigQuery enabled
- GCP Service Account credentials (JSON file)

## Cost Optimization

This project is designed to operate within BigQuery's free tier:

- **10 GB** of storage per month (free)
- **1 TB** of queries per month (free)

See [Deployment Guide](deployment.md) for cost monitoring and optimization strategies.

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
