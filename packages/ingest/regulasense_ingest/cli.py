"""
Command-line interface for RegulaSense data ingestion.
"""
import os
import sys
import json
from pathlib import Path
from typing import List, Optional
import click

from .config import config
from .sources.fred import FredSource
from .sources.bis import BisSource
from .sources.fsb import FsbSource
from .utils.qdrant import upload_items

SOURCES = {
    "fred": FredSource,
    "bis": BisSource,
    "fsb": FsbSource
}

@click.group()
@click.version_option(version="0.1.0")
def cli():
    """RegulaSense data ingestion tool for financial regulatory data."""
    pass

@cli.command()
@click.argument("sources", nargs=-1)
@click.option("--snapshot", type=click.Path(), help="Save data to directory instead of uploading to Qdrant")
@click.option("--max-items", type=int, default=50, help="Maximum items to fetch per source")
def ingest(sources: List[str], snapshot: Optional[str], max_items: int):
    """
    Ingest data from specified sources.
    
    SOURCES: One or more of [fred, bis, fsb]
    """
    if not sources:
        print("Error: No sources specified. Choose from: fred, bis, fsb")
        sys.exit(1)
    
    # Validate sources
    invalid_sources = [s for s in sources if s not in SOURCES]
    if invalid_sources:
        print(f"Error: Invalid sources: {', '.join(invalid_sources)}. Choose from: fred, bis, fsb")
        sys.exit(1)
    
    # Create snapshot directory if needed
    snapshot_dir = None
    if snapshot:
        snapshot_dir = Path(snapshot)
        os.makedirs(snapshot_dir, exist_ok=True)
        print(f"Will save snapshots to {snapshot_dir}")
    
    # Process each source
    for source_name in sources:
        try:
            print(f"\nProcessing source: {source_name}")
            
            # Create source instance
            source_class = SOURCES[source_name]
            source = source_class()
            
            if snapshot_dir:
                # Save snapshot
                output_file = source.snapshot(snapshot_dir, max_items=max_items)
                print(f"Saved snapshot to {output_file}")
            else:
                # Fetch and upload to Qdrant
                print(f"Fetching data from {source_name}...")
                items = list(source.fetch(max_items=max_items))
                print(f"Fetched {len(items)} items from {source_name}")
                
                if items:
                    print(f"Uploading to Qdrant collection '{config.collection_name}'...")
                    upload_items(items)
                    print(f"Successfully uploaded {len(items)} items from {source_name} to Qdrant")
                else:
                    print(f"No items to upload from {source_name}")
        
        except Exception as e:
            print(f"Error processing source {source_name}: {e}")
    
    print("\nData ingestion completed!")

def main():
    """Entry point for the CLI."""
    cli()

if __name__ == "__main__":
    main() 