"""
Test script to verify the parser handles Overpass JSON format correctly.
"""
import json
from app import create_app, db
from utils.overpass_parser import insert_transit_nodes

# Sample data matching the actual Overpass API format
SAMPLE_DATA = {
    "elements": [
        {
            "type": "node",
            "id": 17327417,
            "lat": 13.1023262,
            "lon": 77.5859726,
            "tags": {
                "alt_name": "Escorts Yalahanka Road",
                "highway": "bus_stop",
                "loc_name": "Escorts",
                "name": "Escorts Yelahanka Road",
                "name:en": "Escorts Yelahanka Road",
                "network": "BMTC",
                "operator": "BMTC",
                "public_transport": "platform"
            }
        },
        {
            "type": "node",
            "id": 12345678,
            "lat": 12.9716,
            "lon": 77.5946,
            "tags": {
                "railway": "station",
                "name": "Bangalore City Railway Station",
                "name:en": "Bangalore City Railway Station"
            }
        },
        {
            "type": "node",
            "id": 87654321,
            "lat": 12.9352,
            "lon": 77.6245,
            "tags": {
                "railway": "subway_entrance",
                "name": "MG Road Metro Station",
                "ref": "MG01"
            }
        }
    ]
}

def test_parser():
    """Test the parser with sample data"""
    print("=" * 50)
    print("Testing Overpass Parser")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        # Clear existing test data (optional - comment out if you want to keep data)
        # from app.models import TransitNode
        # TransitNode.query.filter(TransitNode.osm_id.in_(["17327417", "12345678", "87654321"])).delete()
        # db.session.commit()
        
        print("\n📥 Inserting sample data...")
        inserted, skipped = insert_transit_nodes(SAMPLE_DATA)
        
        print(f"✅ Inserted: {inserted} nodes")
        print(f"⚠️  Skipped: {skipped} nodes")
        
        # Verify the data
        from app.models import TransitNode
        
        print("\n📊 Verifying inserted data:")
        nodes = TransitNode.query.filter(
            TransitNode.osm_id.in_(["17327417", "12345678", "87654321"])
        ).all()
        
        for node in nodes:
            print(f"\n  Node ID: {node.id}")
            print(f"  OSM ID: {node.osm_id}")
            print(f"  Type: {node.type}")
            print(f"  Name: {node.name}")
            print(f"  Location: ({node.latitude}, {node.longitude})")
        
        print("\n" + "=" * 50)
        print("✅ Parser test completed!")
        print("=" * 50)

if __name__ == "__main__":
    test_parser()

