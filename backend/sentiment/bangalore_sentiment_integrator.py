"""
Bangalore Sentiment Data Integrator
------------------------------------
Integrates your scraped Reddit sentiment data for Bangalore neighborhoods
with the multi-source sentiment framework.
"""

import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from pathlib import Path


# Bangalore neighborhood coordinates (approximate centers and bounds)
BANGALORE_NEIGHBORHOODS = {
    'Whitefield': {
        'center': (12.9698, 77.7499),
        'bounds': {'lat_min': 12.95, 'lat_max': 13.00, 'lon_min': 77.70, 'lon_max': 77.80}
    },
    'Koramangala': {
        'center': (12.9352, 77.6245),
        'bounds': {'lat_min': 12.92, 'lat_max': 12.95, 'lon_min': 77.60, 'lon_max': 77.65}
    },
    'HSR Layout': {
        'center': (12.9116, 77.6412),
        'bounds': {'lat_min': 12.90, 'lat_max': 12.93, 'lon_min': 77.62, 'lon_max': 77.66}
    },
    'Bellandur': {
        'center': (12.9259, 77.6787),
        'bounds': {'lat_min': 12.90, 'lat_max': 12.95, 'lon_min': 77.65, 'lon_max': 77.71}
    },
    'Indiranagar': {
        'center': (12.9716, 77.6412),
        'bounds': {'lat_min': 12.96, 'lat_max': 12.99, 'lon_min': 77.62, 'lon_max': 77.66}
    },
    'Marathahalli': {
        'center': (12.9591, 77.7012),
        'bounds': {'lat_min': 12.94, 'lat_max': 12.98, 'lon_min': 77.68, 'lon_max': 77.72}
    },
    'Electronic City': {
        'center': (12.8458, 77.6603),
        'bounds': {'lat_min': 12.82, 'lat_max': 12.87, 'lon_min': 77.64, 'lon_max': 77.69}
    },
    'Jayanagar': {
        'center': (12.9250, 77.5838),
        'bounds': {'lat_min': 12.91, 'lat_max': 12.94, 'lon_min': 77.56, 'lon_max': 77.60}
    },
    'Yelahanka': {
        'center': (13.1007, 77.5963),
        'bounds': {'lat_min': 13.08, 'lat_max': 13.13, 'lon_min': 77.57, 'lon_max': 77.62}
    }
}


