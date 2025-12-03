"""
Simple script to check what's in the Postgres database.
Run this to verify data is actually in the database.
"""
from app import create_app, db
from app.models import TransitNode
from sqlalchemy import text

def check_database():
    """Check the database contents"""
    print("=" * 60)
    print("CHECKING POSTGRES DATABASE")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        # Method 1: Using SQLAlchemy ORM
        print("\n[Method 1] Using SQLAlchemy ORM:")
        try:
            count = TransitNode.query.count()
            print(f"   Total records: {count}")
            
            if count > 0:
                print("\n   First 5 records:")
                nodes = TransitNode.query.limit(5).all()
                for node in nodes:
                    print(f"   - ID: {node.id}")
                    print(f"     OSM ID: {node.osm_id}")
                    print(f"     Type: {node.type}")
                    print(f"     Name: {node.name}")
                    print(f"     Location: ({node.latitude}, {node.longitude})")
                    print()
            else:
                print("   ⚠️  No records found in database!")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Method 2: Using raw SQL
        print("\n[Method 2] Using raw SQL:")
        try:
            result = db.session.execute(text("SELECT COUNT(*) FROM transit_nodes"))
            sql_count = result.scalar()
            print(f"   Total records (SQL): {sql_count}")
            
            if sql_count > 0:
                result = db.session.execute(text("""
                    SELECT id, osm_id, type, name, latitude, longitude 
                    FROM transit_nodes 
                    LIMIT 5
                """))
                print("\n   First 5 records (SQL):")
                for row in result:
                    print(f"   - ID: {row[0]}, OSM_ID: {row[1]}, Type: {row[2]}")
                    print(f"     Name: {row[3]}, Location: ({row[4]}, {row[5]})")
                    print()
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Method 3: Check table structure
        print("\n[Method 3] Table structure:")
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = inspector.get_columns('transit_nodes')
            print("   Columns in transit_nodes table:")
            for col in columns:
                print(f"   - {col['name']}: {col['type']}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    check_database()

