from app.services.zone_service import get_zones_json
from app.services.recommendation_service import get_zone_recommendations
import json

zones = get_zones_json()
print(f'✓ Loaded {len(zones)} zones with sentiment data\n')

# Test with a varied zone
test_zone = zones[50]  # Pick a random middle zone

print('Testing full recommendation flow...\n')
lat = test_zone['zone_lat']
lon = test_zone['zone_lon']
print(f'Zone: {lat:.2f}, {lon:.2f}')
print(f'  Business count: {test_zone["business_count"]}')
print(f'  Transport count: {test_zone["transport_count"]}')
print(f'  Zone type: {test_zone["zone_type"]}')
print(f'  Sentiment: {test_zone["final_sentiment"]["mean"]}')
print(f'  Sentiment sources: {test_zone["final_sentiment"]["sources"]}')
print()

rec = get_zone_recommendations(test_zone)
print('Recommendation generated:')
print(f'  Priority: {rec["priority"]}')
print(f'  Sentiment level: {rec["sentiment_level"]}')
primary = rec['primary_recommendation'][:80]
print(f'  Recommendation: {primary}...')
print(f'  Transport access: {rec["context"]["transport_access"]}')
print(f'  Business density: {rec["context"]["business_density"]}')
print(f'  Amenity gaps:')
for category in ['transport', 'retail', 'food', 'healthcare']:
    gap = rec["context"]["amenity_gaps"].get(category, 'N/A')
    print(f'    {category}: {gap}')
print(f'  Focus areas: {rec["focus_areas"]}')
print()
print('✅ Full flow working!')
