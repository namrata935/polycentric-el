import json
from pathlib import Path
from collections import Counter

sentiment_file = Path('sentiment/output/zones_final_sentiment.json')
with open(sentiment_file, 'r', encoding='utf-8') as f:
    zones = json.load(f)

# Collect all unique amenity types
all_amenities = Counter()
for zone in zones:
    tags = zone.get('business_raw_tags', [])
    if isinstance(tags, list):
        for tag in tags:
            if isinstance(tag, dict):
                amenity = tag.get('amenity', 'unknown')
                all_amenities[amenity] += 1

print('Top 35 amenity types found:')
for amenity, count in all_amenities.most_common(35):
    print(f'  {amenity}: {count}')

# Now test the keyword matching
print('\n\nKeyword matching analysis:')
amenity_keywords = {
    'transport': ['bus', 'metro', 'station', 'railway', 'transit', 'transit_node'],
    'healthcare': ['hospital', 'clinic', 'health', 'pharmacy', 'doctor'],
    'education': ['school', 'college', 'university', 'education'],
    'retail': ['supermarket', 'shop', 'mall', 'market', 'retail'],
    'food': ['restaurant', 'cafe', 'fast_food', 'food', 'bakery'],
    'recreation': ['park', 'recreation', 'gym', 'sports', 'entertainment']
}

matched = {cat: [] for cat in amenity_keywords}
for amenity, count in all_amenities.most_common(35):
    for category, keywords in amenity_keywords.items():
        if any(kw in amenity.lower() for kw in keywords):
            matched[category].append((amenity, count))
            break  # Don't double-count

print('\nMatches by category:')
for category, amenities in matched.items():
    total = sum(count for _, count in amenities)
    print(f'\n{category.upper()} ({total} total):')
    for amenity, count in amenities[:5]:  # Show top 5
        print(f'  - {amenity}: {count}')
    if len(amenities) > 5:
        print(f'  ... and {len(amenities)-5} more')
