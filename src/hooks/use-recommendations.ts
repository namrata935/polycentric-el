import { useQuery, UseQueryResult } from "@tanstack/react-query";

export interface Recommendation {
  zone_id: string;
  zone_type: string;
  sentiment_score: number;
  sentiment_level: string;
  primary_recommendation: string;
  all_recommendations: Array<{
    text: string;
    action: string;
    focus: string[];
  }>;
  priority: "critical" | "high" | "medium" | "low";
  context: {
    business_density: string;
    transport_access: string;
    population_level: string;
    sentiment_trend: string;
    amenity_gaps: Record<string, string>;
  };
  recommended_actions: string[];
  focus_areas: string[];
}

export interface BatchRecommendationsResponse {
  status: string;
  total_zones: number;
  recommendations: Recommendation[];
  by_priority: Record<string, Recommendation[]>;
  summary: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
}

const apiBase = import.meta.env.VITE_API_URL || "http://localhost:5000";

/**
 * Fetch recommendation for a single zone
 */
export function useZoneRecommendation(zone: any): UseQueryResult<Recommendation | null> {
  // Generate query key only if zone is valid to avoid accessing properties of null
  const isValidZone = zone && zone.zone_lat && zone.zone_lon;
  
  return useQuery({
    queryKey: isValidZone ? ["zone-recommendation", zone.zone_lat, zone.zone_lon] : ["zone-recommendation", null],
    queryFn: async () => {
      if (!isValidZone) return null;
      const res = await fetch(`${apiBase}/zones/recommendations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(zone),
      });
      if (!res.ok) throw new Error("Failed to fetch recommendation");
      const data = await res.json();
      return data.recommendation;
    },
    enabled: !!isValidZone,
  });
}

/**
 * Fetch recommendations for multiple zones
 */
export function useBatchRecommendations(
  zones: any[],
  enabled: boolean = true
): UseQueryResult<BatchRecommendationsResponse> {
  return useQuery({
    queryKey: ["batch-recommendations", zones?.length],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/zones/recommendations/batch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ zones }),
      });
      if (!res.ok) throw new Error("Failed to fetch recommendations");
      return res.json();
    },
    enabled: enabled && Array.isArray(zones) && zones.length > 0,
  });
}
