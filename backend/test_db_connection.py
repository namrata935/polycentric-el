"""
Database Connection Test Script
Run this script to test your database connection and verify the setup.
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test the database connection"""
    print("=" * 50)
    print("Database Connection Test")
    print("=" * 50)
    
    # Check if DATABASE_URL is set
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in environment variables")
        print("   Please create a .env file with DATABASE_URL")
        print("   Example: DATABASE_URL=postgresql://user:password@localhost:5432/dbname")
        return False
    
    print(f"✅ DATABASE_URL found: {database_url[:30]}...")
    
    # Try to import and test SQLAlchemy connection
    try:
        from app import create_app, db
        print("✅ Flask app and database imports successful")
        
        # Create app
        app = create_app()
        print("✅ Flask app created successfully")
        
        # Test database connection
        with app.app_context():
            try:
                # Try to execute a simple query
                db.session.execute(db.text("SELECT 1"))
                print("✅ Database connection successful!")
                
                # Check if tables exist
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                
                if tables:
                    print(f"✅ Found {len(tables)} table(s): {', '.join(tables)}")
                    
                    # Check if transit_nodes table exists
                    if 'transit_nodes' in tables:
                        print("✅ transit_nodes table exists")
                        
                        # Count records
                        from app.models import TransitNode
                        count = TransitNode.query.count()
                        print(f"✅ Found {count} transit node(s) in database")
                    else:
                        print("⚠️  transit_nodes table does not exist yet")
                        print("   Run: python -c 'from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()'")
                else:
                    print("⚠️  No tables found in database")
                    print("   Run: python -c 'from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()'")
                
                return True
                
            except Exception as e:
                print(f"❌ Database connection failed: {str(e)}")
                print("\nTroubleshooting:")
                print("1. Check if PostgreSQL is running")
                print("2. Verify DATABASE_URL is correct")
                print("3. Ensure database exists")
                print("4. Check user permissions")
                return False
                
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("   Make sure all dependencies are installed: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_flask_app():
    """Test if Flask app can start"""
    print("\n" + "=" * 50)
    print("Flask App Test")
    print("=" * 50)
    
    try:
        from app import create_app
        app = create_app()
        print("✅ Flask app created successfully")
        
        # Check registered routes
        with app.app_context():
            routes = []
            for rule in app.url_map.iter_rules():
                routes.append(f"{rule.rule} [{', '.join(rule.methods)}]")
            
            if routes:
                print(f"✅ Found {len(routes)} route(s):")
                for route in routes:
                    print(f"   - {route}")
            else:
                print("⚠️  No routes registered")
        
        return True
    except Exception as e:
        print(f"❌ Flask app test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n")
    db_ok = test_database_connection()
    app_ok = test_flask_app()
    
    print("\n" + "=" * 50)
    print("Summary")
    print("=" * 50)
    if db_ok and app_ok:
        print("✅ All tests passed! Your backend is ready to use.")
        print("\nTo start the server, run:")
        print("   python run.py")
        print("\nOr:")
        print("   cd backend")
        print("   python run.py")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

