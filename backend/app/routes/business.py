from flask import Blueprint, jsonify, request
from utils.overpass_client import fetch_overpass_data
from utils.overpass_parser import insert_business_nodes
from app.models import Business

business_bp = Blueprint("business", __name__)

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

@business_bp.route("/load", methods=["POST"])
def load_business_data():
    """
    Load business data from Overpass API into the database.
    Only calls API if database is empty (unless ?force=true is passed).
    """
    try:
        # Check if force parameter is provided
        force = request.args.get('force', 'false').lower() == 'true'
        
        # Check if data already exists
        existing_count = Business.query.count()
        
        if existing_count > 0 and not force:
            return jsonify({
                "status": "skipped",
                "message": "Business data already exists in database. API call skipped.",
                "existing_businesses": existing_count,
                "hint": "Add ?force=true to force reload"
            }), 200
        
        # Fetch data from Overpass API
        data = fetch_overpass_data(QUERY)
        inserted, skipped, updated = insert_business_nodes(data)
        total = Business.query.count()
        
        return jsonify({
            "status": "success", 
            "message": "Business data loaded into Postgres",
            "inserted": inserted,
            "updated": updated,
            "skipped": skipped,
            "total_businesses": total
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@business_bp.route("/all", methods=["GET"])
def get_all_businesses():
    """Get all businesses from the database"""
    try:
        businesses = Business.query.all()
        result = [
            {
                "id": str(business.id),
                "osm_id": business.osm_id,
                "name": business.name,
                "category": business.category,
                "latitude": business.latitude,
                "longitude": business.longitude,
                "raw_tags": business.raw_tags
            } for business in businesses
        ]
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

