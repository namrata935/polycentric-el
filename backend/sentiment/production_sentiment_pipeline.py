import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from pathlib import Path
from collections import defaultdict
from datetime import datetime


# Bangalore neighborhood boundaries (from scraped data)
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


class ProductionSentimentPipeline:
    """
    Production-ready sentiment analysis for entire Karnataka.
    Designed for easy integration with recommendation systems.
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
        
    # ==================== DATA LOADING ====================
    
    def load_bangalore_sentiment(self, sentiment_file: str):
        """Load scraped Bangalore sentiment data."""
        try:
            with open(sentiment_file, 'r', encoding='utf-8') as f:
                self.bangalore_sentiment = json.load(f)
            print(f"✓ Loaded sentiment for {len(self.bangalore_sentiment)} Bangalore neighborhoods")
        except Exception as e:
            print(f"⚠ Warning: Could not load Bangalore sentiment: {e}")
            print(f"  Will proceed with accident + synthetic only")
            self.bangalore_sentiment = None
    
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
            print(f"⚠ Warning: Could not load accident data: {e}")
            print(f"  Will proceed with Bangalore + synthetic only")
            self.accident_data = None
    
    # ==================== SENTIMENT COMPONENTS ====================
    
    def map_zone_to_neighborhood(self, zone_lat: float, zone_lon: float) -> Optional[str]:
        """Determine which Bangalore neighborhood a zone belongs to."""
        for neighborhood, bounds in BANGALORE_NEIGHBORHOODS.items():
            if (bounds['lat_min'] <= zone_lat <= bounds['lat_max'] and
                bounds['lon_min'] <= zone_lon <= bounds['lon_max']):
                return neighborhood
        return None
    
    def get_bangalore_sentiment(self, zone_lat: float, zone_lon: float) -> Optional[Dict]:
        """Get Bangalore sentiment if zone is in Bangalore."""
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
            neutral = sentiment['neutral']
            
            # Calculate sentiment score
            positive_pct = positive / total
            negative_pct = negative / total
            neutral_pct = neutral / total
            mean_sentiment = (positive_pct - negative_pct)
            
            # Get issue data
            issues = data.get('issues', {})
            top_issues = data.get('top_issues', [])
            
            return {
                'sentiment_score': round(float(mean_sentiment), 3),
                'confidence': 'high',  # Real data = high confidence
                'positive_ratio': round(float(positive_pct), 3),
                'negative_ratio': round(float(negative_pct), 3),
                'neutral_ratio': round(float(neutral_pct), 3),
                'sample_size': int(total),
                'data_source': 'reddit_bangalore',
                'neighborhood': neighborhood,
                'top_issues': top_issues,
                'all_issues': issues,
                'priority_level': data.get('priority', 'MEDIUM')
            }
        
        return None
    
    def get_accident_sentiment(self, zone_lat: float, zone_lon: float) -> Optional[Dict]:
        """Calculate safety sentiment from accident data."""
        if self.accident_data is None:
            return None
        
        # Calculate distances
        lat_diff = np.abs(self.accident_data['Latitude'] - zone_lat)
        lon_diff = np.abs(self.accident_data['Longitude'] - zone_lon)
        distance_km = np.sqrt((lat_diff * 111)**2 + (lon_diff * 111 * np.cos(np.radians(zone_lat)))**2)
        
        nearby = self.accident_data[distance_km <= 5.0]
        accident_count = len(nearby)
        
        if accident_count == 0:
            return {
                'sentiment_score': 0.7,
                'confidence': 'medium',
                'accident_count': 0,
                'data_source': 'accident_safety',
                'interpretation': 'No accidents nearby - area appears safe'
            }
        
        # Weight by severity
        severity_weights = {
            'Fatal': 3.0, 'Grievous Injury': 2.0, 'Simple Injury': 1.0,
            'Non-Injury (Damage only)': 0.5, 'Damage': 0.5, 'Damage Only': 0.5
        }
        
        weighted_count = 0
        severity_breakdown = {}
        
        if 'Severity' in nearby.columns:
            for _, row in nearby.iterrows():
                severity = row.get('Severity', 'Unknown')
                weight = severity_weights.get(severity, 1.0)
                weighted_count += weight
                severity_breakdown[severity] = severity_breakdown.get(severity, 0) + 1
        else:
            weighted_count = accident_count
        
        # Calculate safety score
        safety_score = -np.log1p(weighted_count) / 4.0
        safety_score = np.clip(safety_score, -1.0, 0.2)
        
        # Interpretation
        if safety_score > 0:
            interpretation = "Relatively safe - few accidents"
        elif safety_score > -0.4:
            interpretation = "Moderate safety concerns"
        else:
            interpretation = "High accident frequency - safety issues"
        
        result = {
            'sentiment_score': round(float(safety_score), 3),
            'confidence': 'medium',
            'accident_count': int(accident_count),
            'weighted_accident_score': round(float(weighted_count), 2),
            'data_source': 'accident_safety',
            'interpretation': interpretation
        }
        
        if severity_breakdown:
            result['severity_breakdown'] = severity_breakdown
        
        return result
    
    def get_synthetic_sentiment(self, zone: Dict[str, Any]) -> Dict:
        """Generate synthetic sentiment from zone attributes."""
        business_count = zone.get('business_count', 0)
        transport_count = zone.get('transport_count', 0)
        population = zone.get('population', 0)
        opportunity_score = zone.get('adjusted_zone_score', 0)
        
        # Calculate factors
        service_factor = min(np.log1p(business_count) / 10.0, 0.3)
        transport_factor = min(np.log1p(transport_count) / 15.0, 0.2)
        pop_pressure = max(-np.log1p(population) / 25.0, -0.3)
        opportunity_factor = opportunity_score * 0.4
        
        base_sentiment = service_factor + transport_factor + pop_pressure + opportunity_factor
        base_sentiment = np.clip(base_sentiment, -1.0, 1.0)
        
        # Interpretation
        if base_sentiment > 0.3:
            interpretation = "Well-served area with good amenities"
        elif base_sentiment > 0:
            interpretation = "Adequate services, room for improvement"
        elif base_sentiment > -0.3:
            interpretation = "Underserved area, opportunity for development"
        else:
            interpretation = "Significant service gaps, high development need"
        
        return {
            'sentiment_score': round(float(base_sentiment), 3),
            'confidence': 'low',  # Synthetic = low confidence
            'data_source': 'model_based',
            'interpretation': interpretation,
            'factors': {
                'service_availability': round(float(service_factor), 3),
                'transport_access': round(float(transport_factor), 3),
                'population_pressure': round(float(pop_pressure), 3),
                'opportunity_score': round(float(opportunity_factor), 3)
            }
        }
    
    # ==================== MAIN INTEGRATION ====================
    
    def analyze_zone(self, zone: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate complete sentiment analysis for a single zone.
        
        Returns a clean, recommendation-ready sentiment object.
        """
        zone_lat = zone['zone_lat']
        zone_lon = zone['zone_lon']
        
        # Collect sentiment from all available sources
        bangalore_sent = self.get_bangalore_sentiment(zone_lat, zone_lon)
        accident_sent = self.get_accident_sentiment(zone_lat, zone_lon)
        synthetic_sent = self.get_synthetic_sentiment(zone)
        
        # Determine primary source and final score
        sources_available = []
        sentiment_scores = []
        weights = []
        
        if bangalore_sent:
            sources_available.append('reddit_bangalore')
            sentiment_scores.append(bangalore_sent['sentiment_score'])
            weights.append(0.5)  # 50% weight for real data
            primary_source = bangalore_sent
            data_quality = 'high'
        elif accident_sent:
            sources_available.append('accident_safety')
            sentiment_scores.append(accident_sent['sentiment_score'])
            weights.append(0.5)
            primary_source = accident_sent
            data_quality = 'medium'
        else:
            primary_source = synthetic_sent
            data_quality = 'low'
        
        # Always add accident if available
        if accident_sent and bangalore_sent:
            sources_available.append('accident_safety')
            sentiment_scores.append(accident_sent['sentiment_score'])
            weights.append(0.3)
        
        # Always add synthetic
        sources_available.append('model_based')
        sentiment_scores.append(synthetic_sent['sentiment_score'])
        weights.append(0.2 if len(sources_available) > 1 else 1.0)
        
        # Calculate weighted final score
        weights = np.array(weights)
        weights = weights / weights.sum()
        final_score = float(np.average(sentiment_scores, weights=weights))
        
        # Build clean output for recommendation system
        result = {
            # ===== CORE SENTIMENT =====
            'sentiment_score': round(final_score, 3),  # Range: -1 (very negative) to +1 (very positive)
            'sentiment_category': self._categorize_sentiment(final_score),
            'data_quality': data_quality,  # high/medium/low
            
            # ===== DATA SOURCES =====
            'sources_used': sources_available,
            'primary_source': primary_source['data_source'],
            
            # ===== DETAILED BREAKDOWN =====
            'source_details': {},
            
            # ===== KEY INSIGHTS (for recommendations) =====
            'key_insights': {
                'interpretation': primary_source.get('interpretation', 'No specific interpretation'),
                'top_issues': primary_source.get('top_issues', []),
                'priority_level': primary_source.get('priority_level', 'MEDIUM'),
                'neighborhood': primary_source.get('neighborhood', None)
            },
            
            # ===== METADATA =====
            'analysis_timestamp': datetime.now().isoformat(),
            'version': '1.0'
        }
        
        # Add detailed source data
        if bangalore_sent:
            result['source_details']['reddit_bangalore'] = bangalore_sent
        if accident_sent:
            result['source_details']['accident_safety'] = accident_sent
        result['source_details']['model_based'] = synthetic_sent
        
        return result
    
    def _categorize_sentiment(self, score: float) -> str:
        """Categorize sentiment score for easy filtering."""
        if score >= 0.5:
            return 'very_positive'
        elif score >= 0.2:
            return 'positive'
        elif score >= -0.2:
            return 'neutral'
        elif score >= -0.5:
            return 'negative'
        else:
            return 'very_negative'
    
    # ==================== BATCH PROCESSING ====================
    
    def process_all_zones(self, 
                         zones_file: str,
                         bangalore_sentiment_file: Optional[str] = None,
                         accident_file: Optional[str] = None,
                         output_file: str = 'output/karnataka_sentiment_analysis.json',
                         summary_file: str = 'output/sentiment_analysis_summary.json'):
        """
        Process all Karnataka zones and generate production output.
        """
        
        print("\n" + "="*70)
        print("KARNATAKA SENTIMENT ANALYSIS - PRODUCTION PIPELINE")
        print("="*70)
        
        # Load zones
        with open(zones_file, 'r', encoding='utf-8') as f:
            zones = json.load(f)
        print(f"\n✓ Loaded {len(zones)} zones from {Path(zones_file).name}")
        
        # Load data sources
        if bangalore_sentiment_file:
            self.load_bangalore_sentiment(bangalore_sentiment_file)
        
        if accident_file:
            self.load_accident_data(accident_file)
        
        # Process zones
        print(f"\nProcessing zones...")
        results = []
        stats = defaultdict(int)
        
        for i, zone in enumerate(zones):
            # Analyze zone
            sentiment = self.analyze_zone(zone)
            
            # Combine with zone data
            zone_result = {
                'zone_id': f"zone_{i+1}",
                'location': {
                    'latitude': zone['zone_lat'],
                    'longitude': zone['zone_lon']
                },
                'zone_info': {
                    'zone_type': zone['zone_type'],
                    'business_count': zone['business_count'],
                    'transport_count': zone['transport_count'],
                    'population': zone['population'],
                    'opportunity_score': zone['adjusted_zone_score']
                },
                'sentiment_analysis': sentiment
            }
            
            results.append(zone_result)
            
            # Track statistics
            stats[sentiment['data_quality']] += 1
            stats[sentiment['sentiment_category']] += 1
            for source in sentiment['sources_used']:
                stats[f'source_{source}'] += 1
            
            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{len(zones)} zones")
        
        # Save main output
        output_data = {
            'metadata': {
                'total_zones': len(zones),
                'analysis_date': datetime.now().isoformat(),
                'version': '1.0',
                'description': 'Sentiment analysis for Karnataka zones - ready for recommendation system integration'
            },
            'zones': results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        # Generate summary
        summary = self._generate_summary(results, stats)
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # Print results
        self._print_results(len(zones), stats, output_file, summary_file)
        
        return results
    
    def _generate_summary(self, results: List[Dict], stats: Dict) -> Dict:
        """Generate summary statistics."""
        total = len(results)
        
        # Sentiment distribution
        sentiment_dist = {
            'very_positive': stats.get('very_positive', 0),
            'positive': stats.get('positive', 0),
            'neutral': stats.get('neutral', 0),
            'negative': stats.get('negative', 0),
            'very_negative': stats.get('very_negative', 0)
        }
        
        # Data quality
        quality_dist = {
            'high': stats.get('high', 0),
            'medium': stats.get('medium', 0),
            'low': stats.get('low', 0)
        }
        
        # Source usage
        source_dist = {
            'reddit_bangalore': stats.get('source_reddit_bangalore', 0),
            'accident_safety': stats.get('source_accident_safety', 0),
            'model_based': stats.get('source_model_based', 0)
        }
        
        return {
            'total_zones_analyzed': total,
            'sentiment_distribution': sentiment_dist,
            'data_quality_distribution': quality_dist,
            'source_distribution': source_dist,
            'coverage_statistics': {
                'real_community_feedback': f"{source_dist['reddit_bangalore']/total*100:.1f}%",
                'safety_data_coverage': f"{source_dist['accident_safety']/total*100:.1f}%",
                'high_quality_data': f"{quality_dist['high']/total*100:.1f}%"
            }
        }
    
    def _print_results(self, total: int, stats: Dict, output_file: str, summary_file: str):
        """Print processing results."""
        print(f"\n{'='*70}")
        print("PROCESSING COMPLETE")
        print(f"{'='*70}")
        print(f"\n✓ Output saved to: {output_file}")
        print(f"✓ Summary saved to: {summary_file}")
        
        print(f"\n{'='*70}")
        print("SENTIMENT DISTRIBUTION")
        print(f"{'='*70}")
        for category in ['very_positive', 'positive', 'neutral', 'negative', 'very_negative']:
            count = stats.get(category, 0)
            pct = count / total * 100
            print(f"  {category:20s}: {count:4d} zones ({pct:5.1f}%)")
        
        print(f"\n{'='*70}")
        print("DATA QUALITY")
        print(f"{'='*70}")
        for quality in ['high', 'medium', 'low']:
            count = stats.get(quality, 0)
            pct = count / total * 100
            print(f"  {quality:20s}: {count:4d} zones ({pct:5.1f}%)")
        
        print(f"\n{'='*70}")
        print("DATA SOURCES")
        print(f"{'='*70}")
        reddit = stats.get('source_reddit_bangalore', 0)
        accident = stats.get('source_accident_safety', 0)
        synthetic = stats.get('source_model_based', 0)
        
        print(f"  Reddit (Bangalore):  {reddit:4d} zones ({reddit/total*100:5.1f}%)")
        print(f"  Accident Safety:     {accident:4d} zones ({accident/total*100:5.1f}%)")
        print(f"  Model-Based:         {synthetic:4d} zones ({synthetic/total*100:5.1f}%)")
        
        print(f"\n{'='*70}")
        print("READY FOR RECOMMENDATION SYSTEM")
        print(f"{'='*70}")
        print(f"\n  The recommendation team can now use:")
        print(f"  • sentiment_score: Overall sentiment (-1 to +1)")
        print(f"  • sentiment_category: Easy filtering (very_positive/positive/etc)")
        print(f"  • top_issues: Key community concerns")
        print(f"  • data_quality: Confidence level (high/medium/low)")
        print(f"\n  Example usage:")
        print(f"    if zone.sentiment_score < -0.3 and 'roads' in zone.top_issues:")
        print(f"        recommend('road-side services')")
        print(f"\n{'='*70}\n")


def main():
    """Main execution."""
    pipeline = ProductionSentimentPipeline(seed=42)
    
    # File paths
    zones_file = 'data/zones_classified.json'
    bangalore_sentiment_file = 'data/bangalore_sentiment.json'
    accident_file = 'data/karnataka_accidents.csv'
    output_file = 'output/karnataka_sentiment_analysis.json'
    summary_file = 'output/sentiment_analysis_summary.json'
    
    # Check required files
    if not Path(zones_file).exists():
        print(f"\n✗ Error: {zones_file} not found!\n")
        return
    
    # Optional files
    if not Path(bangalore_sentiment_file).exists():
        print(f"\n⚠ Note: Bangalore sentiment file not found")
        print(f"  Will proceed with accident + synthetic only\n")
        bangalore_sentiment_file = None
    
    if not Path(accident_file).exists():
        print(f"\n⚠ Note: Accident file not found")
        print(f"  Will proceed with Bangalore + synthetic only\n")
        accident_file = None
    
    # Process
    results = pipeline.process_all_zones(
        zones_file=zones_file,
        bangalore_sentiment_file=bangalore_sentiment_file,
        accident_file=accident_file,
        output_file=output_file,
        summary_file=summary_file
    )
    
    # Show sample
    print("SAMPLE OUTPUT FOR RECOMMENDATION TEAM:")
    print("="*70)
    print(json.dumps(results[0], indent=2))
    print("="*70)


if __name__ == '__main__':
    main()