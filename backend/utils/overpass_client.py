import requests
import time
from typing import Dict, Any

# Multiple Overpass API endpoints to try
OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.openstreetmap.ru/api/interpreter",
]

def fetch_overpass_data(query: str, timeout: int = 180) -> Dict[str, Any]:
    """
    Fetch data from Overpass API with retry logic and better error handling.
    
    Args:
        query: Overpass QL query string
        timeout: Request timeout in seconds (default 180 for large queries)
    
    Returns:
        JSON response from Overpass API
    
    Raises:
        Exception: If all API endpoints fail
    """
    last_error = None
    
    for url in OVERPASS_URLS:
        try:
            print(f"   Trying Overpass API: {url}")
            
            # Make request with timeout
            response = requests.post(
                url,
                data={"data": query},
                timeout=timeout,
                headers={
                    "User-Agent": "Polycentric-EL/1.0 (transit data loader)",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            
            # Check for HTTP errors
            response.raise_for_status()
            
            # Check if response is valid JSON
            try:
                data = response.json()
                
                # Check for Overpass API errors in response
                if "remark" in data:
                    print(f"   [WARNING] API remark: {data['remark']}")
                
                if "elements" in data:
                    print(f"   [OK] Success! Received {len(data['elements'])} elements")
                    return data
                else:
                    print(f"   [WARNING] Response missing 'elements' key")
                    # Still return the data, parser will handle empty elements
                    return data
                    
            except ValueError as e:
                print(f"   [ERROR] Invalid JSON response: {e}")
                print(f"   Response text (first 200 chars): {response.text[:200]}")
                last_error = f"Invalid JSON: {e}"
                continue
                
        except requests.exceptions.Timeout:
            print(f"   [ERROR] Timeout after {timeout} seconds")
            last_error = f"Request timeout after {timeout} seconds"
            continue
            
        except requests.exceptions.ConnectionError as e:
            print(f"   [ERROR] Connection error: {e}")
            last_error = f"Connection error: {e}"
            continue
            
        except requests.exceptions.HTTPError as e:
            print(f"   [ERROR] HTTP error: {e}")
            if hasattr(e.response, 'text'):
                print(f"   Response: {e.response.text[:200]}")
            last_error = f"HTTP {e.response.status_code}: {e}"
            continue
            
        except Exception as e:
            print(f"   [ERROR] Unexpected error: {e}")
            last_error = str(e)
            continue
    
    # If we get here, all endpoints failed
    raise Exception(
        f"All Overpass API endpoints failed. Last error: {last_error}\n"
        f"Tried endpoints: {', '.join(OVERPASS_URLS)}\n"
        f"Possible issues:\n"
        f"1. No internet connection\n"
        f"2. Overpass API servers are down\n"
        f"3. Query is too large (try reducing area or timeout)\n"
        f"4. Rate limiting (wait a few minutes and try again)"
    )
