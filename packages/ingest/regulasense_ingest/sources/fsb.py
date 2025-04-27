"""
Financial Stability Board (FSB) source for RegulaSense.
"""
from typing import List, Dict, Any, Generator, Optional
import requests
from bs4 import BeautifulSoup
import time

from ..config import config
from .base import BaseSource, DataItem

class FsbSource(BaseSource):
    """Source for Financial Stability Board (FSB) documents."""
    
    def __init__(self):
        """Initialize the FSB data source."""
        super().__init__("fsb")
        self.base_url = "https://www.fsb.org"
        self.publications_url = f"{self.base_url}/publications"
    
    def fetch(self, 
              document_types: Optional[List[str]] = None, 
              max_items: int = 50,
              **kwargs) -> Generator[DataItem, None, None]:
        """
        Fetch data from FSB.
        
        Args:
            document_types: List of FSB document types to fetch (e.g., 'policy', 'guidance')
            max_items: Maximum number of items to fetch per type
            **kwargs: Additional parameters (unused)
            
        Yields:
            DataItem for each document
        """
        # Use default document types if none provided
        document_types = document_types or config.fsb_document_types
        
        # Get main publications page
        try:
            print(f"Fetching FSB publications from {self.publications_url}")
            response = requests.get(self.publications_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get all publication URLs - adjust selectors based on actual FSB site structure
            all_links = soup.find_all('a')
            publication_links = []
            
            # Filter links to get relevant publications
            for link in all_links:
                href = link.get('href', '')
                text = link.get_text().strip().lower()
                
                # Check if the link is likely a publication
                is_publication = False
                for doc_type in document_types:
                    if doc_type.lower() in text or doc_type.lower() in href.lower():
                        is_publication = True
                        break
                
                if is_publication and href and '/publications/' in href:
                    # Normalize URL
                    if href.startswith('/'):
                        full_url = f"{self.base_url}{href}"
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        full_url = f"{self.base_url}/{href}"
                    
                    publication_links.append((full_url, text))
            
            # Keep track of documents processed
            processed_count = 0
            processed_urls = set()
            
            # Process each publication
            for pub_url, pub_title in publication_links:
                if processed_count >= max_items or pub_url in processed_urls:
                    continue
                
                try:
                    # Add to processed set to avoid duplicates
                    processed_urls.add(pub_url)
                    
                    # Get publication page
                    pub_response = requests.get(pub_url)
                    pub_response.raise_for_status()
                    pub_soup = BeautifulSoup(pub_response.text, 'html.parser')
                    
                    # Extract title
                    title_elem = pub_soup.find('h1') or pub_soup.find('h2')
                    title = title_elem.get_text().strip() if title_elem else pub_title
                    
                    # Extract content - adjust selectors based on actual FSB site structure
                    content_div = pub_soup.select_one(".publication-content") or pub_soup.select_one("article") 
                    if not content_div:
                        content_div = pub_soup.select_one("main") or pub_soup
                    
                    # Extract text content from paragraphs
                    paragraphs = content_div.find_all('p')
                    content_text = "\n\n".join([p.get_text().strip() for p in paragraphs])
                    
                    # Try to determine document type
                    doc_type = "Unknown"
                    for dt in document_types:
                        if dt.lower() in pub_url.lower() or dt.lower() in title.lower():
                            doc_type = dt
                            break
                    
                    # Create a complete document
                    document_content = f"""
                    {title}
                    
                    Source: Financial Stability Board
                    Type: {doc_type}
                    URL: {pub_url}
                    
                    {content_text}
                    """
                    
                    # Create metadata
                    metadata = {
                        "title": title,
                        "type": doc_type,
                        "url": pub_url
                    }
                    
                    # Create a unique ID
                    doc_id = pub_url.split('/')[-1]
                    if not doc_id or doc_id == "":
                        doc_id = f"fsb_{doc_type}_{processed_count}"
                    
                    # Yield the data item
                    yield DataItem(
                        content=document_content.strip(),
                        source="fsb",
                        source_id=doc_id,
                        metadata=metadata
                    )
                    
                    processed_count += 1
                    
                    # Be nice to the server
                    time.sleep(1)
                
                except Exception as e:
                    print(f"Error processing FSB document {pub_url}: {e}")
        
        except Exception as e:
            print(f"Error fetching FSB publications: {e}") 