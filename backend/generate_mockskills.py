import json
import random
import uuid

with open("/Users/namratasrinivasa/Desktop/V-sem/poly-el/polycentric-el/backend/zones_classified.json", "r") as f:
    zones = json.load(f)

# -------------------------------
# Expanded occupation + skills
# -------------------------------
occupations_by_amenity = {
    "school": [
        ("Primary School Teacher", ["Teaching", "Curriculum Planning"]),
        ("School Clerk", ["Administration", "Record Keeping"]),
        ("Education Assistant", ["Student Support", "Monitoring"])
    ],
    "hospital": [
        ("Nursing Assistant", ["Patient Care", "First Aid"]),
        ("Hospital Attendant", ["Patient Assistance", "Sanitation"]),
        ("Medical Records Clerk", ["Data Entry", "Documentation"])
    ],
    "restaurant": [
        ("Cook", ["Cooking", "Food Safety"]),
        ("Wait Staff", ["Customer Service", "Order Handling"]),
        ("Restaurant Manager", ["Operations", "Staff Management"])
    ],
    "fast_food": [
        ("Food Stall Operator", ["Food Prep", "Sales"]),
        ("Cashier", ["Billing", "Customer Interaction"])
    ],
    "college": [
        ("Lecturer", ["Subject Expertise", "Teaching"]),
        ("Lab Assistant", ["Equipment Handling", "Safety"])
    ],
    "retail": [
        ("Shopkeeper", ["Retail Sales", "Inventory"]),
        ("Sales Assistant", ["Customer Service", "Merchandising"])
    ],
    "bank": [
        ("Bank Clerk", ["Finance", "Customer Handling"]),
        ("Loan Officer", ["Credit Assessment", "Documentation"])
    ],
    "pharmacy": [
        ("Pharmacy Assistant", ["Medication Handling", "Inventory"]),
        ("Pharmacist", ["Prescription Management", "Healthcare"])
    ],
    "transport": [
        ("Auto Driver", ["Driving", "Route Knowledge"]),
        ("Bus Conductor", ["Ticketing", "Passenger Handling"])
    ],
    "marketplace": [
        ("Vegetable Vendor", ["Sales", "Supply Handling"]),
        ("Wholesale Trader", ["Negotiation", "Inventory"])
    ],
    "workshop": [
        ("Mechanic", ["Vehicle Repair", "Diagnostics"]),
        ("Electrician", ["Wiring", "Equipment Repair"])
    ],
    "office": [
        ("Office Assistant", ["Clerical Work", "Scheduling"]),
        ("Data Entry Operator", ["Typing", "Data Accuracy"])
    ],
    "construction": [
        ("Construction Worker", ["Masonry", "Material Handling"]),
        ("Site Supervisor", ["Safety", "Team Coordination"])
    ],
    "tourism": [
        ("Tour Guide", ["Communication", "Local Knowledge"]),
        ("Hotel Staff", ["Hospitality", "Housekeeping"])
    ]
}

# -------------------------------
# Expanded interest pool
# -------------------------------
interest_pool = {
    "low_income": [
        "Affordable healthcare", "Public transport",
        "Low-cost food", "Local markets",
        "Government schemes"
    ],
    "middle_income": [
        "Private clinics", "Education services",
        "Banking services", "Mobile repair",
        "Retail shopping"
    ],
    "youth": [
        "Skill training", "Job opportunities",
        "Tech services", "Online learning",
        "Startups"
    ],
    "general": [
        "Food services", "Healthcare",
        "Education", "Retail",
        "Financial services"
    ]
}

people = []

# -------------------------------
# Generate people per zone
# -------------------------------
for zone in zones:
    lat = zone["zone_lat"]
    lon = zone["zone_lon"]

    raw_tags = zone.get("business_raw_tags", [])

    amenities = set()

    if isinstance(raw_tags, list):
        for t in raw_tags:
            if isinstance(t, dict) and "amenity" in t:
                amenities.add(t["amenity"])


    # density scaling
    num_people = max(5, int(zone["population"] // 150))

    for _ in range(num_people):
        amenity = random.choice(list(amenities)) if amenities else "retail"

        occupation, base_skills = random.choice(
            occupations_by_amenity.get(
                amenity,
                [("Local Worker", ["General Skills"])]
            )
        )

        income_level = random.choice(
            ["Lower-middle", "Middle", "Upper-middle"]
        )

        # interest selection logic
        interests = []
        if income_level == "Lower-middle":
            interests.extend(random.sample(interest_pool["low_income"], 2))
        else:
            interests.extend(random.sample(interest_pool["middle_income"], 2))

        if random.random() > 0.5:
            interests.append(random.choice(interest_pool["youth"]))

        interests.append(random.choice(interest_pool["general"]))

        person = {
            "person_id": str(uuid.uuid4())[:8],
            "zone_lat": lat,
            "zone_lon": lon,
            "age": random.randint(21, 55),
            "education": random.choice(
                ["High School", "Diploma", "Bachelor's", "Master's"]
            ),
            "occupation": occupation,
            "skills": list(set(
                base_skills + random.sample(
                    ["Communication", "Time Management", "Problem Solving"],
                    1
                )
            )),
            "income_level": income_level,
            "employment_status": random.choice(
                ["Employed", "Self-employed", "Contract"]
            ),
            "interests": list(set(interests))
        }

        people.append(person)

# -------------------------------
# Save dataset
# -------------------------------
with open("skills_by_zone.json", "w") as f:
    json.dump(people, f, indent=2)

print(f"Generated {len(people)} people across {len(zones)} zones.")
