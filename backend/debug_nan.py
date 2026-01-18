"""Debug NaN values in zones"""
from app import create_app
from app.services.zone_service import get_zones_classified

app = create_app()
with app.app_context():
    zones = get_zones_classified()
    print("Checking for NaN values:")
    print(zones[['adjusted_zone_score', 'base_zone_score', 'biz_score', 'trans_score', 'pop_score']].isna().sum())
    print("\nSample rows with details:")
    cols = ['zone_lat', 'zone_lon', 'business_count', 'transport_count', 'population', 'adjusted_zone_score', 'base_zone_score', 'biz_score', 'trans_score', 'pop_score']
    print(zones[cols].head(5))
    print("\nRows with NaN in adjusted_zone_score:")
    nan_rows = zones[zones['adjusted_zone_score'].isna()]
    print(f"Count: {len(nan_rows)}")
    if len(nan_rows) > 0:
        print(nan_rows[['zone_lat', 'zone_lon', 'business_count', 'transport_count', 'biz_score', 'trans_score', 'pop_score']].head(3))
