import os
from pathlib import Path

# ==================== PATHS ====================

# Base directory
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
OUTPUT_DIR = BASE_DIR / 'output'

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)

# Input files
ZONES_FILE = DATA_DIR / 'zones_classified.json'
ACCIDENTS_FILE = DATA_DIR / 'karnataka_accidents.csv'

# Output files
SENTIMENT_OUTPUT = OUTPUT_DIR / 'zones_with_multisource_sentiment.json'
SUMMARY_REPORT = OUTPUT_DIR / 'sentiment_analysis_report.json'
REDDIT_CACHE = OUTPUT_DIR / 'reddit_cache.json'

# ==================== ACCIDENT SENTIMENT SETTINGS ====================

ACCIDENT_CONFIG = {
    'search_radius_km': 5.0,           # Search radius for nearby accidents
    'severity_weights': {              # Weight accidents by severity
        'Fatal': 3.0,
        'Grievous Injury': 2.0,
        'Simple Injury': 1.0,
        'Non-Injury (Damage only)': 0.5,
        'Damage': 0.5,
    },
    'karnataka_bounds': {              # Valid coordinate bounds for Karnataka
        'lat_min': 11.5,
        'lat_max': 18.5,
        'lon_min': 74.0,
        'lon_max': 78.5,
    },
    'no_accident_score': 0.7,          # Sentiment when no accidents found
    'scale_factor': 4.0,               # Denominator in log scaling
}

# ==================== REDDIT SENTIMENT SETTINGS ====================

REDDIT_CONFIG = {
    'major_cities': {
        'bengaluru': {
            'lat_range': (12.8, 13.2),
            'lon_range': (77.4, 77.8),
            'subreddit': 'bangalore'
        },
        'mysuru': {
            'lat_range': (12.2, 12.4),
            'lon_range': (76.5, 76.8),
            'subreddit': 'mysore'
        },
        'mangaluru': {
            'lat_range': (12.8, 13.0),
            'lon_range': (74.8, 75.0),
            'subreddit': 'mangalore'
        },
        'hubballi': {
            'lat_range': (15.3, 15.5),
            'lon_range': (75.0, 75.2),
            'subreddit': 'hubli'
        },
    },
    'keywords': [
        'hospital', 'school', 'restaurant', 'traffic', 'transport',
        'market', 'cafe', 'college', 'clinic', 'infrastructure',
        'road', 'bus', 'metro', 'park', 'shopping'
    ],
    'posts_per_city': 100,             # Max posts to scrape per city
    'rate_limit_delay': 1.0,           # Seconds between API calls
    'enable_caching': True,            # Cache Reddit results
}

# ==================== SYNTHETIC SENTIMENT SETTINGS ====================

SYNTHETIC_CONFIG = {
    'amenity_variance': {              # Variance by amenity type
        'hospital': 0.35,
        'clinic': 0.32,
        'restaurant': 0.25,
        'fast_food': 0.28,
        'cafe': 0.22,
        'supermarket': 0.18,
        'school': 0.15,
        'college': 0.20,
        'default': 0.25
    },
    'service_factor_max': 0.3,         # Max contribution from services
    'transport_factor_max': 0.2,       # Max contribution from transport
    'pop_pressure_max': -0.3,          # Max negative from population
    'opportunity_factor_weight': 0.4,  # Weight for opportunity score
    'min_feedbacks': 3,                # Minimum feedback points per zone
    'max_feedbacks': 50,               # Maximum feedback points per zone
    'random_seed': 42,                 # For reproducibility
}

# ==================== INTEGRATION SETTINGS ====================

INTEGRATION_CONFIG = {
    'source_weights': {                # Weights for combining sources
        'reddit': 0.5,                 # 50% weight for real Reddit data
        'accident': 0.3,               # 30% weight for accident proxy
        'synthetic': 0.2,              # 20% weight for synthetic baseline
    },
    'enable_reddit': True,             # Set False to skip Reddit scraping
    'enable_accidents': True,          # Set False to skip accident analysis
    'require_minimum_sources': 1,      # Minimum sources required per zone
}

