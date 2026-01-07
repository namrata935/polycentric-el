"""
Zone classification service for aggregating businesses and transit into zones
and identifying opportunity-focused zones for expansion analysis.
"""

import pandas as pd
import numpy as np
from sqlalchemy import text
from app import db


# -------------------------------------------------
# Classification helper
# -------------------------------------------------
def classify_zone(score: float, high_cutoff: float, mid_cutoff: float) -> str:
    if score >= high_cutoff:
        return "Commercial Zone"
    elif score >= mid_cutoff:
        return "Balanced Zone"
    else:
        return "Opportunity Zone"


# -------------------------------------------------
# Core logic
# -------------------------------------------------
def get_zones_classified():
    """
    Aggregate businesses and transit nodes into zones and classify them
    with an opportunity-aware bias.

    Returns:
        pandas.DataFrame
    """

    engine = db.engine

    # -------------------------------------------------
    # STEP 1: AGGREGATE BUSINESSES
    # -------------------------------------------------
    business_query = text("""
        SELECT
    ROUND(latitude::numeric, 2)  AS zone_lat,
    ROUND(longitude::numeric, 2) AS zone_lon,
    COUNT(*) AS business_count,
    json_agg(raw_tags) AS business_raw_tags
        FROM businesses
        GROUP BY zone_lat, zone_lon
    """)
    business_df = pd.read_sql(business_query, engine)

    # -------------------------------------------------
    # STEP 2: AGGREGATE TRANSIT
    # -------------------------------------------------
    transit_query = text("""
        SELECT
            ROUND(latitude::numeric, 2)  AS zone_lat,
            ROUND(longitude::numeric, 2) AS zone_lon,
            COUNT(*) AS transport_count
        FROM transit_nodes
        GROUP BY zone_lat, zone_lon
    """)
    transit_df = pd.read_sql(transit_query, engine)

    # -------------------------------------------------
    # STEP 3: MERGE INTO ZONES
    # -------------------------------------------------
    zones = pd.merge(
        business_df,
        transit_df,
        on=["zone_lat", "zone_lon"],
        how="outer"
    ).fillna(0)

    # -------------------------------------------------
    # STEP 4: DROP ULTRA-SPARSE ZONES
    # -------------------------------------------------
    zones = zones[(zones["business_count"] + zones["transport_count"]) >= 2]

    if zones.empty:
        return zones

    # -------------------------------------------------
    # STEP 5: POPULATION PROXY
    # -------------------------------------------------
    zones["population"] = (
        zones["business_count"] * 300 +
        zones["transport_count"] * 500
    )

    # -------------------------------------------------
    # STEP 6: LOG SCALING (SKEW FIX)
    # -------------------------------------------------
    zones["biz_log"] = np.log1p(zones["business_count"])
    zones["trans_log"] = np.log1p(zones["transport_count"])
    zones["pop_log"] = np.log1p(zones["population"])

    # -------------------------------------------------
    # STEP 7: NORMALIZATION
    # -------------------------------------------------
    zones["biz_score"] = zones["biz_log"] / zones["biz_log"].max()
    zones["trans_score"] = zones["trans_log"] / zones["trans_log"].max()
    zones["pop_score"] = zones["pop_log"] / zones["pop_log"].max()

    # -------------------------------------------------
    # STEP 8: BASE ACTIVITY SCORE
    # -------------------------------------------------
    zones["base_zone_score"] = (
        0.35 * zones["pop_score"] +
        0.35 * zones["trans_score"] +
        0.30 * zones["biz_score"]
    )

    # -------------------------------------------------
    # STEP 9: OPPORTUNITY-AWARE ADJUSTMENTS (KEY PART)
    # -------------------------------------------------

    # Penalize already saturated business hubs (Tier-1 cores)
    zones["saturation_penalty"] = zones["biz_score"] ** 2

    # Boost zones with population but low saturation (Tier-2 potential)
    zones["opportunity_boost"] = (
        (1 - zones["biz_score"]) *
        zones["pop_score"]
    )

    # Final adjusted score
    zones["adjusted_zone_score"] = (
        zones["base_zone_score"]
        - 0.20 * zones["saturation_penalty"]
        + 0.25 * zones["opportunity_boost"]
    )

    zones["adjusted_zone_score"] = zones["adjusted_zone_score"].clip(0, 1)

    # -------------------------------------------------
    # STEP 10: OPPORTUNITY-FOCUSED CLASSIFICATION
    # -------------------------------------------------
    high_cutoff = zones["adjusted_zone_score"].quantile(0.90)
    mid_cutoff  = zones["adjusted_zone_score"].quantile(0.60)

    zones["zone_type"] = zones["adjusted_zone_score"].apply(
        lambda s: classify_zone(s, high_cutoff, mid_cutoff)
    )

    return zones


# -------------------------------------------------
# JSON API helper
# -------------------------------------------------
def get_zones_json():
    """
    Return zones in JSON-serializable format
    """

    zones_df = get_zones_classified()
    zones_list = zones_df.to_dict("records")

    for z in zones_list:
        z["zone_lat"] = float(z["zone_lat"])
        z["zone_lon"] = float(z["zone_lon"])
        z["business_count"] = int(z["business_count"])
        z["transport_count"] = int(z["transport_count"])
        z["population"] = int(z["population"])

        z["biz_score"] = float(z["biz_score"])
        z["trans_score"] = float(z["trans_score"])
        z["pop_score"] = float(z["pop_score"])

        z["base_zone_score"] = float(z["base_zone_score"])
        z["adjusted_zone_score"] = float(z["adjusted_zone_score"])
        z["business_raw_tags"] = z.get("business_raw_tags", [])
    return zones_list

def save_zones_to_json(file_path="zones_classified.json"):
    zones_df = get_zones_classified()
    zones_json = zones_df.to_dict("records")

    with open(file_path, "w") as f:
        import json
        json.dump(zones_json, f, indent=2)

    print(f"[OK] Zones saved to {file_path}")



