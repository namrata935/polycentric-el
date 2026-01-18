"""
Test script for micro-recommendation system
"""

import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.recommendation_service import MicroRecommendationEngine

def test_opportunity_zone_negative():
    """Test: Opportunity Zone with negative sentiment and poor transport"""
    
    zone = {
        'zone_lat': 12.95,
        'zone_lon': 77.70,
        'zone_type': 'Opportunity Zone',
        'business_count': 5,
        'transport_count': 0,
        'population': 1500,
        'adjusted_zone_score': 0.35,
        'business_raw_tags': [
            {'name': 'School', 'amenity': 'school'},
            {'name': 'Small Shop', 'amenity': 'shop'},
        ],
        'final_sentiment': {
            'mean': -0.42,
            'sources': ['accident_proxy', 'synthetic'],
            'source_breakdown': {
                'accident_proxy': {
                    'mean': 0.0,
                    'accident_count': 3,
                    'severity_breakdown': {'Simple Injury': 2, 'Damage': 1}
                },
                'synthetic': {
                    'mean': -0.38,
                    'num_feedbacks': 5
                }
            }
        }
    }
    
    engine = MicroRecommendationEngine()
    rec = engine.generate_recommendations(zone)
    
    print("=" * 70)
    print("TEST 1: Opportunity Zone with Negative Sentiment & Poor Transport")
    print("=" * 70)
    print(f"Zone Type: {rec['zone_type']}")
    print(f"Sentiment: {rec['sentiment_level']} ({rec['sentiment_score']})")
    print(f"Priority: {rec['priority']}")
    print(f"\nPrimary Recommendation:")
    print(f"  {rec['primary_recommendation']}")
    print(f"\nFocus Areas: {', '.join(rec['focus_areas'])}")
    print(f"Recommended Actions: {', '.join(rec['recommended_actions'])}")
    print()
    return rec

def test_balanced_zone_declining():
    """Test: Balanced Zone with very negative sentiment"""
    
    zone = {
        'zone_lat': 13.00,
        'zone_lon': 77.60,
        'zone_type': 'Balanced Zone',
        'business_count': 45,
        'transport_count': 3,
        'population': 3000,
        'adjusted_zone_score': 0.55,
        'business_raw_tags': [
            {'name': 'School', 'amenity': 'school'},
            {'name': 'Hospital', 'amenity': 'hospital'},
            {'name': 'Restaurant', 'amenity': 'restaurant'},
        ],
        'final_sentiment': {
            'mean': -0.68,
            'sources': ['accident_proxy'],
            'source_breakdown': {
                'accident_proxy': {
                    'mean': -0.68,
                    'accident_count': 15,
                    'severity_breakdown': {'Fatal': 2, 'Grievous Injury': 5, 'Simple Injury': 8}
                }
            }
        }
    }
    
    engine = MicroRecommendationEngine()
    rec = engine.generate_recommendations(zone)
    
    print("=" * 70)
    print("TEST 2: Balanced Zone with Very Negative Sentiment (Safety Crisis)")
    print("=" * 70)
    print(f"Zone Type: {rec['zone_type']}")
    print(f"Sentiment: {rec['sentiment_level']} ({rec['sentiment_score']})")
    print(f"Priority: {rec['priority']}")
    print(f"\nPrimary Recommendation:")
    print(f"  {rec['primary_recommendation']}")
    print(f"\nFocus Areas: {', '.join(rec['focus_areas'])}")
    print(f"Recommended Actions: {', '.join(rec['recommended_actions'])}")
    print(f"\nContext:")
    print(f"  Business Density: {rec['context']['business_density']}")
    print(f"  Transport Access: {rec['context']['transport_access']}")
    print(f"  Population Level: {rec['context']['population_level']}")
    print()
    return rec

