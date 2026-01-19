"""
Flask API endpoint for sentiment analysis data
----------------------------------------------
Add this to your Flask backend to serve sentiment data to the frontend.
"""

from flask import Blueprint, jsonify, request
from pathlib import Path
import json

# Create blueprint
sentiment_bp = Blueprint('sentiment', __name__)

# Path to your sentiment analysis output
SENTIMENT_DATA_PATH = Path(__file__).parent.parent / 'sentiment' / 'output' / 'karnataka_sentiment_analysis.json'


@sentiment_bp.route('/api/sentiment-analysis', methods=['GET'])
def get_sentiment_analysis():
    """
    Get sentiment analysis for all zones or specific zones.
    
    Query parameters:
    - zone_id: Filter by specific zone ID
    - neighborhood: Filter by Bangalore neighborhood name
    - sentiment_category: Filter by category (very_positive, positive, neutral, negative, very_negative)
    - data_quality: Filter by quality (high, medium, low)
    - limit: Limit number of results (default: all)
    """
    try:
        # Load sentiment data
        with open(SENTIMENT_DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        zones = data.get('zones', [])
        
        # Apply filters if provided
        zone_id = request.args.get('zone_id')
        neighborhood = request.args.get('neighborhood')
        sentiment_category = request.args.get('sentiment_category')
        data_quality = request.args.get('data_quality')
        limit = request.args.get('limit', type=int)
        
        # Filter by zone_id
        if zone_id:
            zones = [z for z in zones if z['zone_id'] == zone_id]
        
        # Filter by neighborhood
        if neighborhood:
            zones = [z for z in zones 
                    if z['sentiment_analysis']['key_insights'].get('neighborhood') == neighborhood]
        
        # Filter by sentiment category
        if sentiment_category:
            zones = [z for z in zones 
                    if z['sentiment_analysis']['sentiment_category'] == sentiment_category]
        
        # Filter by data quality
        if data_quality:
            zones = [z for z in zones 
                    if z['sentiment_analysis']['data_quality'] == data_quality]
        
        # Apply limit
        if limit and limit > 0:
            zones = zones[:limit]
        
        return jsonify({
            'success': True,
            'total_zones': len(zones),
            'metadata': data.get('metadata', {}),
            'zones': zones
        })
    
    except FileNotFoundError:
        return jsonify({
            'success': False,
            'error': 'Sentiment analysis data not found. Please run the sentiment analysis pipeline first.'
        }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sentiment_bp.route('/api/sentiment-analysis/summary', methods=['GET'])
def get_sentiment_summary():
    """Get summary statistics for sentiment analysis."""
    try:
        # Load summary data
        summary_path = SENTIMENT_DATA_PATH.parent / 'sentiment_analysis_summary.json'
        
        with open(summary_path, 'r', encoding='utf-8') as f:
            summary = json.load(f)
        
        return jsonify({
            'success': True,
            'summary': summary
        })
    
    except FileNotFoundError:
        return jsonify({
            'success': False,
            'error': 'Summary data not found.'
        }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sentiment_bp.route('/api/sentiment-analysis/neighborhoods', methods=['GET'])
def get_bangalore_neighborhoods():
    """Get list of Bangalore neighborhoods with sentiment data."""
    try:
        with open(SENTIMENT_DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        zones = data.get('zones', [])
        
        # Extract unique neighborhoods
        neighborhoods = {}
        for zone in zones:
            neighborhood = zone['sentiment_analysis']['key_insights'].get('neighborhood')
            if neighborhood:
                if neighborhood not in neighborhoods:
                    neighborhoods[neighborhood] = {
                        'name': neighborhood,
                        'zone_count': 0,
                        'avg_sentiment': 0,
                        'avg_population': 0
                    }
                
                neighborhoods[neighborhood]['zone_count'] += 1
                neighborhoods[neighborhood]['avg_sentiment'] += zone['sentiment_analysis']['sentiment_score']
                neighborhoods[neighborhood]['avg_population'] += zone['zone_info']['population']
        
        # Calculate averages
        for name, data in neighborhoods.items():
            count = data['zone_count']
            data['avg_sentiment'] = round(data['avg_sentiment'] / count, 3)
            data['avg_population'] = int(data['avg_population'] / count)
        
        return jsonify({
            'success': True,
            'neighborhoods': list(neighborhoods.values())
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Register blueprint in your main Flask app:
# app.register_blueprint(sentiment_bp)