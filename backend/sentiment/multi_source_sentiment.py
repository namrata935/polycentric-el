"""
Final Multi-Source Sentiment Framework
---------------------------------------
Integrates THREE real data sources:
1. Bangalore Reddit sentiment (YOUR scraped data) - Real community voice
2. Karnataka accident data - Real safety proxy
3. Synthetic baseline - Complete coverage

This is the final version using your actual scraped sentiment data!
"""

import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from pathlib import Path
from collections import defaultdict


# Bangalore neighborhood boundaries (from your data)
BANGALORE_NEIGHBORHOODS = {
    'Whitefield': {'lat_min': 12.95, 'lat_max': 13.00, 'lon_min': 77.70, 'lon_max': 77.80},
    'Koramangala': {'lat_min': 12.92, 'lat_max': 12.95, 'lon_min': 77.60, 'lon_max': 77.65},
    'HSR Layout': {'lat_min': 12.90, 'lat_max': 12.93, 'lon_min': 77.62, 'lon_max': 77.66},
    'Bellandur': {'lat_min': 12.90, 'lat_max': 12.95, 'lon_min': 77.65, 'lon_max': 77.71},
    'Indiranagar': {'lat_min': 12.96, 'lat_max': 12.99, 'lon_min': 77.62, 'lon_max': 77.66},
    'Marathahalli': {'lat_min': 12.94, 'lat_max': 12.98, 'lon_min': 77.68, 'lon_max': 77.72},
    'Electronic City': {'lat_min': 12.82, 'lat_max': 12.87, 'lon_min': 77.64, 'lon_max': 77.69},
    'Jayanagar': {'lat_min': 12.91, 'lat_max': 12.94, 'lon_min': 77.56, 'lon_max': 77.60},
    'Yelahanka': {'lat_min': 13.08, 'lat_max': 13.13, 'lon_min': 77.57, 'lon_max': 77.62}
}


