# RegulaSense Data Ingestion

A pluggable data ingestion module for the RegulaSense system that can pull or snapshot content from financial regulatory sources, then push it into a Qdrant vector database.

## Features

- Fetch data from multiple financial regulatory sources:
  - FRED (Federal Reserve Economic Data)
  - BIS (Bank for International Settlements)
  - FSB (Financial Stability Board)
- Store data in Qdrant for semantic search and retrieval
- Generate embeddings for financial data using OpenAI
- Snapshot data to disk for archival or preprocessing
- Command-line interface with sub-command pattern

## Installation

```bash
# Install in development mode
pip install -e packages/ingest

# Or if you're distributing the package
pip install packages/ingest
```

## Usage

### Command Line Interface

The module provides a command-line tool called `ingest` with the following functionality:

```bash
# Ingest data from all sources directly to Qdrant
ingest fred fsb bis

# Ingest data from specific sources
ingest fred bis

# Create snapshots instead of uploading to Qdrant
ingest fred --snapshot ./sample_data

# Limit the number of items fetched per source
ingest fsb --max-items 20
```

### Environment Variables

The following environment variables can be set:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key
FRED_API_KEY=your_fred_api_key

# Optional
QDRANT_URL=http://localhost:6333
COLLECTION_NAME=regulasense-evidence
EMBEDDING_MODEL=text-embedding-3-small
CHUNK_SIZE=1000
```

## Adding New Data Sources

The module is designed to be easily extensible with new data sources:

1. Create a new source file in `regulasense_ingest/sources/`
2. Subclass `BaseSource` and implement the `fetch()` method
3. Register the source in `regulasense_ingest/cli.py`

## Development

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e packages/ingest

# Run tests
pytest packages/ingest/tests
``` 