from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
import random
from fastapi.middleware.cors import CORSMiddleware

# ----------------------------
# App setup
# ----------------------------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Load model ONCE
# ----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# Precompute fallback embedding ONCE (IMPORTANT FIX)
NONE_EMB = model.encode("none")

# ----------------------------
# Load datasets
# ----------------------------
with open(
    "zones_classified_extended.json"
) as f:
    zones = json.load(f)

# ----------------------------
# Load persisted embeddings
# ----------------------------
print("📦 Loading persisted embeddings...")

zone_embeddings = np.load(
    "embeddings/zone_embeddings.npz",
    allow_pickle=True
)

people_embeddings = np.load(
    "embeddings/people_embeddings.npz",
    allow_pickle=True
)

print("✅ Embeddings loaded")

# ----------------------------
# Helper functions
# ----------------------------
def cosine(a, b):
    return float(cosine_similarity([a], [b])[0][0])


def level(score):
    if score >= 0.6:
        return "High"
    if score >= 0.35:
        return "Moderate"
    return "Low"


def confidence_from_score(score):
    if score >= 0.55:
        return "High"
    if score >= 0.40:
        return "Medium"
    return "Low"


def short_summary(demand, workforce, competition):
    if demand >= 0.6 and workforce >= 0.5 and competition < 0.3:
        return "Strong demand with skilled workforce and manageable competition."
    if demand >= 0.6:
        return "High demand, though competition requires differentiation."
    if workforce >= 0.6:
        return "Strong workforce availability with moderate demand."
    return "Balanced market conditions across demand and supply."


# ----------------------------
# REGION BUCKETING (FOR DIVERSITY)
# ----------------------------
def region_from_lat(lat):
    if lat < 11.8:
        return "Deep South Karnataka"
    if lat < 12.2:
        return "South Karnataka"
    if lat < 12.6:
        return "South-Central Karnataka"
    if lat < 13.2:
        return "Bangalore Peripheral Belt"
    return "North Karnataka"


# ----------------------------
# Explanation generator
# ----------------------------
def generate_detailed_explanation(
    category,
    demand_score,
    workforce_score,
    competition_score,
    zone_score,
    skills_text,
    interests_text
):
    demand_lvl = level(demand_score).lower()
    workforce_lvl = level(workforce_score).lower()
    competition_lvl = level(1 - competition_score).lower()
    opportunity_lvl = level(zone_score).lower()

    templates = [
        f"This zone demonstrates {demand_lvl} demand for a {category}-oriented business, "
        f"driven by interests such as {interests_text}. Workforce suitability is {workforce_lvl}, "
        f"supported by skills like {skills_text}. Competition is {competition_lvl}, and overall "
        f"opportunity is {opportunity_lvl}.",

        f"The local workforce shows {workforce_lvl} alignment for a {category}-based enterprise, "
        f"with skills including {skills_text}. Demand levels are {demand_lvl}, influenced by "
        f"interests such as {interests_text}, while competition remains {competition_lvl}.",

        f"Residents exhibit {demand_lvl} demand for {category} services, supported by interests "
        f"like {interests_text}. Workforce readiness is {workforce_lvl}, and competitive pressure "
        f"is {competition_lvl}, within a {opportunity_lvl} opportunity zone.",

        f"This zone offers {opportunity_lvl} economic potential for a {category} business. "
        f"Demand is {demand_lvl}, workforce readiness is {workforce_lvl}, and competition is "
        f"{competition_lvl}, indicating manageable market risk.",

        f"Strategically, this zone is {opportunity_lvl} suited for a {category}-focused business. "
        f"Workforce skills such as {skills_text} support operations, while demand driven by "
        f"{interests_text} and competition shape feasibility."
    ]

    return random.choice(templates)

# ----------------------------
# Input schema
# ----------------------------
class BusinessInput(BaseModel):
    category: str
    description: str

# ----------------------------
# API endpoint
# ----------------------------
@app.post("/semantic-zone-search")
def semantic_zone_search(data: BusinessInput):
    # ONE model call per request
    user_emb = model.encode(f"{data.category} {data.description}")

    raw_results = []

    # ----------- SCORE ALL ZONES -----------
    for zone in zones:
        lat = zone["zone_lat"]
        lon = zone["zone_lon"]
        key = f"{lat}_{lon}"

        # Zone embeddings
        zone_data = zone_embeddings[key].item()
        context_emb = zone_data["context_emb"]
        existing_emb = zone_data["existing_emb"]
        adjusted_score = zone["adjusted_zone_score"]

        # People embeddings (NO model calls here)
        people_data = people_embeddings.get(key)
        if people_data is not None:
            people_data = people_data.item()
            workforce_emb = people_data["skills_emb"]
            demand_emb = people_data["interests_emb"]
            skills_text = people_data["skills_text"]
            interests_text = people_data["interests_text"]
        else:
            workforce_emb = NONE_EMB
            demand_emb = NONE_EMB
            skills_text = "general skills"
            interests_text = "general consumer needs"

        # Semantic scores
        context_score = cosine(user_emb, context_emb)
        workforce_score = cosine(user_emb, workforce_emb)
        demand_score = cosine(user_emb, demand_emb)
        competition_score = cosine(user_emb, existing_emb)

        final_score = (
            0.25 * context_score +
            0.20 * workforce_score +
            0.20 * demand_score +
            0.20 * adjusted_score +
            0.15 * (1 - competition_score)
        )

        raw_results.append({
            # 🔑 IDENTIFIERS
            "zone_id": zone.get("zone_id") or f"Z-{lat:.2f}-{lon:.2f}",
            "zone_code": zone.get("zone_code") or "KA-UNK",
            "zone_label": zone.get("zone_label") or "Unnamed Zone",
            "zone_type": zone.get("zone_type") or "Commercial Zone",
            "region_name": zone.get("region_name") or region_from_lat(lat),


            # 📍 GEO
            "zone_lat": float(lat),
            "zone_lon": float(lon),

            # 📊 CORE METRICS
            "population": zone.get("population"),
            "business_count": zone.get("business_count"),
            "transport_count": zone.get("transport_count"),
            "base_zone_score": zone.get("base_zone_score"),
            "adjusted_zone_score": zone.get("adjusted_zone_score"),

            # 🧠 SEMANTIC OUTPUT
            "final_score": round(float(final_score), 3),
            "confidence": confidence_from_score(final_score),
            "summary": short_summary(
                demand_score, workforce_score, competition_score
            ),
            "detailed_explanation": generate_detailed_explanation(
                data.category,
                demand_score,
                workforce_score,
                competition_score,
                adjusted_score,
                skills_text,
                interests_text
            ),
            "signals": [
                {"label": "Demand", "value": level(demand_score)},
                {"label": "Workforce", "value": level(workforce_score)},
                {"label": "Competition", "value": level(1 - competition_score)},
                {"label": "Opportunity", "value": level(adjusted_score)},
            ],

            # 🌍 REGION BUCKET (FOR DIVERSITY)
            "region_bucket": region_from_lat(lat),
        })

    # ----------- DIVERSITY RE-RANKING -----------
    raw_results.sort(key=lambda x: x["final_score"], reverse=True)

    diversified = []
    used_regions = set()

    for r in raw_results:
        if r["region_bucket"] not in used_regions:
            diversified.append(r)
            used_regions.add(r["region_bucket"])
        if len(diversified) == 5:
            break

    # fallback
    i = 0
    while len(diversified) < 5 and i < len(raw_results):
        if raw_results[i] not in diversified:
            diversified.append(raw_results[i])
        i += 1

    return diversified
