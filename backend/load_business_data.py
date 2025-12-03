"""
Script to load business data from Overpass API into the database.
Run this script to populate the businesses table.
Only calls API if database is empty (unless --force flag is used).
"""
import sys
import argparse
from app import create_app, db
from utils.overpass_client import fetch_overpass_data
from utils.overpass_parser import insert_business_nodes
from app.models import Business

# Overpass query for Karnataka businesses
QUERY = """
[out:json][timeout:120];
area["name"="Karnataka"]["boundary"="administrative"]["admin_level"="4"]->.searchArea;
(
  nwr["office"~"company|it|software|research"](area.searchArea);
  nwr["shop"~"supermarket|mall|convenience"](area.searchArea);
  nwr["amenity"~"restaurant|cafe|fast_food"](area.searchArea);
  nwr["amenity"~"clinic|hospital"](area.searchArea);
  nwr["amenity"~"school|college"](area.searchArea);
);
out center;
"""

def load_data(force=False):
    """Load business data into the database"""
    print("=" * 50)
    print("Loading Business Data")
    print("=" * 50)
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        try:
            # Check if data already exists
            existing_count = Business.query.count()
            
            if existing_count > 0 and not force:
                print(f"[SKIP] Data already exists in database!")
                print(f"   Found {existing_count} businesses in database")
                print(f"   API call skipped to avoid unnecessary requests")
                print(f"\n   To force reload, run: python load_business_data.py --force")
                print("=" * 50)
                return True
            
            if force and existing_count > 0:
                print(f"[FORCE] Reloading data (existing: {existing_count} businesses)...")
            
            print("[API] Fetching data from Overpass API...")
            print("   This may take a moment (up to 2 minutes)...")
            
            # Fetch data from Overpass API
            data = fetch_overpass_data(QUERY)
            
            element_count = len(data.get("elements", []))
            print(f"[OK] Received {element_count} elements from Overpass API")
            
            # Insert data into database
            print("[DB] Inserting data into database...")
            inserted, skipped, updated = insert_business_nodes(data)
            
            # Count total records
            total_businesses = Business.query.count()
            
            print(f"[OK] Successfully loaded business data!")
            print(f"   New businesses inserted: {inserted}")
            print(f"   Existing businesses updated: {updated}")
            print(f"   Elements skipped: {skipped}")
            print(f"   Total businesses in database: {total_businesses}")
            print("\n" + "=" * 50)
            return True
            
        except Exception as e:
            print(f"[ERROR] Error loading data: {str(e)}")
            print("\nTroubleshooting:")
            print("1. Check your internet connection")
            print("2. Verify Overpass API is accessible")
            print("3. Check database connection")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Load business data from Overpass API')
    parser.add_argument('--force', action='store_true', 
                       help='Force reload even if data already exists')
    args = parser.parse_args()
    
    success = load_data(force=args.force)
    sys.exit(0 if success else 1)

