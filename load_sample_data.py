#!/usr/bin/env python3
"""
Sample data loader for RegulaSense.
Fetches SEC 10-K data and loads it into Qdrant.
"""
import os
from typing import List, Dict, Any
import requests
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models
import openai

# Load environment variables
load_dotenv()

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "regulasense-evidence")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize clients
openai.api_key = OPENAI_API_KEY
client = QdrantClient(url=QDRANT_URL)

# Sample SEC data - URLs for Apple Inc. 10-K filing sections
SEC_URLS = [
    "https://www.sec.gov/Archives/edgar/data/320193/000032019322000108/aapl-20220924.htm",
]

def create_collection() -> None:
    """Create vector collection if it doesn't exist."""
    try:
        client.get_collection(COLLECTION_NAME)
        print(f"Collection {COLLECTION_NAME} already exists")
    except Exception:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=1536,  # OpenAI embedding dimension
                distance=models.Distance.COSINE
            )
        )
        print(f"Created collection {COLLECTION_NAME}")

def fetch_sec_text(url: str) -> str:
    """Fetch text from SEC filing URL."""
    try:
        response = requests.get(url, headers={"User-Agent": "RegulaSense Research Agent"})
        response.raise_for_status()
        # Extract only main content - simplified for demo
        content = response.text
        # In a real system, we would parse HTML properly
        return content[:20000]  # Truncate for demo purposes
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

def get_embedding(text: str) -> List[float]:
    """Get OpenAI embedding for text."""
    client = openai.Client(api_key=OPENAI_API_KEY)
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def chunk_text(text: str, chunk_size: int = 1000) -> List[str]:
    """Split text into chunks of approximately equal size."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        if current_size + len(word) <= chunk_size:
            current_chunk.append(word)
            current_size += len(word) + 1  # +1 for space
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_size = len(word)
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

def load_data() -> None:
    """Fetch SEC data, chunk it, generate embeddings, and load into Qdrant."""
    # Create collection
    create_collection()
    
    # Track items to upload
    items_to_upload = []
    
    # Process each URL
    for i, url in enumerate(SEC_URLS):
        print(f"Processing {url}")
        text = fetch_sec_text(url)
        if not text:
            continue
        
        # Chunk the text
        chunks = chunk_text(text)
        print(f"Created {len(chunks)} chunks")
        
        # Process each chunk
        for j, chunk in enumerate(chunks):
            try:
                # Get embedding
                embedding = get_embedding(chunk)
                
                # Prepare item for upload
                item = models.PointStruct(
                    id=f"{i}-{j}",
                    vector=embedding,
                    payload={"text": chunk, "source": url}
                )
                items_to_upload.append(item)
                print(f"Processed chunk {j+1}/{len(chunks)}")
            except Exception as e:
                print(f"Error processing chunk {j}: {e}")
    
    # Upload to Qdrant
    if items_to_upload:
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=items_to_upload
        )
        print(f"Uploaded {len(items_to_upload)} items to Qdrant")

if __name__ == "__main__":
    print("Loading sample SEC data into Qdrant...")
    load_data()
    print("Done!") 