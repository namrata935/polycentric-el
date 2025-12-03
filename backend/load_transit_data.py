"""
Script to load transit data from Overpass API into the database.
Run this script to populate the transit_nodes table.
Only calls API if database is empty (unless --force flag is used).
"""
import sys
import argparse
from app import create_app, db
from utils.overpass_client import fetch_overpass_data
from utils.overpass_parser import insert_transit_nodes

# Overpass query for Bangalore city (faster than entire Karnataka)
QUERY = """
[out:json][timeout:60];
area["name"="Bangalore"]["admin_level"="8"]->.searchArea;
(
  node["highway"="bus_stop"](area.searchArea);
  node["railway"="subway_entrance"](area.searchArea);
  node["railway"="station"](area.searchArea);
);
out body;
limit 5000;
"""

def load_data(force=False):
    """Load transit data into the database"""
    print("=" * 50)
    print("Loading Transit Data")
    print("=" * 50)
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        try:
            from app.models import TransitNode
            
            # Check if data already exists
            existing_count = TransitNode.query.count()
            
            if existing_count > 0 and not force:
                print(f"[SKIP] Data already exists in database!")
                print(f"   Found {existing_count} transit nodes in database")
                print(f"   API call skipped to avoid unnecessary requests")
                print(f"\n   To force reload, run: python load_transit_data.py --force")
                print("=" * 50)
                return True
            
            if force and existing_count > 0:
                print(f"[FORCE] Reloading data (existing: {existing_count} nodes)...")
            
            print("[API] Fetching data from Overpass API...")
            print("   This may take a moment...")
            
            # Fetch data from Overpass API
            data = fetch_overpass_data(QUERY)
            
            element_count = len(data.get("elements", []))
            print(f"[OK] Received {element_count} elements from Overpass API")
            
            # Insert data into database
            print("[DB] Inserting data into database...")
            inserted, skipped, updated = insert_transit_nodes(data)
            
            # Count total records
            total_nodes = TransitNode.query.count()
            
            print(f"[OK] Successfully loaded transit data!")
            print(f"   New nodes inserted: {inserted}")
            print(f"   Existing nodes updated: {updated}")
            print(f"   Nodes skipped: {skipped}")
            print(f"   Total transit nodes in database: {total_nodes}")
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
    parser = argparse.ArgumentParser(description='Load transit data from Overpass API')
    parser.add_argument('--force', action='store_true', 
                       help='Force reload even if data already exists')
    args = parser.parse_args()
    
    success = load_data(force=args.force)
    sys.exit(0 if success else 1)

