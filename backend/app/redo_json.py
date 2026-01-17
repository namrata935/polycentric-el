import json
from collections import defaultdict

INPUT_FILE = "/Users/namratasrinivasa/Desktop/V-sem/poly-el/polycentric-el/backend/zones_classified.json"
OUTPUT_FILE = "zones_classified_extended.json"

def determine_region(lat, lon):
    # Urban Bangalore override
    if 12.7 <= lat <= 13.2 and 77.4 <= lon <= 77.9:
        return "Bangalore Metropolitan Region", "KA-BLR"

    if lat >= 15.0:
        return "Far North Karnataka", "KA-FN"
    if lat >= 14.0:
        return "North Karnataka", "KA-N"
    if lat >= 13.0:
        return "North-Central Karnataka", "KA-NC"
    if lat >= 12.5:
        return "Central Karnataka", "KA-C"
    if lat >= 12.0:
        return "South-Central Karnataka", "KA-SC"
    if lat >= 11.5:
        return "South Karnataka", "KA-S"
    return "Deep South Karnataka", "KA-DS"

def infer_zone_theme(zone):
    raw = zone.get("business_raw_tags", [])

    # SAFETY: handle bad data
    if not isinstance(raw, list):
        return "Mixed Services Zone"

    amenities = []
    for t in raw:
        if isinstance(t, dict) and "amenity" in t:
            amenities.append(t["amenity"])

    if amenities.count("hospital") > 0:
        return "Healthcare Hub"
    if amenities.count("restaurant") + amenities.count("fast_food") >= 2:
        return "Commercial Node"
    if amenities.count("school") >= 2:
        return "Education Cluster"
    if len(amenities) > 0:
        return "Local Services Zone"

    return "Low Activity Zone"


with open(INPUT_FILE) as f:
    zones = json.load(f)

region_counters = defaultdict(int)

for zone in zones:
    lat = zone["zone_lat"]
    lon = zone["zone_lon"]

    region_name, region_code = determine_region(lat, lon)
    region_counters[region_code] += 1

    theme = infer_zone_theme(zone)
    index = str(region_counters[region_code]).zfill(2)

    zone["region_name"] = region_name
    zone["zone_code"] = region_code
    zone["zone_id"] = f"Z-{region_code}-{index}"
    zone["zone_label"] = f"{region_name} – {theme}"

with open(OUTPUT_FILE, "w") as f:
    json.dump(zones, f, indent=2)

print("✅ Zone labeling complete. New file created:", OUTPUT_FILE)
