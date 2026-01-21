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
with open("zones_classified_extended.json") as f:
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
    """Confidence based on visual score (matches frontend mapping)"""
    visual_score = visual_score_calc(score)
    if visual_score >= 70:
        return "High"
    if visual_score >= 60:
        return "Medium"
    return "Low"


def visual_score_calc(score):
    """Match frontend visualScore calculation exactly"""
    min_val = 0.32
    max_val = 0.6
    clamped = min(max(score, min_val), max_val)
    return round(60 + ((clamped - min_val) / (max_val - min_val)) * 35)


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
# RELEVANT SKILLS/INTERESTS GENERATOR
# ----------------------------
def generate_relevant_items(category, description):
    """Generate plausible skills and interests based on business category"""
    category_lower = category.lower()
    desc_lower = description.lower()
    
    # Find best match and return MORE than 3 (we'll pick randomly later)
    for key in SKILLS_MAP.keys():
        if key in category_lower or key in desc_lower:
            all_skills = SKILLS_MAP[key]
            all_interests = INTERESTS_MAP[key]
            
            # Randomly select 3 from the larger pool for variety
            import random
            selected_skills = random.sample(all_skills, min(3, len(all_skills)))
            selected_interests = random.sample(all_interests, min(3, len(all_interests)))
            
            return selected_skills, selected_interests
    
    # Fallback generic
    return ["Customer Service", "Operations Management", "Communication"], ["Local Services", "Convenience", "Quality Products"]


