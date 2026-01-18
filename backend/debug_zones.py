"""Debug zones loading issue"""
from app import create_app
from app.services.zone_service import get_zones_classified

app = create_app()
with app.app_context():
    try:
        print("📍 Testing zone loading...")
        zones = get_zones_classified()
        print(f'✅ Total zones loaded: {len(zones)}')
        if len(zones) > 0:
            print(f'\n📊 Zone types:')
            print(zones['zone_type'].value_counts())
            print(f'\n🗺️ Sample zone:')
            print(zones[['zone_lat', 'zone_lon', 'zone_type', 'adjusted_zone_score']].head(1))
        else:
            print('⚠️  No zones found in database')
            print('   This means business/transit data might not be loaded.')
            print('   Check if you need to run:')
            print('     - python load_business_data.py')
            print('     - python load_transit_data.py')
    except Exception as e:
        print(f'❌ Error: {type(e).__name__}: {e}')
        import traceback
        traceback.print_exc()
