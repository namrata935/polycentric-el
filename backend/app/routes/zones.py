from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from app.services.zone_service import get_zones_json

zones_bp = Blueprint("zones", __name__)


@zones_bp.route("/all", methods=["GET", "OPTIONS"])
@cross_origin(origins="*", methods=["GET", "OPTIONS"], allow_headers=["Content-Type"])
def get_all_zones():
    """Get all classified zones from the database"""
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    try:
        zones = get_zones_json()
        return jsonify({
            "status": "success",
            "zones": zones,
            "count": len(zones)
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@zones_bp.route("/summary", methods=["GET", "OPTIONS"])
@cross_origin(origins="*", methods=["GET", "OPTIONS"], allow_headers=["Content-Type"])
def get_zones_summary():
    """Get summary statistics of zones"""
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    try:
        from app.services.zone_service import get_zones_classified
        
        zones_df = get_zones_classified()
        
        if len(zones_df) == 0:
            return jsonify({
                "status": "success",
                "summary": {
                    "total_zones": 0,
                    "by_type": {},
                    "avg_scores": {}
                }
            })
        
        # Count by zone type
        type_counts = zones_df["zone_type"].value_counts().to_dict()
        
        # Average scores
        avg_scores = {
            "zone_score": float(zones_df["zone_score"].mean()),
            "pop_score": float(zones_df["pop_score"].mean()),
            "biz_score": float(zones_df["biz_score"].mean()),
            "trans_score": float(zones_df["trans_score"].mean())
        }
        
        return jsonify({
            "status": "success",
            "summary": {
                "total_zones": int(len(zones_df)),
                "by_type": type_counts,
                "avg_scores": avg_scores
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

