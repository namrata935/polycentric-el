"""
Business service for fetching and storing business data from Overpass API.
"""
from utils.overpass_client import fetch_overpass_data
from utils.overpass_parser import insert_business_nodes

def fetch_business_data(query: str):
    """
    Fetch business data from Overpass API.
    
    Args:
        query: Overpass QL query string
        
    Returns:
        JSON response from Overpass API
    """
    return fetch_overpass_data(query)

def store_business_data(overpass_json):
    """
    Store business data from Overpass API response into the database.
    
    Args:
        overpass_json: JSON response from Overpass API
        
    Returns:
        Tuple of (inserted_count, skipped_count, updated_count)
    """
    return insert_business_nodes(overpass_json)

