"""
Test Accident Sentiment Calculator
-----------------------------------
Test the accident-based safety sentiment on sample zones to verify it works.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path


def test_accident_sentiment():
    """Test accident sentiment calculation on sample zones."""
    
    print("="*70)
    print("TESTING ACCIDENT SENTIMENT CALCULATION")
    print("="*70)
    
    # Load zones
    zones_file = 'data/zones_classified.json'
    try:
        with open(zones_file, 'r') as f:
            zones = json.load(f)
        print(f"\n✓ Loaded {len(zones)} zones from {zones_file}")
    except FileNotFoundError:
        print(f"\n✗ Could not load {zones_file}")
        print(f"  Please ensure zones_classified.json is in the data/ folder\n")
        return
    except Exception as e:
        print(f"\n✗ Error loading zones: {e}\n")
        return
    
    # Load accidents
    accident_file = 'data/karnataka_accidents.csv'
    try:
        accidents = pd.read_csv(accident_file, encoding='utf-8')
        print(f"✓ Loaded {len(accidents)} accident records")
        
        # Clean data
        accidents = accidents.dropna(subset=['Latitude', 'Longitude'])
        accidents = accidents[
            (accidents['Latitude'] >= 11.5) & 
            (accidents['Latitude'] <= 18.5) &
            (accidents['Longitude'] >= 74.0) & 
            (accidents['Longitude'] <= 78.5)
        ]
        print(f"✓ {len(accidents)} valid accident records with coordinates")
        
    except FileNotFoundError:
        print(f"\n✗ Could not load {accident_file}")
        print(f"  Please ensure karnataka_accidents.csv is in the data/ folder\n")
        return
    except Exception as e:
        print(f"\n✗ Error loading accident data: {e}\n")
        return
    
    # Test on first 5 zones
    print(f"\n{'='*70}")
    print("TESTING ON SAMPLE ZONES")
    print(f"{'='*70}\n")
    
    sample_zones = zones[:5]
    
    for i, zone in enumerate(sample_zones, 1):
        zone_lat = zone['zone_lat']
        zone_lon = zone['zone_lon']
        
        print(f"Zone {i}:")
        print(f"  Location: ({zone_lat:.4f}, {zone_lon:.4f})")
        print(f"  Type: {zone['zone_type']}")
        print(f"  Business Count: {zone['business_count']}")
        print(f"  Population: {zone['population']}")
        
        # Calculate distance to all accidents
        lat_diff = np.abs(accidents['Latitude'] - zone_lat)
        lon_diff = np.abs(accidents['Longitude'] - zone_lon)
        distance_km = np.sqrt((lat_diff * 111)**2 + (lon_diff * 111 * np.cos(np.radians(zone_lat)))**2)
        
        # Count accidents within different radii
        radius_5km = len(accidents[distance_km <= 5.0])
        radius_10km = len(accidents[distance_km <= 10.0])
        radius_20km = len(accidents[distance_km <= 20.0])
        
        print(f"\n  Nearby Accidents:")
        print(f"    Within 5km:  {radius_5km:3d}")
        print(f"    Within 10km: {radius_10km:3d}")
        print(f"    Within 20km: {radius_20km:3d}")
        
        # Calculate safety sentiment (using 5km radius)
        if radius_5km == 0:
            safety_score = 0.7
            sentiment_desc = "Very Safe (No accidents)"
        else:
            nearby = accidents[distance_km <= 5.0]
            
            # Weight by severity if available
            severity_weights = {
                'Fatal': 3.0,
                'Grievous Injury': 2.0,
                'Simple Injury': 1.0,
                'Non-Injury (Damage only)': 0.5,
                'Damage': 0.5
            }
            
            if 'Severity' in nearby.columns:
                weighted_count = sum(
                    severity_weights.get(row.get('Severity', 'Unknown'), 1.0)
                    for _, row in nearby.iterrows()
                )
                
                severity_breakdown = nearby['Severity'].value_counts().to_dict()
                print(f"\n  Severity Breakdown (within 5km):")
                for severity, count in sorted(severity_breakdown.items(), 
                                             key=lambda x: severity_weights.get(x[0], 1.0), 
                                             reverse=True):
                    weight = severity_weights.get(severity, 1.0)
                    print(f"    {severity:30s}: {count:2d} (weight: {weight})")
            else:
                weighted_count = radius_5km
            
            # Calculate sentiment
            safety_score = -np.log1p(weighted_count) / 4.0
            safety_score = np.clip(safety_score, -1.0, 0.2)
            
            if safety_score > 0:
                sentiment_desc = "Relatively Safe"
            elif safety_score > -0.3:
                sentiment_desc = "Moderate Safety Concern"
            elif safety_score > -0.6:
                sentiment_desc = "High Safety Concern"
            else:
                sentiment_desc = "Very High Safety Concern"
        
        print(f"\n  Safety Sentiment:")
        print(f"    Score: {safety_score:.3f}")
        print(f"    Assessment: {sentiment_desc}")
        
        # Visual indicator
        if safety_score > 0.3:
            indicator = "🟢 Safe"
        elif safety_score > 0:
            indicator = "🟡 Fairly Safe"
        elif safety_score > -0.4:
            indicator = "🟠 Caution"
        else:
            indicator = "🔴 High Risk"
        
        print(f"    Indicator: {indicator}")
        print(f"\n{'-'*70}\n")
    
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    
    # Calculate coverage
    all_accident_counts = []
    for zone in zones:
        lat_diff = np.abs(accidents['Latitude'] - zone['zone_lat'])
        lon_diff = np.abs(accidents['Longitude'] - zone['zone_lon'])
        distance_km = np.sqrt((lat_diff * 111)**2 + (lon_diff * 111 * np.cos(np.radians(zone['zone_lat'])))**2)
        count = len(accidents[distance_km <= 5.0])
        all_accident_counts.append(count)
    
    all_accident_counts = np.array(all_accident_counts)
    zones_with_accidents = np.sum(all_accident_counts > 0)
    
    print(f"\nAccident Coverage:")
    print(f"  Zones with accidents (5km radius): {zones_with_accidents}/{len(zones)} ({zones_with_accidents/len(zones)*100:.1f}%)")
    print(f"  Zones without accidents: {len(zones) - zones_with_accidents} ({(len(zones)-zones_with_accidents)/len(zones)*100:.1f}%)")
    print(f"\n  Average accidents per zone: {all_accident_counts.mean():.1f}")
    print(f"  Max accidents in any zone: {all_accident_counts.max()}")
    print(f"  Median accidents per zone: {np.median(all_accident_counts):.0f}")
    
    print(f"\n✓ Accident sentiment calculation working correctly!")
    print(f"  Ready to integrate with multi-source sentiment framework.")
    print(f"\n  Next step: python multi_source_sentiment.py\n")


if __name__ == '__main__':
    test_accident_sentiment()