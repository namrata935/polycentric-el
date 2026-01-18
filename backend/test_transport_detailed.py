from app.services.zone_service import get_zones_json
from app.services.recommendation_service import get_zone_recommendations

zones = get_zones_json()

# Find zones with transport and without
zones_with_transport = [z for z in zones if z['transport_count'] > 0]
zones_without_transport = [z for z in zones if z['transport_count'] == 0 and z['business_count'] > 20]

print('ZONES WITH TRANSPORT:')
for z in zones_with_transport[:3]:
    lat = z['zone_lat']
    lon = z['zone_lon']
    print(f'\nZone {lat:.2f}, {lon:.2f}:')
    print(f'  Transport count: {z["transport_count"]}')
    print(f'  Business count: {z["business_count"]}')
    rec = get_zone_recommendations(z)
    print(f'  Transport access: {rec["context"]["transport_access"]}')
    print(f'  Amenity gap transport: {rec["context"]["amenity_gaps"]["transport"]}')

print('\n\nZONES WITHOUT TRANSPORT (many businesses):')
for z in zones_without_transport[:3]:
    lat = z['zone_lat']
    lon = z['zone_lon']
    print(f'\nZone {lat:.2f}, {lon:.2f}:')
    print(f'  Transport count: {z["transport_count"]}')
    print(f'  Business count: {z["business_count"]}')
    rec = get_zone_recommendations(z)
    print(f'  Transport access: {rec["context"]["transport_access"]}')
    print(f'  Amenity gap transport: {rec["context"]["amenity_gaps"]["transport"]}')
