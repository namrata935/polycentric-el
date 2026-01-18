"""
Micro-Recommendation Engine
============================

Provides intelligent recommendations based on:
1. Zone Type (Opportunity, Balanced, Commercial)
2. Sentiment Analysis (positive, negative, neutral)
3. Key Amenity Gaps (transport, businesses, etc.)
4. Development Potential

Rules-based system that generates actionable insights for stakeholders.
"""

from typing import Dict, Any, List, Tuple
from enum import Enum


class SentimentLevel(Enum):
    """Sentiment classification levels"""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class RecommendationPriority(Enum):
    """Priority level for recommendations"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class MicroRecommendationEngine:
    """
    Generates targeted micro-recommendations for zones based on
    multi-dimensional analysis.
    """

    def __init__(self):
        """Initialize recommendation rules and patterns"""
        self.amenity_keywords = {
            'transport': ['bus', 'metro', 'station', 'railway', 'transit', 'transit_node', 'taxi', 'parking', 'airport'],
            'healthcare': ['hospital', 'clinic', 'health', 'pharmacy', 'doctor', 'medical', 'dental'],
            'education': ['school', 'college', 'university', 'education', 'prep', 'driving', 'training'],
            'food': ['restaurant', 'cafe', 'fast_food', 'food', 'bakery', 'ice_cream', 'bar', 'pub'],
        }

    # ==================== SENTIMENT EXTRACTION ====================

    def categorize_sentiment(self, sentiment_score: float) -> SentimentLevel:
        """Convert sentiment score to category"""
        if sentiment_score >= 0.5:
            return SentimentLevel.VERY_POSITIVE
        elif sentiment_score >= 0.2:
            return SentimentLevel.POSITIVE
        elif sentiment_score >= -0.2:
            return SentimentLevel.NEUTRAL
        elif sentiment_score >= -0.5:
            return SentimentLevel.NEGATIVE
        else:
            return SentimentLevel.VERY_NEGATIVE

    def extract_amenity_gaps(self, zone: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identify missing or weak amenity categories in zone.

        Returns dict with amenity strength scores.
        """
        gaps = {}

        # Extract amenities from business_raw_tags
        amenities = {}
        business_tags = zone.get('business_raw_tags', [])

        if isinstance(business_tags, list):
            for tag in business_tags:
                if isinstance(tag, dict):
                    amenity_type = tag.get('amenity', 'unknown')
                    amenities[amenity_type] = amenities.get(amenity_type, 0) + 1

        # Categorize amenities and identify gaps
        category_counts = {cat: 0 for cat in self.amenity_keywords}

        for amenity_type, count in amenities.items():
            for category, keywords in self.amenity_keywords.items():
                if any(kw in amenity_type.lower() for kw in keywords):
                    category_counts[category] += count
                    break  # Don't double-count amenities

        # ✅ NEW: Use actual transport_count from zone data if businesses don't have transport
        if category_counts['transport'] == 0 and zone.get('transport_count', 0) > 0:
            category_counts['transport'] = int(zone.get('transport_count', 0))

        # ✅ NEW: Boost counts with zone-level metrics if all amenities are 0
        if sum(category_counts.values()) == 0:
            # Zone has businesses but no recognized amenities - apply fallback scoring
            business_count = zone.get('business_count', 0)
            population = zone.get('population', 0)
            
            if business_count > 20:
                category_counts['food'] += 3
            if business_count > 10:
                category_counts['healthcare'] += 2
                category_counts['education'] += 2

        # Calculate gap strength (0-1, where 0 = gap exists)
        max_count = max(category_counts.values()) if category_counts.values() else 1
        for category, count in category_counts.items():
            gaps[category] = {
                'strength': count / max(max_count, 1),
                'count': int(count)
            }

        return gaps

    def extract_sentiment_issues(self, zone: Dict[str, Any]) -> List[str]:
        """Extract key issues from sentiment breakdown"""
        issues = []
        
        sentiment_data = zone.get('final_sentiment', {})
        source_breakdown = sentiment_data.get('source_breakdown', {})
        
        # Analyze accident data for safety issues
        accident_data = source_breakdown.get('accident_proxy', {})
        if accident_data.get('accident_count', 0) > 0:
            severity = accident_data.get('severity_breakdown', {})
            if severity.get('Fatal', 0) > 0 or severity.get('Grievous Injury', 0) > 0:
                issues.append('high_accident_severity')
            else:
                issues.append('moderate_safety_concerns')
        
        # Analyze synthetic sentiment for service gaps
        synthetic_data = source_breakdown.get('synthetic', {})
        if synthetic_data.get('mean', 0) < -0.3:
            issues.append('poor_service_availability')
        
        return issues

    # ==================== RECOMMENDATION RULES ====================

    def generate_recommendations(self, zone: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate micro-recommendations for a zone.

        Args:
            zone: Zone data with sentiment analysis

        Returns:
            Dict with recommendations, priority, and reasoning
        """

        zone_type = zone.get('zone_type', 'Unknown')
        sentiment_score = zone.get('final_sentiment', {}).get('mean', 0)
        sentiment_level = self.categorize_sentiment(sentiment_score)

        # Extract context
        amenity_gaps = self.extract_amenity_gaps(zone)
        sentiment_issues = self.extract_sentiment_issues(zone)
        business_count = zone.get('business_count', 0)
        transport_count = zone.get('transport_count', 0)
        population = zone.get('population', 0)

        # Generate recommendations based on patterns
        recommendations = []
        priority = RecommendationPriority.MEDIUM

        # ===================== OPPORTUNITY ZONES =====================
        if zone_type == "Opportunity Zone":
            if sentiment_level == SentimentLevel.VERY_NEGATIVE:
                priority = RecommendationPriority.CRITICAL
                recommendations.append({
                    'text': 'Critical development needed: High accident rate and poor services detected. Prioritize safety improvements before expansion.',
                    'action': 'improve_safety_first',
                    'focus': ['infrastructure', 'safety']
                })
            elif sentiment_level == SentimentLevel.NEGATIVE:
                if 'high_accident_severity' in sentiment_issues:
                    recommendations.append({
                        'text': 'Consider improving connectivity and safety infrastructure before large-scale development.',
                        'action': 'improve_connectivity',
                        'focus': ['transport', 'safety']
                    })
                    priority = RecommendationPriority.HIGH
                elif amenity_gaps['transport']['strength'] < 0.3:
                    recommendations.append({
                        'text': 'Limited transport access detected. Develop transit connectivity to unlock area potential.',
                        'action': 'expand_transit',
                        'focus': ['transport']
                    })
                    priority = RecommendationPriority.HIGH
                else:
                    recommendations.append({
                        'text': 'Area has development potential. Focus on improving service coverage (healthcare, education, retail).',
                        'action': 'expand_services',
                        'focus': ['services']
                    })
            elif sentiment_level == SentimentLevel.NEUTRAL:
                recommendations.append({
                    'text': 'Moderate potential for mixed-use development. Consider targeted improvements in underserved amenities.',
                    'action': 'mixed_development',
                    'focus': ['mixed_use']
                })
                priority = RecommendationPriority.MEDIUM
            elif sentiment_level in [SentimentLevel.POSITIVE, SentimentLevel.VERY_POSITIVE]:
                recommendations.append({
                    'text': 'Strong opportunity: Area shows positive trends. Recommended for targeted development initiatives.',
                    'action': 'accelerate_development',
                    'focus': ['expansion']
                })
                priority = RecommendationPriority.LOW

        # ===================== BALANCED ZONES =====================
        elif zone_type == "Balanced Zone":
            if sentiment_level == SentimentLevel.VERY_POSITIVE:
                recommendations.append({
                    'text': 'Area is well-balanced and sentiment is strong. Ideal for mixed-use expansion and community projects.',
                    'action': 'mixed_use_expansion',
                    'focus': ['expansion', 'community']
                })
                priority = RecommendationPriority.LOW
            elif sentiment_level == SentimentLevel.POSITIVE:
                recommendations.append({
                    'text': 'Positive sentiment with balanced amenities. Consider selective expansion in underserved categories.',
                    'action': 'selective_expansion',
                    'focus': ['targeted_expansion']
                })
                priority = RecommendationPriority.LOW
            elif sentiment_level == SentimentLevel.NEUTRAL:
                recommendations.append({
                    'text': 'Stable area with mixed sentiment. Maintain current service levels while monitoring key indicators.',
                    'action': 'maintain_monitor',
                    'focus': ['monitoring']
                })
                priority = RecommendationPriority.MEDIUM
            elif sentiment_level == SentimentLevel.NEGATIVE:
                recommendations.append({
                    'text': 'Balanced zone showing negative sentiment. Address community concerns and improve service quality.',
                    'action': 'improve_services',
                    'focus': ['service_quality']
                })
                priority = RecommendationPriority.MEDIUM
            else:  # VERY_NEGATIVE
                recommendations.append({
                    'text': 'Urgent attention needed: Balanced zone declining. Implement comprehensive improvement plan.',
                    'action': 'comprehensive_improvement',
                    'focus': ['urgent_improvement']
                })
                priority = RecommendationPriority.HIGH

        # ===================== COMMERCIAL ZONES =====================
        else:  # Commercial Zone
            if sentiment_level == SentimentLevel.VERY_NEGATIVE:
                recommendations.append({
                    'text': 'Commercial zone deteriorating: High saturation with negative sentiment. Plan gradual diversification.',
                    'action': 'diversify_services',
                    'focus': ['diversification']
                })
                priority = RecommendationPriority.HIGH
            elif sentiment_level == SentimentLevel.NEGATIVE:
                recommendations.append({
                    'text': 'Commercial zone showing strain. Consider traffic management and service diversification.',
                    'action': 'traffic_management',
                    'focus': ['traffic', 'services']
                })
                priority = RecommendationPriority.MEDIUM
            elif sentiment_level == SentimentLevel.NEUTRAL:
                recommendations.append({
                    'text': 'Mature commercial zone: Maintain current operations while exploring adjacent underserved areas.',
                    'action': 'maintain_adjacent',
                    'focus': ['adjacent_markets']
                })
                priority = RecommendationPriority.LOW
            else:  # POSITIVE or VERY_POSITIVE
                recommendations.append({
                    'text': 'Strong commercial performance: Well-managed with positive sentiment. Consider controlled expansion.',
                    'action': 'controlled_expansion',
                    'focus': ['expansion']
                })
                priority = RecommendationPriority.LOW

        # ===================== AMENITY-SPECIFIC INSIGHTS =====================
        weakest_amenity = min(amenity_gaps.items(), key=lambda x: x[1]['strength'])
        if weakest_amenity[1]['strength'] < 0.2:
            recommendations.append({
                'text': f"Significant gap in {weakest_amenity[0].replace('_', ' ')} infrastructure. Consider targeted investment.",
                'action': f'improve_{weakest_amenity[0]}',
                'focus': [weakest_amenity[0]]
            })

        # ===================== CONTEXT INSIGHTS =====================
        
        # Determine transport access level based on both amenity gaps and direct transport_count
        transport_strength = amenity_gaps.get('transport', {}).get('strength', 0)
        if transport_strength == 0 and transport_count == 0:
            transport_access = 'poor'
        elif transport_strength < 0.3 or transport_count < 2:
            transport_access = 'limited'
        elif transport_strength < 0.6 or transport_count < 5:
            transport_access = 'moderate'
        else:
            transport_access = 'good'
        
        insights = {
            'business_density': 'high' if business_count > 50 else 'medium' if business_count > 10 else 'low',
            'transport_access': transport_access,
            'population_level': 'high' if population > 2000 else 'medium' if population > 500 else 'low',
            'sentiment_trend': sentiment_level.value,
            'amenity_gaps': {k: f"{v['strength']:.0%}" for k, v in amenity_gaps.items()}
        }

        return {
            'zone_id': f"lat_{zone.get('zone_lat')}_lon_{zone.get('zone_lon')}",
            'zone_type': zone_type,
            'sentiment_score': round(sentiment_score, 3),
            'sentiment_level': sentiment_level.value,
            'primary_recommendation': recommendations[0]['text'] if recommendations else "Monitor zone conditions.",
            'all_recommendations': recommendations,
            'priority': priority.value,
            'context': insights,
            'recommended_actions': [r['action'] for r in recommendations],
            'focus_areas': list(set(area for r in recommendations for area in r.get('focus', [])))
        }


# ==================== UTILITY FUNCTION ====================

def get_zone_recommendations(zone: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to generate recommendations"""
    engine = MicroRecommendationEngine()
    return engine.generate_recommendations(zone)
