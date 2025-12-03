from flask import Blueprint, jsonify, request
from utils.overpass_client import fetch_overpass_data
from utils.overpass_parser import insert_transit_nodes
from app.models import TransitNode

transit_bp = Blueprint("transit", __name__)

# Full Karnataka query (may take 1-2 minutes)
QUERY_FULL = """
[out:json][timeout:180];
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

# Smaller query for Bangalore city only (faster, ~30 seconds)
QUERY_BANGALORE = """
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

# Use smaller query by default to avoid timeouts
QUERY = QUERY_BANGALORE

@transit_bp.route("/load_transit", methods=["POST"])
def load_transit_data():
    """
    Load transit data from Overpass API into the database.
    Only calls API if database is empty (unless ?force=true is passed).
    """
    try:
        # Check if force parameter is provided
        force = request.args.get('force', 'false').lower() == 'true'
        
        # Check if data already exists
        existing_count = TransitNode.query.count()
        
        if existing_count > 0 and not force:
            return jsonify({
                "status": "skipped",
                "message": "Data already exists in database. API call skipped.",
                "existing_nodes": existing_count,
                "hint": "Add ?force=true to force reload"
            }), 200
        
        # Fetch data from Overpass API
        data = fetch_overpass_data(QUERY)
        inserted, skipped, updated = insert_transit_nodes(data)
        total = TransitNode.query.count()
        
        return jsonify({
            "status": "success", 
            "message": "Transit data loaded into Postgres",
            "inserted": inserted,
            "updated": updated,
            "skipped": skipped,
            "total_nodes": total
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@transit_bp.route("/all", methods=["GET"])
def get_transit_nodes():
    """Get all transit nodes from the database"""
    from app.models import TransitNode
    try:
        nodes = TransitNode.query.all()
        result = [
            {
                "id": node.id,
                "osm_id": node.osm_id,
                "type": node.type,
                "name": node.name,
                "latitude": node.latitude,
                "longitude": node.longitude
            } for node in nodes
        ]
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
