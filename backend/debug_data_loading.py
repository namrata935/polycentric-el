"""
Debug script to check why data isn't appearing in Postgres.
This will help identify where the issue is in the data loading process.
"""
import sys
from app import create_app, db
from utils.overpass_client import fetch_overpass_data
from utils.overpass_parser import insert_transit_nodes
from app.models import TransitNode

QUERY = """
[out:json][timeout:25];
area["name"="Karnataka"]["boundary"="administrative"]["admin_level"="4"]->.searchArea;
(
  node["highway"="bus_stop"](area.searchArea);
  node["railway"="subway_entrance"](area.searchArea);
  node["railway"="station"](area.searchArea);
);
out body;
>;
out skel qt;
"""

def debug_data_loading():
    """Debug the entire data loading process"""
    print("=" * 60)
    print("DEBUGGING DATA LOADING PROCESS")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        # Step 1: Check database connection
        print("\n[STEP 1] Checking database connection...")
        try:
            db.session.execute(db.text("SELECT 1"))
            print("✅ Database connection: OK")
        except Exception as e:
            print(f"❌ Database connection FAILED: {e}")
            return False
        
        # Step 2: Check if table exists
        print("\n[STEP 2] Checking if transit_nodes table exists...")
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            if 'transit_nodes' in tables:
                print("✅ Table 'transit_nodes' exists")
            else:
                print("❌ Table 'transit_nodes' does NOT exist")
                print("   Creating table...")
                db.create_all()
                print("✅ Table created")
        except Exception as e:
            print(f"❌ Error checking table: {e}")
            return False
        
        # Step 3: Check current data count
        print("\n[STEP 3] Checking current data in table...")
        try:
            current_count = TransitNode.query.count()
            print(f"   Current records in table: {current_count}")
            
            if current_count > 0:
                print("\n   Sample records:")
                sample = TransitNode.query.limit(3).all()
                for node in sample:
                    print(f"   - ID: {node.id}, OSM_ID: {node.osm_id}, Type: {node.type}, Name: {node.name}")
        except Exception as e:
            print(f"❌ Error querying table: {e}")
            return False
        
        # Step 4: Test Overpass API connection
        print("\n[STEP 4] Testing Overpass API connection...")
        try:
            print("   Fetching data from Overpass API (this may take 30-60 seconds)...")
            data = fetch_overpass_data(QUERY)
            element_count = len(data.get("elements", []))
            print(f"✅ Overpass API: OK - Received {element_count} elements")
            
            if element_count == 0:
                print("⚠️  WARNING: No elements returned from Overpass API!")
                print("   This could mean:")
                print("   - Query didn't match any nodes")
                print("   - Overpass API returned empty result")
                return False
            
            # Show sample of first element
            if element_count > 0:
                first_element = data["elements"][0]
                print(f"\n   Sample element:")
                print(f"   - Type: {first_element.get('type')}")
                print(f"   - ID: {first_element.get('id')}")
                print(f"   - Has lat/lon: {first_element.get('lat') is not None}/{first_element.get('lon') is not None}")
                if 'tags' in first_element:
                    tags = first_element['tags']
                    print(f"   - Tags: {list(tags.keys())[:5]}...")
                    if 'highway' in tags:
                        print(f"   - Highway: {tags['highway']}")
                    if 'railway' in tags:
                        print(f"   - Railway: {tags['railway']}")
        except Exception as e:
            print(f"❌ Overpass API FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Step 5: Test parsing and insertion
        print("\n[STEP 5] Testing data parsing and insertion...")
        try:
            print("   Parsing and inserting data...")
            inserted, skipped, updated = insert_transit_nodes(data)
            print(f"✅ Parsing complete:")
            print(f"   - Inserted: {inserted} nodes")
            print(f"   - Updated: {updated} nodes")
            print(f"   - Skipped: {skipped} nodes")
            
            if inserted == 0 and updated == 0 and skipped > 0:
                print("\n⚠️  WARNING: No nodes were inserted, but some were skipped!")
                print("   This usually means:")
                print("   - Nodes don't have valid transit_type (bus_stop, railway_station, subway_entrance)")
                print("   - Nodes are missing lat/lon coordinates")
                print("   - All nodes already exist in database")
            
            # Verify data was actually inserted
            new_count = TransitNode.query.count()
            print(f"\n   Records before: {current_count}")
            print(f"   Records after: {new_count}")
            print(f"   Difference: {new_count - current_count}")
            
            if new_count > current_count:
                print("✅ Data successfully inserted into database!")
            elif inserted > 0:
                print("⚠️  Data was marked as inserted but count didn't increase!")
                print("   This might indicate a transaction issue.")
            else:
                print("⚠️  No new data was inserted.")
                
        except Exception as e:
            print(f"❌ Parsing/Insertion FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Step 6: Verify data in database
        print("\n[STEP 6] Verifying data in database...")
        try:
            final_count = TransitNode.query.count()
            print(f"   Total records: {final_count}")
            
            if final_count > 0:
                print("\n   Latest records:")
                latest = TransitNode.query.order_by(TransitNode.id.desc()).limit(5).all()
                for node in latest:
                    print(f"   - ID: {node.id}, OSM_ID: {node.osm_id}, Type: {node.type}, Name: {node.name}")
                    print(f"     Location: ({node.latitude}, {node.longitude})")
            
            # Test direct SQL query
            print("\n   Testing direct SQL query...")
            result = db.session.execute(db.text("SELECT COUNT(*) FROM transit_nodes"))
            sql_count = result.scalar()
            print(f"   SQL COUNT result: {sql_count}")
            
            if sql_count != final_count:
                print("⚠️  WARNING: SQLAlchemy count doesn't match SQL count!")
                print("   This might indicate a transaction/commit issue.")
            
        except Exception as e:
            print(f"❌ Verification FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n" + "=" * 60)
        print("DEBUG COMPLETE")
        print("=" * 60)
        return True

if __name__ == "__main__":
    success = debug_data_loading()
    sys.exit(0 if success else 1)

