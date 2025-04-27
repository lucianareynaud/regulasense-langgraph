"""
RegulaSense Data Ingestion module.

A pluggable data ingestion system for pulling regulatory data from
financial sources and storing it in a vector database.
"""
from .config import config, IngestConfig

__version__ = "0.1.0"
__all__ = [
    'config',
    'IngestConfig'
]
