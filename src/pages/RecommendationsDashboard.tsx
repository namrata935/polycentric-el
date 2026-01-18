import React, { useState, useMemo } from "react";
import Navigation from "@/components/Navigation";
import { useQuery } from "@tanstack/react-query";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import RecommendationCard from "@/components/RecommendationCard";
import { AlertTriangle, TrendingUp, Info, Target, Loader2, Filter, Grid, List, X } from "lucide-react";

const apiBase = import.meta.env.VITE_API_URL || "http://localhost:5000";

interface Zone {
  zone_lat: number;
  zone_lon: number;
  zone_type: string;
  business_count: number;
  transport_count: number;
  population: number;
  adjusted_zone_score: number;
  business_raw_tags?: any[];
  final_sentiment?: any;
}

interface Recommendation {
  zone_id: string;
  zone_type: string;
  sentiment_score: number;
  sentiment_level: string;
  primary_recommendation: string;
  priority: "critical" | "high" | "medium" | "low";
  context: Record<string, any>;
  recommended_actions: string[];
  focus_areas: string[];
}

/* ========================================================= */
/* ===================== FETCH ZONES ====================== */
/* ========================================================= */

async function fetchZonesWithSentiment(): Promise<Zone[]> {
  try {
    const res = await fetch(`${apiBase}/zones/all`);
    if (!res.ok) throw new Error("Failed to fetch zones");
    const data = await res.json();
    return Array.isArray(data?.zones) ? data.zones : [];
  } catch (err) {
    console.error("Error fetching zones:", err);
    return [];
  }
}

/* ========================================================= */
/* ===================== BATCH FETCH RECOMMENDATIONS ====== */
/* ========================================================= */

async function fetchBatchRecommendations(zones: Zone[]): Promise<Recommendation[]> {
  if (zones.length === 0) return [];

  try {
    const res = await fetch(`${apiBase}/zones/recommendations/batch`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ zones }),
    });
    if (!res.ok) throw new Error("Failed to fetch recommendations");
    const data = await res.json();
    return data.recommendations || [];
  } catch (err) {
    console.error("Error fetching recommendations:", err);
    return [];
  }
}

/* ========================================================= */
/* ===================== MAIN DASHBOARD =================== */
/* ========================================================= */