def load_bangalore_sentiment(sentiment_file: str) -> Dict:
    """Load your scraped Bangalore sentiment data."""
    with open(sentiment_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def map_zone_to_neighborhood(zone_lat: float, zone_lon: float) -> Optional[str]:
    """
    Determine which Bangalore neighborhood a zone belongs to.
    
    Args:
        zone_lat, zone_lon: Zone coordinates
        
    Returns:
        Neighborhood name or None
    """
    for neighborhood, info in BANGALORE_NEIGHBORHOODS.items():
        bounds = info['bounds']
        if (bounds['lat_min'] <= zone_lat <= bounds['lat_max'] and
            bounds['lon_min'] <= zone_lon <= bounds['lon_max']):
            return neighborhood
    return None


def convert_scraped_to_sentiment(neighborhood_data: Dict) -> Dict[str, Any]:
    """
    Convert your scraped sentiment format to our standard format.
    
    Args:
        neighborhood_data: Data for one neighborhood from your scraped file
        
    Returns:
        Standardized sentiment dictionary
    """
    sentiment = neighborhood_data['sentiment']
    total = sentiment['total']
    
    if total == 0:
        return None
    
    positive = sentiment['positive']
    negative = sentiment['negative']
    neutral = sentiment['neutral']
    
    # Calculate mean sentiment score (-1 to +1)
    # More negative = lower score
    negative_pct = negative / total
    positive_pct = positive / total
    
    # Mean sentiment: weighted by proportions
    mean_sentiment = (positive_pct - negative_pct)
    
    # Calculate variance based on issue diversity
    issues = neighborhood_data.get('issues', {})
    issue_count = len(issues)
    std = 0.25 + (issue_count * 0.02)  # More issues = more variance
    
    return {
        'mean': round(float(mean_sentiment), 3),
        'std': round(float(std), 3),
        'positive_ratio': round(float(positive_pct), 3),
        'negative_ratio': round(float(negative_pct), 3),
        'neutral_ratio': round(float(neutral / total), 3),
        'num_feedbacks': int(total),
        'source': 'reddit_scraped',
        'neighborhood': None,  # Will be set later
        'top_issues': neighborhood_data.get('top_issues', []),
        'priority': neighborhood_data.get('priority', 'MEDIUM'),
        'negative_percentage': neighborhood_data.get('negative_percentage', 0)
    }


def integrate_bangalore_sentiment(zones_file: str, 
                                   bangalore_sentiment_file: str,
                                   output_file: str = 'output/zones_with_bangalore_sentiment.json'):
    """
    Integrate your scraped Bangalore sentiment with zones.
    
    Args:
        zones_file: Path to zones_classified.json
        bangalore_sentiment_file: Path to your scraped sentiment JSON
        output_file: Output path
    """
    # Load data
    print("="*70)
    print("BANGALORE SENTIMENT INTEGRATION")
    print("="*70)
    
    with open(zones_file, 'r', encoding='utf-8') as f:
        zones = json.load(f)
    print(f"\n✓ Loaded {len(zones)} zones")
    
    bangalore_sentiment = load_bangalore_sentiment(bangalore_sentiment_file)
    print(f"✓ Loaded sentiment for {len(bangalore_sentiment)} Bangalore neighborhoods")
    
    # Convert scraped data to standard format
    neighborhood_sentiments = {}
    for neighborhood, data in bangalore_sentiment.items():
        sentiment = convert_scraped_to_sentiment(data)
        if sentiment:
            sentiment['neighborhood'] = neighborhood
            neighborhood_sentiments[neighborhood] = sentiment
    
    print(f"\n✓ Converted {len(neighborhood_sentiments)} neighborhood sentiments")
    
    # Map zones to neighborhoods
    print(f"\nMapping zones to Bangalore neighborhoods...")
    
    matched_zones = 0
    enriched_zones = []
    
    for zone in zones:
        zone_lat = zone['zone_lat']
        zone_lon = zone['zone_lon']
        
        # Check if zone is in Bangalore
        neighborhood = map_zone_to_neighborhood(zone_lat, zone_lon)
        
        enriched_zone = zone.copy()
        
        if neighborhood and neighborhood in neighborhood_sentiments:
            # Zone is in a Bangalore neighborhood with sentiment data
            enriched_zone['bangalore_sentiment'] = neighborhood_sentiments[neighborhood]
            matched_zones += 1
        else:
            # Zone is not in Bangalore or no sentiment available
            enriched_zone['bangalore_sentiment'] = None
        
        enriched_zones.append(enriched_zone)
    
    # Save output
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(enriched_zones, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print(f"\n{'='*70}")
    print("INTEGRATION COMPLETE")
    print(f"{'='*70}")
    print(f"✓ Output saved to: {output_file}")
    print(f"\nCoverage:")
    print(f"  Zones with Bangalore sentiment: {matched_zones}/{len(zones)} ({matched_zones/len(zones)*100:.1f}%)")
    print(f"  Zones without sentiment: {len(zones) - matched_zones} ({(len(zones)-matched_zones)/len(zones)*100:.1f}%)")
    
    # Show neighborhood breakdown
    print(f"\n{'='*70}")
    print("NEIGHBORHOOD BREAKDOWN")
    print(f"{'='*70}")
    
    neighborhood_counts = {}
    for zone in enriched_zones:
        if zone['bangalore_sentiment']:
            neighborhood = zone['bangalore_sentiment']['neighborhood']
            neighborhood_counts[neighborhood] = neighborhood_counts.get(neighborhood, 0) + 1
    
    for neighborhood in sorted(neighborhood_counts.keys()):
        count = neighborhood_counts[neighborhood]
        sentiment_data = neighborhood_sentiments[neighborhood]
        mean = sentiment_data['mean']
        priority = sentiment_data['priority']
        
        print(f"\n  {neighborhood}:")
        print(f"    Zones: {count}")
        print(f"    Mean sentiment: {mean:.3f}")
        print(f"    Priority: {priority}")
        print(f"    Top issues: {', '.join(sentiment_data['top_issues'][:3])}")
    
    return enriched_zones


def show_sample_output(zones: List[Dict]):
    """Display sample zone with Bangalore sentiment."""
    print(f"\n{'='*70}")
    print("SAMPLE OUTPUT (Zone with Bangalore Sentiment)")
    print(f"{'='*70}")
    
    # Find a zone with sentiment
    sample = None
    for zone in zones:
        if zone['bangalore_sentiment'] is not None:
            sample = zone
            break
    
    if sample:
        print(f"\nZone: ({sample['zone_lat']}, {sample['zone_lon']})")
        print(f"Zone Type: {sample['zone_type']}")
        print(f"Business Count: {sample['business_count']}")
        print(f"Population: {sample['population']}")
        print(f"\nBangalore Sentiment:")
        print(json.dumps(sample['bangalore_sentiment'], indent=2))
    else:
        print("\nNo zones found with Bangalore sentiment data.")


def main():
    """Main execution."""
    zones_file = 'data/zones_classified.json'
    bangalore_sentiment_file = 'data/bangalore_sentiment.json'  # Your scraped file
    output_file = 'output/zones_with_bangalore_sentiment.json'
    
    # Check if files exist
    if not Path(zones_file).exists():
        print(f"\n✗ Error: {zones_file} not found!")
        return
    
    if not Path(bangalore_sentiment_file).exists():
        print(f"\n✗ Error: {bangalore_sentiment_file} not found!")
        print(f"  Please save your scraped sentiment data as: {bangalore_sentiment_file}\n")
        return
    
    # Integrate
    enriched_zones = integrate_bangalore_sentiment(
        zones_file=zones_file,
        bangalore_sentiment_file=bangalore_sentiment_file,
        output_file=output_file
    )
    
    # Show sample
    show_sample_output(enriched_zones)
    
    print(f"\n{'='*70}")
    print("NEXT STEPS")
    print(f"{'='*70}")
    print(f"\n1. Use this Bangalore sentiment data as your 'real community voice'")
    print(f"2. Combine with accident data for safety sentiment")
    print(f"3. Add synthetic sentiment for non-Bangalore zones")
    print(f"4. Run: python multi_source_sentiment_final.py")
    print(f"\n💡 TIP: Your scraped data covers ~{len(BANGALORE_NEIGHBORHOODS)} major Bangalore areas!")
    print(f"   This is excellent real sentiment data! 🎉\n")


if __name__ == '__main__':
    main()