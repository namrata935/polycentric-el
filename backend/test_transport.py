from app.services.zone_service import get_zones_json
from app.services.recommendation_service import get_zone_recommendations

zones = get_zones_json()

# Find zones with different transport levels
test_zones = []
for z in zones:
    if len(test_zones) < 5:
        test_zones.append(z)

print('Testing transport_access context...\n')
for z in test_zones:
    lat = z['zone_lat']
    lon = z['zone_lon']
    print(f'Zone {lat:.2f}, {lon:.2f}:')
    print(f'  Transport count: {z["transport_count"]}')
    print(f'  Business count: {z["business_count"]}')
    rec = get_zone_recommendations(z)
    print(f'  Transport access: {rec["context"]["transport_access"]}')
    print(f'  Amenity gap transport: {rec["context"]["amenity_gaps"]["transport"]}')
    print()
