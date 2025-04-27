"""
Base classes for data sources in the RegulaSense ingestion system.
"""
import os
import json
import datetime
from pathlib import Path
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Generator, Optional

class DataItem:
    """Representation of a single data item for ingestion."""
    
    def __init__(self, 
                 content: str, 
                 source: str, 
                 source_id: str, 
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a data item.
        
        Args:
            content: The textual content of the item
            source: Source identifier (e.g., 'fred', 'bis', 'fsb')
            source_id: Unique identifier within the source
            metadata: Additional metadata for the item
        """
        self.content = content
        self.source = source
        self.source_id = source_id
        self.metadata = metadata or {}
        self.timestamp = datetime.datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary representation."""
        return {
            "content": self.content,
            "source": self.source,
            "source_id": self.source_id,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataItem':
        """Create a DataItem from a dictionary."""
        item = cls(
            content=data["content"],
            source=data["source"],
            source_id=data["source_id"],
            metadata=data.get("metadata", {})
        )
        item.timestamp = data.get("timestamp", item.timestamp)
        return item
    
    def __str__(self) -> str:
        return f"DataItem(source={self.source}, id={self.source_id}, len={len(self.content)})"


class BaseSource(ABC):
    """Abstract base class for all data sources."""
    
    def __init__(self, name: str):
        """
        Initialize a data source.
        
        Args:
            name: Unique name for the source
        """
        self.name = name
    
    @abstractmethod
    def fetch(self, **kwargs) -> Generator[DataItem, None, None]:
        """
        Fetch data from the source.
        
        Args:
            **kwargs: Source-specific parameters
            
        Yields:
            DataItem objects
        """
        pass
        
    def snapshot(self, output_dir: Path, **kwargs) -> Path:
        """
        Save a snapshot of the source data to disk.
        
        Args:
            output_dir: Directory to write snapshot files
            **kwargs: Source-specific parameters
            
        Returns:
            Path to the output directory with snapshot files
        """
        # Create source-specific directory
        source_dir = output_dir / self.name
        os.makedirs(source_dir, exist_ok=True)
        
        # Save each item as a JSON file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = source_dir / f"{self.name}_{timestamp}.json"
        
        # Collect items
        items = list(self.fetch(**kwargs))
        
        # Write to file
        with open(output_file, 'w') as f:
            json.dump([item.to_dict() for item in items], f, indent=2)
        
        print(f"Saved {len(items)} items from {self.name} to {output_file}")
        return output_file 