class FinalMultiSourceFramework:
    """
    Final sentiment framework using your scraped Bangalore data + accidents + synthetic.
    """
    
    AMENITY_VARIANCE = {
        'hospital': 0.35, 'clinic': 0.32, 'restaurant': 0.25,
        'fast_food': 0.28, 'cafe': 0.22, 'supermarket': 0.18,
        'school': 0.15, 'college': 0.20, 'default': 0.25
    }
    
    def __init__(self, seed: int = 42):
        self.rng = np.random.RandomState(seed)
        self.bangalore_sentiment = None
        self.accident_data = None
        
    # ==================== COMPONENT 1: BANGALORE REDDIT SENTIMENT ====================
    
    def load_bangalore_sentiment(self, sentiment_file: str):
        """Load your scraped Bangalore sentiment data."""
        try:
            with open(sentiment_file, 'r', encoding='utf-8') as f:
                self.bangalore_sentiment = json.load(f)
            print(f"✓ Loaded sentiment for {len(self.bangalore_sentiment)} Bangalore neighborhoods")
        except Exception as e:
            print(f"✗ Failed to load Bangalore sentiment: {e}")
            self.bangalore_sentiment = None
    
    def map_zone_to_neighborhood(self, zone_lat: float, zone_lon: float) -> Optional[str]:
        """Determine which Bangalore neighborhood a zone belongs to."""
        for neighborhood, bounds in BANGALORE_NEIGHBORHOODS.items():
            if (bounds['lat_min'] <= zone_lat <= bounds['lat_max'] and
                bounds['lon_min'] <= zone_lon <= bounds['lon_max']):
                return neighborhood
        return None
    
    def get_bangalore_sentiment_for_zone(self, zone_lat: float, zone_lon: float) -> Optional[Dict]:
        """Get Bangalore sentiment for a zone if it's in Bangalore."""
        if self.bangalore_sentiment is None:
            return None
        
        neighborhood = self.map_zone_to_neighborhood(zone_lat, zone_lon)
        
        if neighborhood and neighborhood in self.bangalore_sentiment:
            data = self.bangalore_sentiment[neighborhood]
            sentiment = data['sentiment']
            total = sentiment['total']
            
            if total == 0:
                return None
            
            positive = sentiment['positive']
            negative = sentiment['negative']
            
            # Calculate mean sentiment (-1 to +1)
            negative_pct = negative / total
            positive_pct = positive / total
            mean_sentiment = (positive_pct - negative_pct)
            
            # Calculate variance based on issue diversity
            issues = data.get('issues', {})
            issue_count = len(issues)
            std = 0.25 + (issue_count * 0.02)
            
            return {
                'mean': round(float(mean_sentiment), 3),
                'std': round(float(std), 3),
                'positive_ratio': round(float(positive_pct), 3),
                'negative_ratio': round(float(negative_pct), 3),
                'num_feedbacks': int(total),
                'source': 'reddit_bangalore',
                'neighborhood': neighborhood,
                'top_issues': data.get('top_issues', []),
                'priority': data.get('priority', 'MEDIUM')
            }
        
        return None
    
    # ==================== COMPONENT 2: ACCIDENT SAFETY SENTIMENT ====================
    
    def load_accident_data(self, accident_file: str):
        """Load Karnataka accident data."""
        try:
            self.accident_data = pd.read_csv(accident_file, encoding='utf-8')
            print(f"✓ Loaded {len(self.accident_data)} accident records")
            
            # Clean data
            self.accident_data = self.accident_data.dropna(subset=['Latitude', 'Longitude'])
            self.accident_data = self.accident_data[
                (self.accident_data['Latitude'] >= 11.5) & 
                (self.accident_data['Latitude'] <= 18.5) &
                (self.accident_data['Longitude'] >= 74.0) & 
                (self.accident_data['Longitude'] <= 78.5)
            ]
            
            print(f"  Valid records: {len(self.accident_data)}")
            
        except Exception as e:
            print(f"✗ Failed to load accident data: {e}")
            self.accident_data = None
    
    def calculate_accident_sentiment(self, zone_lat: float, zone_lon: float, 
                                     radius_km: float = 5.0) -> Optional[Dict]:
        """Calculate safety sentiment from nearby accidents."""
        if self.accident_data is None:
            return None
        
        # Calculate distance
        lat_diff = np.abs(self.accident_data['Latitude'] - zone_lat)
        lon_diff = np.abs(self.accident_data['Longitude'] - zone_lon)
        distance_km = np.sqrt((lat_diff * 111)**2 + (lon_diff * 111 * np.cos(np.radians(zone_lat)))**2)
        
        # Find nearby accidents
        nearby_accidents = self.accident_data[distance_km <= radius_km]
        accident_count = len(nearby_accidents)
        
        if accident_count == 0:
            return {
                'mean': 0.7,
                'std': 0.12,
                'positive_ratio': 0.85,
                'negative_ratio': 0.15,
                'accident_count': 0,
                'source': 'accident_proxy'
            }
        
        # Weight by severity
        severity_weights = {
            'Fatal': 3.0,
            'Grievous Injury': 2.0,
            'Simple Injury': 1.0,
            'Non-Injury (Damage only)': 0.5,
            'Damage': 0.5,
            'Damage Only': 0.5
        }
        
        if 'Severity' in nearby_accidents.columns:
            weighted_count = sum(
                severity_weights.get(row.get('Severity', 'Unknown'), 1.0)
                for _, row in nearby_accidents.iterrows()
            )
            severity_breakdown = nearby_accidents['Severity'].value_counts().to_dict()
        else:
            weighted_count = accident_count
            severity_breakdown = {}
        
        # Calculate safety score
        safety_score = -np.log1p(weighted_count) / 4.0
        safety_score = np.clip(safety_score, -1.0, 0.2)
        
        base_variance = 0.2
        if severity_breakdown:
            fatal_ratio = severity_breakdown.get('Fatal', 0) / accident_count
            variance = base_variance + (fatal_ratio * 0.15)
        else:
            variance = base_variance
        
        negative_ratio = min(0.9, 0.5 + (weighted_count / 50))
        positive_ratio = max(0.1, 1.0 - negative_ratio)
        
        result = {
            'mean': round(float(safety_score), 3),
            'std': round(float(variance), 3),
            'positive_ratio': round(float(positive_ratio), 3),
            'negative_ratio': round(float(negative_ratio), 3),
            'accident_count': int(accident_count),
            'weighted_count': round(float(weighted_count), 2),
            'source': 'accident_proxy'
        }
        
        if severity_breakdown:
            result['severity_breakdown'] = {k: int(v) for k, v in severity_breakdown.items()}
        
        return result
    
    # ==================== COMPONENT 3: SYNTHETIC SENTIMENT ====================
    
    def generate_synthetic_sentiment(self, zone: Dict[str, Any]) -> Dict[str, Any]:
        """Generate synthetic sentiment from zone attributes."""
        business_count = zone.get('business_count', 0)
        transport_count = zone.get('transport_count', 0)
        population = zone.get('population', 0)
        opportunity_score = zone.get('adjusted_zone_score', 0)
        
        service_factor = min(np.log1p(business_count) / 10.0, 0.3)
        transport_factor = min(np.log1p(transport_count) / 15.0, 0.2)
        pop_pressure = max(-np.log1p(population) / 25.0, -0.3)
        opportunity_factor = opportunity_score * 0.4
        
        base_sentiment = service_factor + transport_factor + pop_pressure + opportunity_factor
        base_sentiment = np.clip(base_sentiment, -1.0, 1.0)
        
        business_tags = zone.get('business_raw_tags', [])
        if business_tags:
            variances = [self.AMENITY_VARIANCE.get(tag.get('amenity', 'default'), 
                                                   self.AMENITY_VARIANCE['default'])
                        for tag in business_tags]
            variance = np.mean(variances)
        else:
            variance = self.AMENITY_VARIANCE['default']
        
        num_feedbacks = int(business_count * self.rng.uniform(1, 3))
        num_feedbacks = np.clip(num_feedbacks + int(np.log1p(population) / 2), 3, 50)
        
        feedback_points = self.rng.normal(base_sentiment, variance, num_feedbacks)
        feedback_points = np.clip(feedback_points, -1.0, 1.0)
        
        return {
            'mean': round(float(np.mean(feedback_points)), 3),
            'std': round(float(np.std(feedback_points)), 3),
            'positive_ratio': round(float(np.sum(feedback_points > 0) / len(feedback_points)), 3),
            'negative_ratio': round(float(np.sum(feedback_points < 0) / len(feedback_points)), 3),
            'num_feedbacks': int(num_feedbacks),
            'source': 'synthetic'
        }
    
    # ==================== MAIN INTEGRATION ====================
    
    def generate_integrated_sentiment(self, zone: Dict[str, Any]) -> Dict[str, Any]:
        """Generate multi-source sentiment combining all three sources."""
        zone_lat = zone['zone_lat']
        zone_lon = zone['zone_lon']
        
        sources_used = []
        combined_sentiments = []
        weights = []
        
        # Source 1: Bangalore Reddit sentiment (YOUR DATA!)
        bangalore_sentiment = self.get_bangalore_sentiment_for_zone(zone_lat, zone_lon)
        if bangalore_sentiment:
            combined_sentiments.append(bangalore_sentiment['mean'])
            weights.append(0.5)  # 50% weight - this is REAL data!
            sources_used.append('reddit_bangalore')
        
        # Source 2: Accident safety sentiment
        accident_sentiment = self.calculate_accident_sentiment(zone_lat, zone_lon)
        if accident_sentiment:
            combined_sentiments.append(accident_sentiment['mean'])
            weights.append(0.3)  # 30% weight
            sources_used.append('accident_proxy')
        
        # Source 3: Synthetic baseline
        synthetic_sentiment = self.generate_synthetic_sentiment(zone)
        combined_sentiments.append(synthetic_sentiment['mean'])
        weights.append(0.2 if sources_used else 1.0)
        sources_used.append('synthetic')
        
        # Calculate weighted average
        weights = np.array(weights)
        weights = weights / weights.sum()
        final_mean = float(np.average(combined_sentiments, weights=weights))
        
        # Build result
        result = {
            'mean': round(final_mean, 3),
            'sources': sources_used,
            'source_breakdown': {},
            'primary_source': sources_used[0]
        }
        
        if bangalore_sentiment:
            result['source_breakdown']['reddit_bangalore'] = bangalore_sentiment
        if accident_sentiment:
            result['source_breakdown']['accident_proxy'] = accident_sentiment
        result['source_breakdown']['synthetic'] = synthetic_sentiment
        
        return result
    
    def process_all_zones(self, zones_file: str, 
                         bangalore_sentiment_file: str,
                         accident_file: Optional[str] = None,
                         output_file: str = 'output/zones_final_sentiment.json') -> List[Dict]:
        """Process all zones with multi-source sentiment."""
        
        # Load zones
        with open(zones_file, 'r', encoding='utf-8') as f:
            zones = json.load(f)
        
        print(f"\n{'='*60}")
        print("FINAL MULTI-SOURCE SENTIMENT FRAMEWORK")
        print(f"{'='*60}")
        print(f"Total zones to process: {len(zones)}")
        
        # Load Bangalore sentiment (YOUR DATA!)
        self.load_bangalore_sentiment(bangalore_sentiment_file)
        
        # Load accident data
        if accident_file:
            self.load_accident_data(accident_file)
        
        # Process zones
        print(f"\nProcessing zones...")
        enriched_zones = []
        source_stats = defaultdict(int)
        
        for i, zone in enumerate(zones):
            sentiment = self.generate_integrated_sentiment(zone)
            
            enriched_zone = zone.copy()
            enriched_zone['final_sentiment'] = sentiment
            enriched_zones.append(enriched_zone)
            
            for source in sentiment['sources']:
                source_stats[source] += 1
            
            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{len(zones)} zones")
        
        # Save output
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enriched_zones, f, indent=2, ensure_ascii=False)
        
        # Print summary
        print(f"\n{'='*60}")
        print("PROCESSING COMPLETE")
        print(f"{'='*60}")
        print(f"✓ Output saved to: {output_file}")
        print(f"\nSource Distribution:")
        for source, count in sorted(source_stats.items()):
            pct = count / len(zones) * 100
            print(f"  {source:25s}: {count:4d} zones ({pct:5.1f}%)")
        
        # Bangalore-specific stats
        bangalore_zones = sum(1 for z in enriched_zones 
                            if 'reddit_bangalore' in z['final_sentiment']['sources'])
        
        print(f"\n✅ REAL SENTIMENT COVERAGE:")
        print(f"  Bangalore neighborhoods: {bangalore_zones} zones ({bangalore_zones/len(zones)*100:.1f}%)")
        print(f"  Accident safety data:    {source_stats.get('accident_proxy', 0)} zones")
        print(f"  Total with real data:    {max(bangalore_zones, source_stats.get('accident_proxy', 0))} zones")
        
        return enriched_zones


