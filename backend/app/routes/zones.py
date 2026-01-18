from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from app.services.zone_service import get_zones_json
from app.services.recommendation_service import get_zone_recommendations

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


@zones_bp.route("/recommendations", methods=["POST", "OPTIONS"])
@cross_origin(origins="*", methods=["POST", "OPTIONS"], allow_headers=["Content-Type"])
def get_recommendations():
    """Get micro-recommendations for a zone based on sentiment and type"""
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No zone data provided"
            }), 400
        
        # Generate recommendation
        recommendation = get_zone_recommendations(data)
        
        return jsonify({
            "status": "success",
            "recommendation": recommendation
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@zones_bp.route("/recommendations/batch", methods=["POST", "OPTIONS"])
@cross_origin(origins="*", methods=["POST", "OPTIONS"], allow_headers=["Content-Type"])
def get_batch_recommendations():
    """Get recommendations for multiple zones"""
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    try:
        data = request.get_json()
        zones = data.get('zones', []) if isinstance(data, dict) else data
        
        if not isinstance(zones, list):
            return jsonify({
                "status": "error",
                "message": "Expected list of zones"
            }), 400
        
        # Generate recommendations for all zones
        recommendations = [get_zone_recommendations(zone) for zone in zones]
        
        # Group by priority
        by_priority = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        for rec in recommendations:
            priority = rec.get('priority', 'medium')
            by_priority[priority].append(rec)
        
        return jsonify({
            "status": "success",
            "total_zones": len(zones),
            "recommendations": recommendations,
            "by_priority": by_priority,
            "summary": {
                "critical": len(by_priority['critical']),
                "high": len(by_priority['high']),
                "medium": len(by_priority['medium']),
                "low": len(by_priority['low'])
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

