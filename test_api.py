#!/usr/bin/env python3
"""
Test script for RegulaSense API.
Sends a sample query and prints the response.
"""
import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000/run")

def test_api():
    """Test the RegulaSense API with a sample query."""
    # Sample query for financial statement extraction
    query = {
        "prompt": "Extract the key financial metrics from Apple's most recent 10-K filing. Generate an XBRL-compatible financial statement with their revenue, assets, and net income."
    }
    
    try:
        # Send request to API
        print(f"Sending request to {API_URL}...")
        response = requests.post(API_URL, json=query, timeout=300)
        response.raise_for_status()
        
        # Parse and print response
        result = response.json()
        print("\nAPI Response:")
        print(json.dumps(result, indent=2))
        
        # Parse as JSON if it's a string
        if isinstance(result, str):
            try:
                parsed = json.loads(result)
                print("\nParsed Financial Statement:")
                print(json.dumps(parsed, indent=2))
            except:
                pass
        
        return True
    except Exception as e:
        print(f"Error testing API: {e}")
        return False

if __name__ == "__main__":
    print("Testing RegulaSense API...")
    success = test_api()
    if success:
        print("\nAPI test completed successfully!")
    else:
        print("\nAPI test failed.") 