# ==================== PROCESSING SETTINGS ====================

PROCESSING_CONFIG = {
    'batch_size': 100,                 # Progress update frequency
    'save_intermediate': True,         # Save intermediate results
    'verbose': True,                   # Print detailed progress
    'encoding': 'utf-8',               # File encoding
}

# ==================== API SETTINGS ====================

API_CONFIG = {
    'pushshift_base_url': 'https://api.pushshift.io/reddit/search/submission/',
    'timeout': 10,                     # Request timeout in seconds
    'max_retries': 3,                  # Max retry attempts for failed requests
}

# ==================== VALIDATION THRESHOLDS ====================

VALIDATION_CONFIG = {
    'min_zones_required': 100,         # Minimum zones for valid analysis
    'min_accidents_required': 1000,    # Minimum accidents for valid analysis
    'max_missing_coords_pct': 30,      # Max % of zones with missing coords
    'coordinate_precision': 4,         # Decimal places for coordinates
}

# ==================== EXPORT SETTINGS ====================

EXPORT_CONFIG = {
    'json_indent': 2,                  # Indentation for JSON files
    'ensure_ascii': False,             # Allow Unicode characters
    'include_metadata': True,          # Include processing metadata
    'timestamp_format': '%Y-%m-%d %H:%M:%S',
}

# ==================== HELPER FUNCTIONS ====================

def get_file_path(file_type: str) -> Path:
    """Get file path by type."""
    paths = {
        'zones': ZONES_FILE,
        'accidents': ACCIDENTS_FILE,
        'output': SENTIMENT_OUTPUT,
        'report': SUMMARY_REPORT,
        'reddit_cache': REDDIT_CACHE,
    }
    return paths.get(file_type)

def validate_paths():
    """Validate that required paths exist."""
    issues = []
    
    if not ZONES_FILE.exists():
        issues.append(f"Missing: {ZONES_FILE}")
    
    if INTEGRATION_CONFIG['enable_accidents'] and not ACCIDENTS_FILE.exists():
        issues.append(f"Missing: {ACCIDENTS_FILE}")
    
    if issues:
        print("⚠ Configuration Issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    
    return True

def print_config_summary():
    """Print configuration summary."""
    print("="*70)
    print("SENTIMENT ANALYSIS CONFIGURATION")
    print("="*70)
    print(f"\nInput Files:")
    print(f"  Zones:     {ZONES_FILE}")
    print(f"  Accidents: {ACCIDENTS_FILE}")
    print(f"\nOutput Files:")
    print(f"  Results:   {SENTIMENT_OUTPUT}")
    print(f"  Report:    {SUMMARY_REPORT}")
    print(f"\nProcessing Settings:")
    print(f"  Reddit enabled:    {INTEGRATION_CONFIG['enable_reddit']}")
    print(f"  Accidents enabled: {INTEGRATION_CONFIG['enable_accidents']}")
    print(f"  Random seed:       {SYNTHETIC_CONFIG['random_seed']}")
    print(f"\nAccident Settings:")
    print(f"  Search radius:     {ACCIDENT_CONFIG['search_radius_km']} km")
    print(f"\nReddit Settings:")
    print(f"  Cities tracked:    {len(REDDIT_CONFIG['major_cities'])}")
    print(f"  Posts per city:    {REDDIT_CONFIG['posts_per_city']}")
    print("="*70 + "\n")

if __name__ == '__main__':
    print_config_summary()
    if validate_paths():
        print("✓ All required files found!")
    else:
        print("✗ Some required files are missing.")
        print("\nPlease ensure:")
        print("  1. zones_classified.json is in the data/ folder")
        print("  2. karnataka_accidents.csv is in the data/ folder")