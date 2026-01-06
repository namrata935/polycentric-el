"""
Test script to check Overpass API connectivity.
This helps diagnose connection issues.
"""
import sys
from utils.overpass_client import fetch_overpass_data

# Simple test query - just get a few bus stops in Bangalore
SIMPLE_QUERY = """
[out:json][timeout:60];
(
  node["highway"="bus_stop"](around:5000,12.9716,77.5946);
);
out body;
"""

# Even simpler query - just get one node
MINIMAL_QUERY = """
[out:json][timeout:5];
node(17327417);
out body;
"""

def test_overpass_connection():
    """Test Overpass API with different query sizes"""
    print("=" * 60)
    print("TESTING OVERPASS API CONNECTION")
    print("=" * 60)
    
    # Test 1: Minimal query (single node)
    print("\n[TEST 1] Minimal query (single known node)...")
    try:
        data = fetch_overpass_data(MINIMAL_QUERY)
        if "elements" in data and len(data["elements"]) > 0:
            print(f"✅ SUCCESS! Got {len(data['elements'])} element(s)")
            element = data["elements"][0]
            print(f"   Node ID: {element.get('id')}")
            print(f"   Type: {element.get('type')}")
            if 'tags' in element:
                print(f"   Tags: {list(element['tags'].keys())[:5]}")
        else:
            print("⚠️  Got response but no elements")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False
    
    # Test 2: Simple query (small area)
    print("\n[TEST 2] Simple query (10 bus stops near Bangalore)...")
    try:
        data = fetch_overpass_data(SIMPLE_QUERY)
        if "elements" in data:
            print(f"✅ SUCCESS! Got {len(data['elements'])} element(s)")
            if len(data['elements']) > 0:
                print("   Sample element:")
                el = data["elements"][0]
                print(f"   - ID: {el.get('id')}, Type: {el.get('type')}")
                if 'tags' in el:
                    tags = el['tags']
                    print(f"   - Highway: {tags.get('highway')}")
                    print(f"   - Name: {tags.get('name', 'N/A')}")
        else:
            print("⚠️  Got response but no elements")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        print("   This might indicate the API is working but query is too large")
    
    print("\n" + "=" * 60)
    print("If Test 1 passed, Overpass API is working!")
    print("If Test 2 failed, try using a smaller area or shorter timeout.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_overpass_connection()
    sys.exit(0 if success else 1)