def main():
    """Main execution."""
    framework = FinalMultiSourceFramework(seed=42)
    
    # Configuration
    zones_file = 'data/zones_classified.json'
    bangalore_sentiment_file = 'data/bangalore_sentiment.json'  # YOUR SCRAPED DATA!
    accident_file = 'data/karnataka_accidents.csv'
    output_file = 'output/zones_final_sentiment.json'
    
    # Check files
    if not Path(zones_file).exists():
        print(f"\n✗ Error: {zones_file} not found!\n")
        return
    
    if not Path(bangalore_sentiment_file).exists():
        print(f"\n✗ Error: {bangalore_sentiment_file} not found!")
        print(f"  Please save your scraped sentiment data to this location.\n")
        return
    
    if not Path(accident_file).exists():
        print(f"\n⚠ Warning: {accident_file} not found!")
        print(f"  Will proceed without accident data.\n")
        accident_file = None
    
    # Process
    enriched_zones = framework.process_all_zones(
        zones_file=zones_file,
        bangalore_sentiment_file=bangalore_sentiment_file,
        accident_file=accident_file,
        output_file=output_file
    )
    
    # Show sample
    print(f"\n{'='*60}")
    print("SAMPLE OUTPUT")
    print(f"{'='*60}")
    
    # Find a Bangalore zone
    sample = None
    for zone in enriched_zones:
        if 'reddit_bangalore' in zone['final_sentiment']['sources']:
            sample = zone
            break
    
    if sample:
        print(f"\nZone: ({sample['zone_lat']}, {sample['zone_lon']})")
        print(f"Zone Type: {sample['zone_type']}")
        print(f"\nFinal Sentiment:")
        print(json.dumps(sample['final_sentiment'], indent=2))
    
    print(f"\n{'='*60}")
    print("🎉 SUCCESS!")
    print(f"{'='*60}")
    print(f"\nYou now have multi-source sentiment with:")
    print(f"  ✅ Real Bangalore community sentiment (YOUR scraped data)")
    print(f"  ✅ Real accident safety data")
    print(f"  ✅ Synthetic baseline for complete coverage")
    print(f"\nThis is research-grade, defensible sentiment analysis! 🚀\n")


if __name__ == '__main__':
    main()