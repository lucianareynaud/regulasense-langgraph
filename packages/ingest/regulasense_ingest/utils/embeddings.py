"""
Utilities for generating embeddings from text.
"""
from typing import List, Dict, Any
import openai

from ..config import config

def get_embedding(text: str) -> List[float]:
    """
    Generate an embedding for the given text using OpenAI's API.
    
    Args:
        text: Text to embed
        
    Returns:
        List of embedding values
    """
    if not config.openai_api_key:
        raise ValueError("OPENAI_API_KEY not set in environment variables")
    
    client = openai.Client(api_key=config.openai_api_key)
    response = client.embeddings.create(
        input=text,
        model=config.embedding_model
    )
    return response.data[0].embedding


def chunk_text(text: str, chunk_size: int = None) -> List[str]:
    """
    Split text into chunks of approximately equal size.
    
    Args:
        text: Text to split
        chunk_size: Target size for each chunk (in characters)
        
    Returns:
        List of text chunks
    """
    chunk_size = chunk_size or config.chunk_size
    
    # Split by sentences to preserve context
    sentences = text.replace('\n', ' ').split('. ')
    chunks = []
    current_chunk = []
    current_size = 0
    
    for sentence in sentences:
        # Add period back except for the last sentence if it doesn't end with one
        if sentence and not sentence.endswith('.'):
            sentence = sentence + '.'
            
        # If adding this sentence would exceed chunk size and we already have content,
        # complete the current chunk and start a new one
        if current_size + len(sentence) > chunk_size and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_size = 0
        
        # If a single sentence is longer than chunk_size, we still keep it as one chunk
        current_chunk.append(sentence)
        current_size += len(sentence) + 1  # +1 for space
    
    # Add the last chunk if there's anything left
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks 