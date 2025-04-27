"""
Utilities for interacting with Qdrant vector database.
"""
from typing import List, Dict, Any, Optional
from tqdm import tqdm
from qdrant_client import QdrantClient
from qdrant_client.http import models

from ..config import config
from ..sources.base import DataItem
from .embeddings import get_embedding, chunk_text

def ensure_collection_exists(client: Optional[QdrantClient] = None) -> QdrantClient:
    """
    Ensure the Qdrant collection exists, creating it if necessary.
    
    Args:
        client: Optional QdrantClient instance
        
    Returns:
        QdrantClient instance
    """
    # Create client if not provided
    if client is None:
        client = QdrantClient(url=config.qdrant_url)
    
    # Check if collection exists
    try:
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if config.collection_name not in collection_names:
            # Create collection
            client.create_collection(
                collection_name=config.collection_name,
                vectors_config=models.VectorParams(
                    size=1536,  # OpenAI embedding dimension
                    distance=models.Distance.COSINE
                )
            )
            print(f"Created collection {config.collection_name}")
        else:
            print(f"Collection {config.collection_name} already exists")
    
    except Exception as e:
        print(f"Error ensuring collection exists: {e}")
        raise
    
    return client


def upload_items(items: List[DataItem], client: Optional[QdrantClient] = None) -> int:
    """
    Upload items to Qdrant.
    
    Args:
        items: List of DataItem objects to upload
        client: Optional QdrantClient instance
        
    Returns:
        Number of points uploaded
    """
    # Create client if not provided
    if client is None:
        client = QdrantClient(url=config.qdrant_url)
    
    # Ensure collection exists
    client = ensure_collection_exists(client)
    
    # Prepare points for upload
    points_to_upload = []
    points_processed = 0
    
    # Process each item
    print(f"Processing {len(items)} items for upload to Qdrant...")
    for item_idx, item in enumerate(tqdm(items)):
        # Chunk the content
        chunks = chunk_text(item.content)
        
        # Process each chunk
        for chunk_idx, chunk in enumerate(chunks):
            try:
                # Generate embedding
                embedding = get_embedding(chunk)
                
                # Create a unique ID for this chunk
                point_id = f"{item.source}_{item.source_id}_{chunk_idx}"
                
                # Create metadata for this chunk, combining item metadata with chunk info
                metadata = {
                    **item.metadata,
                    "source": item.source,
                    "source_id": item.source_id,
                    "chunk_index": chunk_idx,
                    "total_chunks": len(chunks),
                    "timestamp": item.timestamp,
                    "text": chunk
                }
                
                # Create point
                point = models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=metadata
                )
                
                points_to_upload.append(point)
                points_processed += 1
                
                # Upload in batches of 100 to avoid memory issues
                if len(points_to_upload) >= 100:
                    client.upsert(
                        collection_name=config.collection_name,
                        points=points_to_upload
                    )
                    points_to_upload = []
            
            except Exception as e:
                print(f"Error processing chunk {chunk_idx} of item {item_idx}: {e}")
    
    # Upload any remaining points
    if points_to_upload:
        client.upsert(
            collection_name=config.collection_name,
            points=points_to_upload
        )
    
    print(f"Uploaded {points_processed} points to Qdrant")
    return points_processed 