function RecommendationsDashboard() {
  const [priorityFilter, setPriorityFilter] = useState<string>("all");
  const [sentimentFilter, setSentimentFilter] = useState<string>("all");
  const [zoneTypeFilter, setZoneTypeFilter] = useState<string>("all");
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");

  /* -------- FETCH ZONES -------- */
  const { data: zones = [], isLoading: zonesLoading } = useQuery({
    queryKey: ["zones-dashboard"],
    queryFn: fetchZonesWithSentiment,
  });

  /* -------- FETCH RECOMMENDATIONS -------- */
  const { data: recommendations = [], isLoading: recsLoading } = useQuery({
    queryKey: ["recommendations-batch", zones.length],
    queryFn: () => fetchBatchRecommendations(zones),
    enabled: zones.length > 0,
  });

  /* -------- BUILD ZONE → REC MAP -------- */
  const recMap = useMemo(() => {
    const map = new Map<string, Recommendation>();
    recommendations.forEach((rec) => {
      map.set(rec.zone_id, rec);
    });
    return map;
  }, [recommendations]);

  /* -------- STATISTICS -------- */
  const stats = useMemo(() => {
    const stats = {
      total: recommendations.length,
      critical: 0,
      high: 0,
      medium: 0,
      low: 0,
      byType: { "Opportunity Zone": 0, "Balanced Zone": 0, "Commercial Zone": 0 },
      bySentiment: {
        very_positive: 0,
        positive: 0,
        neutral: 0,
        negative: 0,
        very_negative: 0,
      },
    };

    recommendations.forEach((rec) => {
      stats[rec.priority]++;
      stats.byType[rec.zone_type] = (stats.byType[rec.zone_type] || 0) + 1;
      stats.bySentiment[rec.sentiment_level] =
        (stats.bySentiment[rec.sentiment_level] || 0) + 1;
    });

    return stats;
  }, [recommendations]);

  /* -------- FILTER RECOMMENDATIONS -------- */
  const filteredRecs = useMemo(() => {
    return recommendations.filter((rec) => {
      if (priorityFilter !== "all" && rec.priority !== priorityFilter)
        return false;
      if (sentimentFilter !== "all" && rec.sentiment_level !== sentimentFilter)
        return false;
      if (zoneTypeFilter !== "all" && rec.zone_type !== zoneTypeFilter)
        return false;
      return true;
    });
  }, [recommendations, priorityFilter, sentimentFilter, zoneTypeFilter]);

  const isLoading = zonesLoading || recsLoading;

  const hasActiveFilters = priorityFilter !== "all" || sentimentFilter !== "all" || zoneTypeFilter !== "all";

  const clearAllFilters = () => {
    setPriorityFilter("all");
    setSentimentFilter("all");
    setZoneTypeFilter("all");
  };

  const priorityOptions = [
    { value: 'all', label: 'All', color: 'bg-gray-100 text-gray-700 hover:bg-gray-200', activeColor: 'bg-gray-700 text-white' },
    { value: 'critical', label: 'Critical', color: 'bg-red-50 text-red-700 hover:bg-red-100', activeColor: 'bg-red-600 text-white' },
    { value: 'high', label: 'High', color: 'bg-orange-50 text-orange-700 hover:bg-orange-100', activeColor: 'bg-orange-600 text-white' },
    { value: 'medium', label: 'Medium', color: 'bg-yellow-50 text-yellow-700 hover:bg-yellow-100', activeColor: 'bg-yellow-600 text-white' },
    { value: 'low', label: 'Low', color: 'bg-green-50 text-green-700 hover:bg-green-100', activeColor: 'bg-green-600 text-white' },
  ];

  const sentimentOptions = [
    { value: 'all', label: 'All' },
    { value: 'very_positive', label: 'Very Positive', emoji: '😄' },
    { value: 'positive', label: 'Positive', emoji: '🙂' },
    { value: 'neutral', label: 'Neutral', emoji: '😐' },
    { value: 'negative', label: 'Negative', emoji: '😟' },
    { value: 'very_negative', label: 'Very Negative', emoji: '😢' },
  ];

  const zoneTypeOptions = [
    { value: 'all', label: 'All Zones' },
    { value: 'Opportunity Zone', label: 'Opportunity', icon: '🎯' },
    { value: 'Balanced Zone', label: 'Balanced', icon: '⚖️' },
    { value: 'Commercial Zone', label: 'Commercial', icon: '🏢' },
  ];

  /* ========================================================= */
  /* ==================== RENDER ============================= */
  /* ========================================================= */

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <Navigation />

      <div className="container mx-auto px-4 py-8">
        {/* HEADER */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Recommendations Dashboard</h1>
          <p className="text-gray-600">
            View AI-generated recommendations for all Karnataka zones based on sentiment analysis
          </p>
        </div>

        {/* STATISTICS CARDS */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Total Zones
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total}</div>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-red-500">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-red-600">
                Critical
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{stats.critical}</div>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-orange-500">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-orange-600">
                High
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">{stats.high}</div>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-yellow-500">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-yellow-600">
                Medium
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">{stats.medium}</div>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-green-500">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-green-600">
                Low
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{stats.low}</div>
            </CardContent>
          </Card>
        </div>

        {/* IMPROVED FILTERS */}
        <Card className="mb-8">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Filter className="w-5 h-5 text-blue-600" />
                Filters & View
              </CardTitle>
              {hasActiveFilters && (
                <button
                  onClick={clearAllFilters}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X className="w-4 h-4" />
                  Clear All
                </button>
              )}
            </div>
          </CardHeader>
          
          <CardContent className="space-y-6">
            {/* Priority Filter */}
            <div>
              <label className="text-sm font-semibold text-gray-700 mb-3 block">
                Priority Level
              </label>
              <div className="flex flex-wrap gap-2">
                {priorityOptions.map((opt) => (
                  <button
                    key={opt.value}
                    onClick={() => setPriorityFilter(opt.value)}
                    className={`px-4 py-2.5 rounded-lg font-medium text-sm transition-all duration-200 ${
                      priorityFilter === opt.value
                        ? `${opt.activeColor} shadow-sm ring-2 ring-offset-1`
                        : opt.color
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Sentiment Filter */}
            <div>
              <label className="text-sm font-semibold text-gray-700 mb-3 block">
                Sentiment Level
              </label>
              <div className="flex flex-wrap gap-2">
                {sentimentOptions.map((opt) => (
                  <button
                    key={opt.value}
                    onClick={() => setSentimentFilter(opt.value)}
                    className={`px-4 py-2.5 rounded-lg font-medium text-sm transition-all duration-200 flex items-center gap-2 ${
                      sentimentFilter === opt.value
                        ? "bg-blue-600 text-white shadow-md ring-2 ring-blue-600/20 ring-offset-1"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200 hover:shadow-sm"
                    }`}
                  >
                    {opt.emoji && <span className="text-base">{opt.emoji}</span>}
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Zone Type Filter */}
            <div>
              <label className="text-sm font-semibold text-gray-700 mb-3 block">
                Zone Type
              </label>
              <div className="flex flex-wrap gap-2">
                {zoneTypeOptions.map((opt) => (
                  <button
                    key={opt.value}
                    onClick={() => setZoneTypeFilter(opt.value)}
                    className={`px-4 py-2.5 rounded-lg font-medium text-sm transition-all duration-200 flex items-center gap-2 ${
                      zoneTypeFilter === opt.value
                        ? "bg-blue-600 text-white shadow-md ring-2 ring-blue-600/20 ring-offset-1"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200 hover:shadow-sm"
                    }`}
                  >
                    {opt.icon && <span className="text-base">{opt.icon}</span>}
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            {/* View Mode Toggle */}
            <div className="pt-4 border-t border-gray-100">
              <label className="text-sm font-semibold text-gray-700 mb-3 block">
                View Mode
              </label>
              <div className="inline-flex bg-gray-100 rounded-lg p-1 gap-1">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`px-4 py-2 rounded-md font-medium text-sm transition-all duration-200 flex items-center gap-2 ${
                    viewMode === 'grid'
                      ? 'bg-white text-blue-600 shadow-sm'
                      : 'text-gray-700 hover:text-gray-900'
                  }`}
                >
                  <Grid className="w-4 h-4" />
                  Grid View
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`px-4 py-2 rounded-md font-medium text-sm transition-all duration-200 flex items-center gap-2 ${
                    viewMode === 'list'
                      ? 'bg-white text-blue-600 shadow-sm'
                      : 'text-gray-700 hover:text-gray-900'
                  }`}
                >
                  <List className="w-4 h-4" />
                  List View
                </button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* RESULTS */}
        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2 text-blue-600" />
              <p className="text-gray-600">Loading recommendations...</p>
            </div>
          </div>
        )}

        {!isLoading && filteredRecs.length === 0 && (
          <Card className="text-center py-12">
            <p className="text-gray-500">
              No recommendations found with current filters
            </p>
          </Card>
        )}

        {!isLoading && filteredRecs.length > 0 && (
          <div>
            <p className="text-sm text-gray-600 mb-4">
              Showing {filteredRecs.length} of {stats.total} recommendations
            </p>

            {viewMode === "grid" && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredRecs.map((rec) => (
                  <RecommendationCard key={rec.zone_id} recommendation={rec} />
                ))}
              </div>
            )}

            {viewMode === "list" && (
              <div className="space-y-4">
                {filteredRecs.map((rec) => (
                  <Card key={rec.zone_id} className="hover:shadow-lg transition">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <div>
                          <CardTitle className="text-lg">
                            {rec.zone_type}
                          </CardTitle>
                          <CardDescription>{rec.zone_id}</CardDescription>
                        </div>
                        <div
                          className={`px-3 py-1 rounded-full text-xs font-bold ${
                            rec.priority === "critical"
                              ? "bg-red-100 text-red-800"
                              : rec.priority === "high"
                              ? "bg-orange-100 text-orange-800"
                              : rec.priority === "medium"
                              ? "bg-yellow-100 text-yellow-800"
                              : "bg-green-100 text-green-800"
                          }`}
                        >
                          {rec.priority.toUpperCase()}
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-gray-700 mb-3">
                        {rec.primary_recommendation}
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {rec.focus_areas.map((area) => (
                          <span
                            key={area}
                            className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full"
                          >
                            {area}
                          </span>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default RecommendationsDashboard;