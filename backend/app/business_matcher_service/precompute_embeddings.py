import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer

# ----------------------------
# Paths
# ----------------------------
EMBED_DIR = "embeddings"
PEOPLE_EMB_PATH = os.path.join(EMBED_DIR, "people_embeddings.npz")
ZONE_EMB_PATH = os.path.join(EMBED_DIR, "zone_embeddings.npz")

os.makedirs(EMBED_DIR, exist_ok=True)

# ----------------------------
# Check if embeddings already exist
# ----------------------------
people_exists = os.path.exists(PEOPLE_EMB_PATH)
zone_exists = os.path.exists(ZONE_EMB_PATH)

if people_exists and zone_exists:
    print("✅ Embeddings already exist. Skipping computation.")
    exit(0)

print("🔄 Computing missing embeddings...")

# ----------------------------
# Load data
# ----------------------------
with open("skills_by_zone.json") as f:
    people = json.load(f)

with open("zones_classified.json") as f:
    zones = json.load(f)

model = SentenceTransformer("all-MiniLM-L6-v2")

# ----------------------------
# Safe helpers
# ----------------------------
def safe_amenities(zone):
    raw = zone.get("business_raw_tags", [])
    if not isinstance(raw, list):
        return set()
    return {
        t["amenity"]
        for t in raw
        if isinstance(t, dict) and "amenity" in t
    }


def build_context_text(zone):
    amenities = safe_amenities(zone)
    return " ".join(amenities) if amenities else "none"

# ----------------------------
# People embeddings
# ----------------------------
if not people_exists:
    print("👥 Processing people embeddings...")

    people_by_zone = {}

    for p in people:
        key = f"{p['zone_lat']}_{p['zone_lon']}"
        people_by_zone.setdefault(key, {"skills": [], "interests": []})
        people_by_zone[key]["skills"].extend(p.get("skills", []))
        people_by_zone[key]["interests"].extend(p.get("interests", []))

    people_embeddings = {}

    for key, data in people_by_zone.items():
        skills_text = " ".join(set(data["skills"])) or "none"
        interests_text = " ".join(set(data["interests"])) or "none"

        people_embeddings[key] = {
            "skills_emb": model.encode(skills_text),
            "interests_emb": model.encode(interests_text),
            "skills_text": skills_text,
            "interests_text": interests_text
        }

    np.savez(PEOPLE_EMB_PATH, **people_embeddings)
    print("✅ People embeddings saved")

else:
    print("➡️ People embeddings already exist. Skipping.")

# ----------------------------
# Zone embeddings
# ----------------------------
if not zone_exists:
    print("📍 Processing zone embeddings...")

    zone_embeddings = {}

    for zone in zones:
        key = f"{zone['zone_lat']}_{zone['zone_lon']}"

        context_text = build_context_text(zone)
        existing_text = context_text  # reuse safely

        zone_embeddings[key] = {
            "context_emb": model.encode(context_text),
            "existing_emb": model.encode(existing_text),
            "adjusted_score": zone["adjusted_zone_score"]
        }

    np.savez(ZONE_EMB_PATH, **zone_embeddings)
    print("✅ Zone embeddings saved")

else:
    print("➡️ Zone embeddings already exist. Skipping.")

print("🎉 Precomputation complete")
