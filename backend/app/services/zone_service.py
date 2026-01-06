"""
Zone classification service for aggregating businesses and transit into zones
and calculating zone scores.
"""
import pandas as pd
import numpy as np
from sqlalchemy import text
from app import db
from app.models import Business, TransitNode


def classify_zone(score: float, high_cutoff: float, mid_cutoff: float) -> str:
    """Classify zone based on percentile-based thresholds"""
    if score >= high_cutoff:
        return "Commercial Zone"
    elif score >= mid_cutoff:
        return "Balanced Zone"
    else:
        return "Opportunity Zone"


def get_zones_classified():
    """
    Aggregate businesses and transit nodes into zones and classify them.
    
    Returns:
        DataFrame with zone data including lat, lon, counts, scores, and classification
    """
    # Get database connection from SQLAlchemy
    engine = db.engine
    
    # STEP 1: AGGREGATE BUSINESSES INTO ZONES
    business_query = text("""
        SELECT
            ROUND(latitude::numeric, 2)  AS zone_lat,
            ROUND(longitude::numeric, 2) AS zone_lon,
            COUNT(*) AS business_count
        FROM businesses
        GROUP BY zone_lat, zone_lon
    """)
    
    business_df = pd.read_sql(business_query, engine)
    
    # STEP 2: AGGREGATE TRANSIT INTO ZONES
    transit_query = text("""
        SELECT
            ROUND(latitude::numeric, 2)  AS zone_lat,
            ROUND(longitude::numeric, 2) AS zone_lon,
            COUNT(*) AS transport_count
        FROM transit_nodes
        GROUP BY zone_lat, zone_lon
    """)
    
    transit_df = pd.read_sql(transit_query, engine)
    
    # STEP 3: MERGE INTO ZONES
    zones = pd.merge(
        business_df,
        transit_df,
        on=["zone_lat", "zone_lon"],
        how="outer"
    ).fillna(0)
    
    # STEP 4: REMOVE ULTRA-SPARSE ZONES (OPTIONAL BUT IMPORTANT)
    zones = zones[(zones["business_count"] + zones["transport_count"]) >= 2]
    
    # STEP 5: POPULATION PROXY
    zones["population"] = (
        zones["business_count"] * 300 +
        zones["transport_count"] * 500
    )
    
    # STEP 6: LOG SCALING (KEY FIX)
    zones["biz_log"] = np.log1p(zones["business_count"])
    zones["trans_log"] = np.log1p(zones["transport_count"])
    zones["pop_log"] = np.log1p(zones["population"])
    
    # STEP 7: NORMALIZATION AFTER LOG
    if len(zones) > 0:
        zones["biz_score"] = zones["biz_log"] / zones["biz_log"].max() if zones["biz_log"].max() > 0 else 0
        zones["trans_score"] = zones["trans_log"] / zones["trans_log"].max() if zones["trans_log"].max() > 0 else 0
        zones["pop_score"] = zones["pop_log"] / zones["pop_log"].max() if zones["pop_log"].max() > 0 else 0
    else:
        zones["biz_score"] = 0
        zones["trans_score"] = 0
        zones["pop_score"] = 0
    
    # STEP 8: WEIGHTED ZONE SCORE (REBALANCED)
    zones["zone_score"] = (
        0.35 * zones["pop_score"] +
        0.35 * zones["trans_score"] +
        0.30 * zones["biz_score"]
    )
    
    # STEP 9: PERCENTILE-BASED CLASSIFICATION (KEY FIX)
    if len(zones) > 0:
        high_cutoff = zones["zone_score"].quantile(0.85)
        mid_cutoff = zones["zone_score"].quantile(0.55)
        
        zones["zone_type"] = zones["zone_score"].apply(
            lambda score: classify_zone(score, high_cutoff, mid_cutoff)
        )
    else:
        zones["zone_type"] = "Opportunity Zone"
    
    # Convert to dict for JSON serialization
    return zones


def get_zones_json():
    """
    Get zones as JSON-serializable list of dictionaries.
    
    Returns:
        List of zone dictionaries
    """
    zones_df = get_zones_classified()
    
    # Convert DataFrame to list of dicts
    zones_list = zones_df.to_dict('records')
    
    # Ensure numeric types are JSON serializable
    for zone in zones_list:
        zone['zone_lat'] = float(zone['zone_lat'])
        zone['zone_lon'] = float(zone['zone_lon'])
        zone['business_count'] = int(zone['business_count'])
        zone['transport_count'] = int(zone['transport_count'])
        zone['population'] = int(zone['population'])
        zone['biz_log'] = float(zone.get('biz_log', 0))
        zone['trans_log'] = float(zone.get('trans_log', 0))
        zone['pop_log'] = float(zone.get('pop_log', 0))
        zone['pop_score'] = float(zone['pop_score'])
        zone['biz_score'] = float(zone['biz_score'])
        zone['trans_score'] = float(zone['trans_score'])
        zone['zone_score'] = float(zone['zone_score'])
    
    return zones_list