# ----------------------------
# SMART EXPLANATION GENERATOR
# ----------------------------
def generate_smart_explanation(category, final_score):
    """Generate tier-based explanations: Excellent (70+), Average (60-70), Poor (<60)"""
    
    # Use visual score (matches frontend display)
    visual_score = visual_score_calc(final_score)
    
    # ========== EXCELLENT TIER (70+) ==========
    if visual_score >= 70:
        templates = [
            f"🌟 Exceptional opportunity for your {category} business! This zone demonstrates outstanding market alignment with strong demand, a well-equipped workforce, and manageable competition. All key indicators point to high success potential.",
            
            f"🎯 Outstanding match for {category} operations! The market conditions here are highly favorable with robust local demand, skilled talent availability, and a competitive landscape you can thrive in.",
            
            f"⭐ Highly favorable location! Your {category} venture would excel in this zone with excellent demand patterns, strong workforce capabilities, and advantageous competitive dynamics.",
            
            f"💎 Premium opportunity zone! This location ranks among the best for {category} businesses, showing exceptional viability across all key success factors.",
            
            f"✨ Excellent business environment! The convergence of high demand, capable workforce, and manageable competition creates ideal conditions for your {category} venture.",
            
            f"🚀 Top-tier opportunity! This zone presents outstanding potential for {category} services with all major indicators strongly aligned in your favor.",
            
            f"🏆 Outstanding business potential! Market fundamentals are exceptionally strong for {category} operations with high demand and favorable supply-side conditions.",
            
            f"💪 Exceptionally strong match! Your {category} business would benefit from excellent market demand, workforce readiness, and strategic competitive positioning here.",
            
            f"🌟 Prime location identified! This zone offers superior conditions for {category} ventures with robust demand drivers and strong operational foundations.",
            
            f"⭐ Highly recommended zone! All critical success factors align exceptionally well for {category} businesses in this area.",
            
            f"🎯 Outstanding market fit! This location demonstrates excellent viability for {category} operations with strong fundamentals across demand and supply.",
            
            f"💎 Top-ranked opportunity! The zone shows exceptional promise for {category} services with favorable conditions on all key metrics.",
            
            f"✨ Superior business environment! Market conditions strongly favor {category} ventures with high demand and excellent workforce alignment.",
            
            f"🚀 Exceptional growth potential! This zone presents outstanding opportunities for {category} businesses to establish and thrive.",
            
            f"🏆 Premium market conditions! Your {category} venture would benefit from excellent demand patterns and strong operational support in this zone.",
        ]
    
    # ========== AVERAGE TIER (60-70) ==========
    elif visual_score >= 60:
        templates = [
            f"✓ Solid potential for your {category} business. Market demand is present and local capabilities provide a decent foundation. Competition exists but remains manageable with the right strategy.",
            
            f"📊 Moderate opportunity for {category} operations. The zone shows reasonable market alignment and workforce capabilities. The fundamentals are in place for a well-planned business.",
            
            f"⚖️ Balanced market conditions for your {category} venture. Demand indicators are adequate and workforce support is reasonable, though competition will require differentiation.",
            
            f"👍 Acceptable location for {category} services. The zone presents fair conditions with moderate demand and reasonable capability levels that can be strategically navigated.",
            
            f"✅ Viable option for {category} businesses. Market conditions show moderate strength with adequate demand and workforce foundations to build upon.",
            
            f"📈 Reasonable opportunity zone. Your {category} venture could succeed here with careful planning and strategic positioning to address competitive pressures.",
            
            f"🎯 Fair market potential for {category} operations. Demand levels are satisfactory and local capabilities support business viability with proper execution.",
            
            f"⚖️ Moderate suitability detected. This zone offers balanced conditions for {category} services though success will depend on strategic differentiation.",
            
            f"✓ Decent business environment. The fundamentals for {category} ventures are moderately strong with addressable competitive challenges.",
            
            f"📊 Acceptable market alignment for {category} businesses. Demand and supply factors show reasonable balance requiring strategic market positioning.",
            
            f"👍 Fair opportunity level. This zone presents moderate potential for {category} operations with adequate foundational support.",
            
            f"✅ Reasonable business case. Market conditions are moderately favorable for {category} ventures with manageable execution challenges.",
            
            f"📈 Moderate viability zone. Your {category} business could establish successfully here with focused strategy and market awareness.",
            
            f"⚖️ Balanced potential identified. The zone offers fair conditions for {category} services with standard market dynamics to navigate.",
            
            f"✓ Acceptable market opportunity. Fundamentals support {category} business development though competitive strategy will be important.",
        ]
    
    # ========== POOR TIER (<60) ==========
    else:
        templates = [
            f"⚠️ Limited suitability for your {category} business. Overall market conditions present significant challenges with insufficient demand, high competition, or weak workforce alignment.",
            
            f"❌ Below-average opportunity for {category} operations. Key success factors are lacking and this location would require considerable investment to overcome market disadvantages.",
            
            f"🔴 Challenging environment for {category} ventures. The zone shows weak market alignment and fundamental gaps exist that may hinder business success.",
            
            f"⛔ Poor market fit for {category} services. Demand is limited, workforce capabilities are insufficient, or competition is too intense. Consider higher-scoring alternatives.",
            
            f"⚠️ Unfavorable conditions detected. This zone presents substantial obstacles for {category} businesses with multiple weak indicators across key metrics.",
            
            f"❌ Not recommended for {category} operations. Market fundamentals are inadequate and significant barriers exist that would challenge business viability.",
            
            f"🔴 High-risk opportunity. The zone shows concerning weakness in critical success factors for {category} ventures requiring substantial market development.",
            
            f"⛔ Suboptimal location identified. Key indicators suggest {category} businesses would face considerable headwinds in this market environment.",
            
            f"⚠️ Weak market potential. Fundamental conditions for {category} services are below acceptable thresholds across demand and operational factors.",
            
            f"❌ Poor business environment. This zone lacks the necessary market strength for {category} ventures to establish successfully without major interventions.",
            
            f"🔴 Challenging market dynamics. Multiple weak indicators suggest {category} operations would struggle with demand, competition, or workforce issues.",
            
            f"⛔ Limited viability detected. The zone presents unfavorable conditions for {category} businesses with insufficient market support.",
            
            f"⚠️ Below standard opportunity. Market fundamentals fall short of requirements for sustainable {category} business operations.",
            
            f"❌ Unfavorable zone characteristics. Key success factors are inadequate for {category} ventures making this a high-risk location choice.",
            
            f"🔴 Weak market alignment. This zone shows concerning gaps in critical areas that would challenge {category} business success.",
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

        # Generate unique skills/interests per zone
        top_skills, top_interests = generate_relevant_items(data.category, data.description)

        raw_results.append({
            # 🔑 IDENTIFIERS
            "zone_id": zone.get("zone_id") or f"Z-{lat:.2f}-{lon:.2f}",
            "zone_code": zone.get("zone_code") or "KA-UNK",
            "zone_label": "",  # Removed to avoid "Local Services Zone" text
            "zone_type": "",  # Removed to avoid "Commercial Zone" text
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
            "detailed_explanation": generate_smart_explanation(
                data.category,
                final_score
            ),
            "signals": [
                {"label": "Demand", "value": level(demand_score)},
                {"label": "Workforce", "value": level(workforce_score)},
                {"label": "Competition", "value": level(1 - competition_score)},
                {"label": "Opportunity", "value": level(adjusted_score)},
            ],
            
            # 🎯 RELEVANT MATCHES (same for all zones, matches user input)
            "top_skills": top_skills,
            "top_interests": top_interests,

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


# ----------------------------
# SKILLS & INTERESTS MAPPINGS
# ----------------------------
SKILLS_MAP = {
    "food": ["Food Preparation", "Food Safety & Hygiene", "Customer Service", "Menu Planning", "Kitchen Management", "Food Cost Control"],
    "restaurant": ["Culinary Arts", "Kitchen Management", "Food Service Operations", "Staff Training", "Quality Control", "Customer Relations"],
    "cafe": ["Barista Techniques", "Food & Beverage Service", "Customer Relations", "Cash Handling", "Inventory Management", "Cleaning & Sanitation"],
    "coffee": ["Coffee Brewing", "Espresso Machine Operation", "Customer Engagement", "Latte Art", "Bean Selection", "Equipment Maintenance"],
    "bakery": ["Baking & Pastry", "Recipe Development", "Quality Control", "Dough Preparation", "Decorating Skills", "Production Planning"],
    "catering": ["Event Catering", "Menu Planning", "Food Production Management", "Transportation Logistics", "Client Communication", "Team Coordination"],
    
    "retail": ["Sales & Marketing", "Inventory Management", "Customer Service", "Visual Merchandising", "Cash Management", "Product Knowledge"],
    "shop": ["Product Knowledge", "Visual Merchandising", "Point of Sale Operations", "Stock Control", "Customer Assistance", "Loss Prevention"],
    "store": ["Retail Operations", "Stock Management", "Customer Relations", "Sales Techniques", "Store Layout", "Team Leadership"],
    "boutique": ["Fashion Merchandising", "Styling Consultation", "Sales", "Trend Forecasting", "Client Relations", "Buying & Sourcing"],
    "grocery": ["Inventory Control", "Product Display", "Customer Assistance", "Fresh Food Handling", "Pricing", "Shelf Stocking"],
    
    "tech": ["Technical Support", "Software Proficiency", "Problem Solving", "Troubleshooting", "Documentation", "System Configuration"],
    "software": ["Software Development", "System Architecture", "Quality Assurance", "Code Review", "Database Management", "API Integration"],
    "it": ["IT Support", "Network Administration", "Technical Troubleshooting", "Hardware Repair", "Security Protocols", "User Training"],
    "computer": ["Computer Repair", "Hardware Diagnostics", "Software Installation", "Data Recovery", "Virus Removal", "System Optimization"],
    "electronics": ["Electronic Repair", "Circuit Analysis", "Device Troubleshooting", "Soldering", "Component Testing", "Warranty Service"],
    
    "salon": ["Hair Styling", "Beauty Services", "Client Consultation"],
    "beauty": ["Makeup Application", "Skincare Services", "Beauty Consultation"],
    "spa": ["Spa Treatments", "Massage Therapy", "Client Care"],
    "barbershop": ["Hair Cutting", "Shaving Services", "Customer Service"],
    
    "fitness": ["Personal Training", "Exercise Instruction", "Nutrition Guidance"],
    "gym": ["Fitness Coaching", "Equipment Maintenance", "Member Engagement"],
    "yoga": ["Yoga Instruction", "Wellness Coaching", "Class Management"],
    "sports": ["Athletic Training", "Sports Coaching", "Performance Analysis"],
    
    "education": ["Teaching & Instruction", "Curriculum Development", "Student Assessment"],
    "tutoring": ["Subject Matter Expertise", "Lesson Planning", "Student Evaluation"],
    "training": ["Training Delivery", "Course Design", "Performance Assessment"],
    "coaching": ["Coaching Methodology", "Goal Setting", "Progress Tracking"],
    
    "healthcare": ["Medical Knowledge", "Patient Care", "Healthcare Administration"],
    "clinic": ["Clinical Procedures", "Patient Management", "Medical Records"],
    "dental": ["Dental Care", "Patient Treatment", "Oral Health Education"],
    "pharmacy": ["Pharmaceutical Knowledge", "Prescription Management", "Customer Counseling"],
    
    "auto": ["Automotive Repair", "Diagnostics & Testing", "Mechanical Skills"],
    "repair": ["Technical Repair", "Equipment Troubleshooting", "Maintenance"],
    "mechanic": ["Engine Repair", "Auto Diagnostics", "Vehicle Maintenance"],
    "garage": ["Automotive Service", "Parts Replacement", "Quality Inspection"],
    
    "cleaning": ["Professional Cleaning", "Equipment Operation", "Time Management"],
    "laundry": ["Fabric Care", "Stain Treatment", "Pressing & Folding"],
    "housekeeping": ["Housekeeping Services", "Sanitation Standards", "Organization"],
    
    "delivery": ["Route Planning", "Logistics Coordination", "Customer Delivery"],
    "logistics": ["Supply Chain Management", "Warehouse Operations", "Distribution"],
    "courier": ["Package Handling", "Delivery Scheduling", "Customer Service"],
    "transport": ["Transportation Management", "Route Optimization", "Fleet Coordination"],
    
    "construction": ["Carpentry", "Electrical Installation", "Project Management"],
    "contractor": ["Construction Management", "Trade Coordination", "Quality Control"],
    "plumbing": ["Plumbing Installation", "Pipe Repair", "System Maintenance"],
    "electrical": ["Electrical Wiring", "Circuit Installation", "Safety Compliance"],
    
    "fashion": ["Fashion Design", "Pattern Making", "Trend Analysis"],
    "tailoring": ["Garment Tailoring", "Alterations", "Custom Fitting"],
    "clothing": ["Apparel Production", "Quality Inspection", "Fabric Selection"],
    
    "photography": ["Photography Skills", "Photo Editing", "Client Management"],
    "video": ["Video Production", "Editing & Post-Production", "Creative Direction"],
    "design": ["Graphic Design", "Creative Software", "Brand Development"],
    
    "event": ["Event Planning", "Vendor Coordination", "Project Management"],
    "wedding": ["Wedding Coordination", "Event Decoration", "Timeline Management"],
    "party": ["Party Planning", "Entertainment Coordination", "Guest Services"],
    
    "real estate": ["Property Sales", "Market Analysis", "Client Negotiation"],
    "property": ["Property Management", "Tenant Relations", "Maintenance Coordination"],
    
    "finance": ["Financial Analysis", "Accounting", "Client Advisory"],
    "accounting": ["Bookkeeping", "Tax Preparation", "Financial Reporting"],
    "insurance": ["Insurance Sales", "Risk Assessment", "Policy Management"],
    
    "hotel": ["Hospitality Management", "Guest Services", "Operations Management"],
    "travel": ["Travel Planning", "Itinerary Design", "Customer Service"],
    "tourism": ["Tour Coordination", "Destination Knowledge", "Guest Relations"],
}

INTERESTS_MAP = {
    "food": ["Dining Experiences", "Culinary Exploration", "Local Cuisine", "Food Quality", "Authentic Flavors", "Meal Variety"],
    "restaurant": ["Fine Dining", "Restaurant Culture", "Food Quality", "Ambiance", "Special Occasions", "Gourmet Experiences"],
    "cafe": ["Coffee Culture", "Casual Dining", "Social Gatherings", "Relaxed Atmosphere", "Quick Bites", "Meeting Spaces"],
    "coffee": ["Specialty Coffee", "Coffee Appreciation", "Cafe Atmosphere", "Artisan Brews", "Coffee Quality", "Cozy Spaces"],
    "bakery": ["Fresh Baked Goods", "Artisan Breads", "Desserts & Pastries", "Morning Treats", "Sweet Indulgences", "Quality Ingredients"],
    "catering": ["Event Dining", "Customized Menus", "Professional Catering", "Party Food", "Special Events", "Food Presentation"],
    
    "retail": ["Shopping Experience", "Product Discovery", "Brand Preferences", "Retail Therapy", "New Products", "Quality Shopping"],
    "shop": ["Local Shopping", "Product Variety", "Quality Merchandise", "Convenient Access", "Store Atmosphere", "Personalized Service"],
    "store": ["Retail Convenience", "Shopping Trends", "Customer Service", "Product Selection", "Store Loyalty", "Shopping Ease"],
    "boutique": ["Fashion Trends", "Unique Styles", "Personalized Shopping", "Exclusive Items", "Boutique Experience", "Style Curation"],
    "grocery": ["Fresh Produce", "Grocery Convenience", "Quality Groceries", "Weekly Shopping", "Fresh Foods", "Local Products"],
    
    "tech": ["Technology Adoption", "Digital Solutions", "Innovation", "Tech Convenience", "Smart Solutions", "Modern Technology"],
    "software": ["Software Tools", "Productivity Apps", "Tech Efficiency", "Digital Workflows", "Automation", "Cloud Solutions"],
    "it": ["IT Services", "Technical Solutions", "System Reliability", "Tech Support", "Network Services", "IT Infrastructure"],
    "computer": ["Computer Services", "Device Upgrades", "Tech Maintenance", "Performance", "Reliable Computing", "Tech Help"],
    "electronics": ["Consumer Electronics", "Device Repair", "Tech Gadgets", "Latest Devices", "Electronic Solutions", "Tech Accessories"],
    
    "salon": ["Personal Grooming", "Hair Care", "Beauty Trends"],
    "beauty": ["Beauty Services", "Skincare", "Personal Enhancement"],
    "spa": ["Wellness & Relaxation", "Spa Treatments", "Self-Care"],
    "barbershop": ["Grooming Services", "Traditional Barbering", "Style Maintenance"],
    
    "fitness": ["Health & Fitness", "Active Lifestyle", "Wellness Goals"],
    "gym": ["Workout Routines", "Strength Training", "Fitness Community"],
    "yoga": ["Yoga Practice", "Mindfulness", "Holistic Wellness"],
    "sports": ["Athletic Performance", "Sports Activities", "Competition"],
    
    "education": ["Learning & Development", "Skill Acquisition", "Academic Growth"],
    "tutoring": ["Academic Support", "Test Preparation", "Subject Mastery"],
    "training": ["Professional Development", "Skill Training", "Career Advancement"],
    "coaching": ["Personal Coaching", "Goal Achievement", "Performance Improvement"],
    
    "healthcare": ["Health Services", "Medical Care", "Wellness Management"],
    "clinic": ["Medical Consultation", "Healthcare Access", "Treatment Options"],
    "dental": ["Dental Health", "Oral Care", "Preventive Dentistry"],
    "pharmacy": ["Medication Access", "Health Products", "Pharmaceutical Services"],
    
    "auto": ["Vehicle Maintenance", "Auto Care", "Reliable Transportation"],
    "repair": ["Repair Services", "Equipment Maintenance", "Quick Fixes"],
    "mechanic": ["Auto Service", "Vehicle Repair", "Mechanical Reliability"],
    "garage": ["Automotive Services", "Car Maintenance", "Vehicle Care"],
    
    "cleaning": ["Clean Spaces", "Professional Cleaning", "Home Hygiene"],
    "laundry": ["Laundry Services", "Garment Care", "Fabric Maintenance"],
    "housekeeping": ["Home Maintenance", "Cleaning Services", "Organization"],
    
    "delivery": ["Home Delivery", "Convenience Services", "Fast Shipping"],
    "logistics": ["Supply Solutions", "Efficient Delivery", "Product Access"],
    "courier": ["Package Delivery", "Express Services", "Reliable Shipping"],
    "transport": ["Transportation Services", "Commute Solutions", "Mobility"],
    
    "construction": ["Home Improvement", "Renovation Projects", "Building Services"],
    "contractor": ["Construction Services", "Project Development", "Quality Building"],
    "plumbing": ["Plumbing Services", "Water Systems", "Home Repairs"],
    "electrical": ["Electrical Services", "Home Wiring", "Safety Solutions"],
    
    "fashion": ["Fashion Trends", "Personal Style", "Clothing Preferences"],
    "tailoring": ["Custom Clothing", "Garment Alterations", "Perfect Fit"],
    "clothing": ["Apparel Shopping", "Fashion Choices", "Wardrobe Selection"],
    
    "photography": ["Photography Services", "Event Photography", "Memory Preservation"],
    "video": ["Video Content", "Professional Videos", "Creative Production"],
    "design": ["Design Services", "Visual Communication", "Creative Solutions"],
    
    "event": ["Event Services", "Special Occasions", "Celebrations"],
    "wedding": ["Wedding Planning", "Marriage Celebrations", "Event Coordination"],
    "party": ["Party Hosting", "Celebrations", "Social Events"],
    
    "real estate": ["Property Investment", "Home Ownership", "Real Estate Opportunities"],
    "property": ["Property Management", "Rental Solutions", "Housing Options"],
    
    "finance": ["Financial Planning", "Investment Opportunities", "Money Management"],
    "accounting": ["Tax Services", "Accounting Support", "Financial Records"],
    "insurance": ["Insurance Coverage", "Risk Protection", "Policy Options"],
    
    "hotel": ["Accommodation Services", "Travel Stays", "Hospitality Experience"],
    "travel": ["Travel Services", "Vacation Planning", "Destination Experiences"],
    "tourism": ["Tourism Activities", "Local Attractions", "Travel Experiences"],
}