"""
Bank for International Settlements (BIS) source for RegulaSense.
"""
from typing import List, Dict, Any, Generator, Optional
import requests
from bs4 import BeautifulSoup
import time

from ..config import config
from .base import BaseSource, DataItem

class BisSource(BaseSource):
    """Source for Bank for International Settlements (BIS) documents."""
    
    def __init__(self):
        """Initialize the BIS data source."""
        super().__init__("bis")
        self.base_url = "https://www.bis.org"
        self.publications_url = f"{self.base_url}/publications"
    
    def fetch(self, 
              categories: Optional[List[str]] = None, 
              max_items: int = 50,
              **kwargs) -> Generator[DataItem, None, None]:
        """
        Fetch data from BIS.
        
        Args:
            categories: List of BIS categories to fetch (e.g., 'banking', 'statistics')
            max_items: Maximum number of items to fetch per category
            **kwargs: Additional parameters (unused)
            
        Yields:
            DataItem for each document
        """
        # Use default categories if none provided
        categories = categories or config.bis_categories
        
        # Fetch documents for each category
        for category in categories:
            try:
                item_count = 0
                category_url = f"{self.publications_url}/{category}"
                print(f"Fetching BIS documents from {category_url}")
                
                # Get the publication list
                response = requests.get(category_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find document links - adjust selectors based on actual BIS site structure
                document_links = soup.select(".publication-list .publication-item a")
                if not document_links:
                    # Try alternative selectors based on BIS site structure
                    document_links = soup.select("a[href*='/publications/']")
                
                # Process each document
                for link in document_links:
                    if item_count >= max_items:
                        break
                    
                    # Get document URL
                    href = link.get('href')
                    if not href:
                        continue
                    
                    # Normalize URL
                    if href.startswith('/'):
                        doc_url = f"{self.base_url}{href}"
                    elif href.startswith('http'):
                        doc_url = href
                    else:
                        doc_url = f"{self.base_url}/{href}"
                    
                    try:
                        # Get document title
                        title = link.get_text().strip()
                        if not title:
                            title = f"BIS Document {doc_url.split('/')[-1]}"
                        
                        # Get document content
                        doc_response = requests.get(doc_url)
                        doc_response.raise_for_status()
                        doc_soup = BeautifulSoup(doc_response.text, 'html.parser')
                        
                        # Extract content - adjust selectors based on actual BIS site structure
                        content_div = doc_soup.select_one(".content-wrapper")
                        if not content_div:
                            content_div = doc_soup.select_one("article") or doc_soup.select_one("main")
                        
                        # If we found content, process it
                        if content_div:
                            # Extract text
                            paragraphs = content_div.find_all('p')
                            content_text = "\n\n".join([p.get_text().strip() for p in paragraphs])
                            
                            # Create a complete document with title
                            document_content = f"""
                            {title}
                            
                            Source: Bank for International Settlements
                            Category: {category}
                            URL: {doc_url}
                            
                            {content_text}
                            """
                            
                            # Create metadata
                            metadata = {
                                "title": title,
                                "category": category,
                                "url": doc_url
                            }
                            
                            # Create a unique ID
                            doc_id = doc_url.split('/')[-1]
                            if not doc_id or doc_id == "":
                                doc_id = f"bis_{category}_{item_count}"
                            
                            # Yield the data item
                            yield DataItem(
                                content=document_content.strip(),
                                source="bis",
                                source_id=doc_id,
                                metadata=metadata
                            )
                            
                            item_count += 1
                            
                            # Be nice to the server
                            time.sleep(1)
                        
                    except Exception as e:
                        print(f"Error processing BIS document {doc_url}: {e}")
                
            except Exception as e:
                print(f"Error fetching BIS category {category}: {e}") 