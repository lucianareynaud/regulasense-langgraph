"""
Federal Reserve Economic Data (FRED) source for RegulaSense.
"""
from typing import List, Dict, Any, Generator, Optional
import datetime
import pandas as pd
from fredapi import Fred

from ..config import config
from .base import BaseSource, DataItem

class FredSource(BaseSource):
    """Source for Federal Reserve Economic Data (FRED)."""
    
    def __init__(self):
        """Initialize the FRED data source."""
        super().__init__("fred")
        if not config.fred_api_key:
            raise ValueError("FRED_API_KEY not set in environment variables")
        self.fred = Fred(api_key=config.fred_api_key)
    
    def fetch(self, 
              series_ids: Optional[List[str]] = None, 
              start_date: Optional[str] = None,
              end_date: Optional[str] = None,
              **kwargs) -> Generator[DataItem, None, None]:
        """
        Fetch data from FRED.
        
        Args:
            series_ids: List of FRED series IDs to fetch (e.g., 'GDP', 'UNRATE')
            start_date: Start date in YYYY-MM-DD format (default: 5 years ago)
            end_date: End date in YYYY-MM-DD format (default: today)
            **kwargs: Additional parameters to pass to FRED.get_series
            
        Yields:
            DataItem for each series with its description and data
        """
        # Use default series if none provided
        series_ids = series_ids or config.fred_series
        
        # Set default date range if not provided
        if not start_date:
            start_date = (datetime.datetime.now() - datetime.timedelta(days=5*365)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.datetime.now().strftime('%Y-%m-%d')
        
        # Fetch each series
        for series_id in series_ids:
            try:
                # Get series info
                series_info = self.fred.get_series_info(series_id)
                title = series_info.get('title', f'Series {series_id}')
                notes = series_info.get('notes', '')
                units = series_info.get('units', '')
                frequency = series_info.get('frequency', '')
                
                # Get series data
                data = self.fred.get_series(
                    series_id,
                    observation_start=start_date,
                    observation_end=end_date,
                    **kwargs
                )
                
                # Skip empty series
                if data is None or len(data) == 0:
                    print(f"No data found for FRED series {series_id}")
                    continue
                
                # Convert to string representation
                if isinstance(data, pd.Series):
                    # Format the time series data
                    data_str = "\n".join([
                        f"{date.strftime('%Y-%m-%d')}: {value}" 
                        for date, value in data.items()
                    ])
                else:
                    data_str = str(data)
                
                # Create a descriptive text document
                content = f"""
                {title}
                Series ID: {series_id}
                
                Description:
                {notes}
                
                Units: {units}
                Frequency: {frequency}
                
                Data:
                {data_str}
                """
                
                # Create metadata
                metadata = {
                    "title": title,
                    "series_id": series_id,
                    "units": units,
                    "frequency": frequency,
                    "start_date": start_date,
                    "end_date": end_date,
                    "observation_count": len(data) if hasattr(data, "__len__") else 0
                }
                
                # Yield the data item
                yield DataItem(
                    content=content.strip(),
                    source="fred",
                    source_id=series_id,
                    metadata=metadata
                )
                
            except Exception as e:
                print(f"Error fetching FRED series {series_id}: {e}") 