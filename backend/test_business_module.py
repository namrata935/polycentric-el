"""
Test script for Business Data Ingestion Module.
Tests database connection, model creation, and data loading.
"""
import sys
from app import create_app, db
from app.models import Business

def test_business_module():
    """Test the business module"""
    print("=" * 60)
    print("TESTING BUSINESS DATA MODULE")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        # Step 1: Check database connection
        print("\n[STEP 1] Checking database connection...")
        try:
            db.session.execute(db.text("SELECT 1"))
            print("[OK] Database connection: SUCCESS")
        except Exception as e:
            print(f"[ERROR] Database connection FAILED: {e}")
            return False
        
        # Step 2: Check if businesses table exists
        print("\n[STEP 2] Checking if businesses table exists...")
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            if 'businesses' in tables:
                print("[OK] Table 'businesses' exists")
                
                # Check table structure
                columns = inspector.get_columns('businesses')
                print(f"   Columns: {[col['name'] for col in columns]}")
            else:
                print("[WARNING] Table 'businesses' does NOT exist")
                print("   Creating table...")
                db.create_all()
                print("[OK] Table created")
        except Exception as e:
            print(f"[ERROR] Error checking table: {e}")
            return False
        
        # Step 3: Check current data
        print("\n[STEP 3] Checking current data in businesses table...")
        try:
            count = Business.query.count()
            print(f"   Current businesses in database: {count}")
            
            if count > 0:
                print("\n   Sample businesses:")
                sample = Business.query.limit(3).all()
                for biz in sample:
                    print(f"   - ID: {biz.id}")
                    print(f"     OSM ID: {biz.osm_id}")
                    print(f"     Name: {biz.name}")
                    print(f"     Category: {biz.category}")
                    print(f"     Location: ({biz.latitude}, {biz.longitude})")
                    print()
            else:
                print("   [INFO] No businesses in database yet")
                print("   Run: python load_business_data.py to load data")
        except Exception as e:
            print(f"[ERROR] Error querying table: {e}")
            return False
        
        # Step 4: Test model creation
        print("\n[STEP 4] Testing Business model...")
        try:
            # Try to create a test business (won't save, just test structure)
            test_business = Business(
                osm_id=999999999,
                name="Test Business",
                category="amenity",
                latitude=12.9716,
                longitude=77.5946,
                raw_tags={"test": "data"}
            )
            print("[OK] Business model structure is valid")
            print(f"   Sample: {test_business.name} ({test_business.category})")
        except Exception as e:
            print(f"[ERROR] Business model test FAILED: {e}")
            return False
        
        print("\n" + "=" * 60)
        print("TEST COMPLETE")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Load business data: python load_business_data.py")
        print("2. Test API endpoint: POST http://localhost:5000/business/load")
        print("3. Get all businesses: GET http://localhost:5000/business/all")
        return True

if __name__ == "__main__":
    success = test_business_module()
    sys.exit(0 if success else 1)

