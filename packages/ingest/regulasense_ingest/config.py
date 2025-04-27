"""
Configuration module for the RegulaSense data ingestion system.
"""
import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

class IngestConfig(BaseModel):
    """Configuration for the data ingestion module."""
    # Qdrant configuration
    qdrant_url: str = Field(
        default=os.getenv("QDRANT_URL", "http://localhost:6333"), 
        description="URL for the Qdrant server"
    )
    collection_name: str = Field(
        default=os.getenv("COLLECTION_NAME", "regulasense-evidence"),
        description="Name of the Qdrant collection to store data in"
    )
    
    # API keys
    openai_api_key: Optional[str] = Field(
        default=os.getenv("OPENAI_API_KEY"),
        description="OpenAI API key for embeddings"
    )
    fred_api_key: Optional[str] = Field(
        default=os.getenv("FRED_API_KEY"),
        description="FRED API key for accessing Federal Reserve data"
    )
    
    # Embedding configuration
    embedding_model: str = Field(
        default=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        description="OpenAI embedding model to use"
    )
    
    # Chunking configuration
    chunk_size: int = Field(
        default=int(os.getenv("CHUNK_SIZE", "1000")),
        description="Size of text chunks for embedding"
    )
    
    # Source specific configurations
    fred_series: list[str] = Field(
        default=["GDP", "UNRATE", "CPIAUCSL", "DFF", "SP500"],
        description="Default FRED data series to ingest"
    )
    
    bis_categories: list[str] = Field(
        default=["banking", "statistics", "regulation"],
        description="BIS report categories to ingest"
    )
    
    fsb_document_types: list[str] = Field(
        default=["policy", "guidance", "standards"],
        description="FSB document types to ingest"
    )

    # Snapshot configuration
    default_snapshot_dir: Path = Field(
        default=Path("./sample_data"),
        description="Default directory for snapshot output"
    )
    
    def __str__(self) -> str:
        """String representation of the configuration."""
        return (
            f"IngestConfig:\n"
            f"  - qdrant_url: {self.qdrant_url}\n"
            f"  - collection_name: {self.collection_name}\n"
            f"  - embedding_model: {self.embedding_model}\n"
            f"  - chunk_size: {self.chunk_size}\n"
            f"  - FRED API key: {'set' if self.fred_api_key else 'not set'}\n"
            f"  - OpenAI API key: {'set' if self.openai_api_key else 'not set'}"
        )

# Default configuration instance
config = IngestConfig() 