def test_commercial_zone_thriving():
    """Test: Commercial Zone with positive sentiment"""
    
    zone = {
        'zone_lat': 12.92,
        'zone_lon': 77.62,
        'zone_type': 'Commercial Zone',
        'business_count': 150,
        'transport_count': 12,
        'population': 5000,
        'adjusted_zone_score': 0.85,
        'business_raw_tags': [
            {'name': 'Supermarket', 'amenity': 'supermarket'},
            {'name': 'Hospital', 'amenity': 'hospital'},
            {'name': 'Shopping Mall', 'amenity': 'mall'},
            {'name': 'School', 'amenity': 'school'},
            {'name': 'Bus Station', 'amenity': 'bus_station'},
        ],
        'final_sentiment': {
            'mean': 0.72,
            'sources': ['reddit_bangalore', 'accident_proxy'],
            'source_breakdown': {
                'reddit_bangalore': {'mean': 0.65},
                'accident_proxy': {'mean': 0.75, 'accident_count': 0}
            }
        }
    }
    
    engine = MicroRecommendationEngine()
    rec = engine.generate_recommendations(zone)
    
    print("=" * 70)
    print("TEST 3: Commercial Zone with Positive Sentiment")
    print("=" * 70)
    print(f"Zone Type: {rec['zone_type']}")
    print(f"Sentiment: {rec['sentiment_level']} ({rec['sentiment_score']})")
    print(f"Priority: {rec['priority']}")
    print(f"\nPrimary Recommendation:")
    print(f"  {rec['primary_recommendation']}")
    print(f"\nFocus Areas: {', '.join(rec['focus_areas'])}")
    print(f"Recommended Actions: {', '.join(rec['recommended_actions'])}")
    print(f"\nContext:")
    print(f"  Business Density: {rec['context']['business_density']}")
    print(f"  Transport Access: {rec['context']['transport_access']}")
    print(f"  Population Level: {rec['context']['population_level']}")
    print()
    return rec

def test_neutral_balanced_zone():
    """Test: Balanced Zone with neutral sentiment"""
    
    zone = {
        'zone_lat': 13.10,
        'zone_lon': 77.58,
        'zone_type': 'Balanced Zone',
        'business_count': 35,
        'transport_count': 2,
        'population': 2000,
        'adjusted_zone_score': 0.52,
        'business_raw_tags': [
            {'name': 'School', 'amenity': 'school'},
            {'name': 'Clinic', 'amenity': 'clinic'},
        ],
        'final_sentiment': {
            'mean': 0.05,
            'sources': ['synthetic'],
            'source_breakdown': {
                'synthetic': {'mean': 0.05}
            }
        }
    }
    
    engine = MicroRecommendationEngine()
    rec = engine.generate_recommendations(zone)
    
    print("=" * 70)
    print("TEST 4: Balanced Zone with Neutral Sentiment")
    print("=" * 70)
    print(f"Zone Type: {rec['zone_type']}")
    print(f"Sentiment: {rec['sentiment_level']} ({rec['sentiment_score']})")
    print(f"Priority: {rec['priority']}")
    print(f"\nPrimary Recommendation:")
    print(f"  {rec['primary_recommendation']}")
    print(f"\nFocus Areas: {', '.join(rec['focus_areas'])}")
    print(f"Recommended Actions: {', '.join(rec['recommended_actions'])}")
    print()
    return rec

if __name__ == '__main__':
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 12 + "MICRO-RECOMMENDATION SYSTEM TEST SUITE" + " " * 19 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\n")
    
    results = []
    
    try:
        results.append(test_opportunity_zone_negative())
        results.append(test_balanced_zone_declining())
        results.append(test_commercial_zone_thriving())
        results.append(test_neutral_balanced_zone())
        
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Total tests: 4")
        print(f"All tests passed ✓")
        print("\nPriority Distribution:")
        priority_counts = {}
        for rec in results:
            p = rec['priority']
            priority_counts[p] = priority_counts.get(p, 0) + 1
        for priority in ['critical', 'high', 'medium', 'low']:
            count = priority_counts.get(priority, 0)
            print(f"  {priority.upper()}: {count}")
        
    except Exception as e:
        print(f"\n✗ Test failed with error:")
        print(f"  {str(e)}")
        import traceback
        traceback.print_exc()
