/**
 * INTEGRATION GUIDE: Micro-Recommendation System
 * ===============================================
 * 
 * This file shows how to integrate the recommendation system into
 * your existing OpportunityZones component and other pages.
 */

import React, { useState } from "react";
import { useZoneRecommendation, useBatchRecommendations } from "@/hooks/use-recommendations";
import RecommendationCard from "@/components/RecommendationCard";
import { Zone } from "@/types/zones";

/* ========================================================= */
/* USAGE EXAMPLE 1: Single Zone Recommendation              */
/* ========================================================= */

export function ZoneDetailWithRecommendation({ zone }: { zone: Zone }) {
  const { data: recommendation, isLoading, error } = useZoneRecommendation(zone);

  return (
    <div className="space-y-4">
      {/* Zone Details */}
      <div className="p-4 bg-gray-50 rounded-lg">
        <h3 className="font-semibold text-lg mb-2">{zone.zone_type}</h3>
        <p className="text-sm text-gray-600">
          Location: {zone.zone_lat?.toFixed(2)}, {zone.zone_lon?.toFixed(2)}
        </p>
        <p className="text-sm text-gray-600">
          Businesses: {zone.business_count} | Transport: {zone.transport_count}
        </p>
      </div>

      {/* Recommendation */}
      <RecommendationCard
        recommendation={recommendation || null}
        isLoading={isLoading}
        error={error}
      />
    </div>
  );
}

/* ========================================================= */
/* USAGE EXAMPLE 2: Batch Recommendations with Priority View */
/* ========================================================= */

export function BatchRecommendationsView({ zones }: { zones: Zone[] }) {
  const { data: batchData, isLoading } = useBatchRecommendations(zones);
  const [selectedPriority, setSelectedPriority] = useState<string>("all");

  if (isLoading) {
    return <div className="p-4">Loading recommendations...</div>;
  }

  if (!batchData) {
    return <div className="p-4">No recommendations available</div>;
  }

  const priorityOptions = [
    { value: "all", label: "All Zones", count: batchData.total_zones },
    { value: "critical", label: "Critical", count: batchData.summary.critical },
    { value: "high", label: "High Priority", count: batchData.summary.high },
    { value: "medium", label: "Medium Priority", count: batchData.summary.medium },
    { value: "low", label: "Low Priority", count: batchData.summary.low },
  ];

  const displayedRecs =
    selectedPriority === "all"
      ? batchData.recommendations
      : batchData.by_priority[selectedPriority];

  return (
    <div className="space-y-6">
      {/* Priority Filter */}
      <div className="flex flex-wrap gap-2">
        {priorityOptions.map((opt) => (
          <button
            key={opt.value}
            onClick={() => setSelectedPriority(opt.value)}
            className={`px-4 py-2 rounded-lg font-medium text-sm transition ${
              selectedPriority === opt.value
                ? "bg-blue-600 text-white"
                : "bg-gray-200 text-gray-700 hover:bg-gray-300"
            }`}
          >
            {opt.label} ({opt.count})
          </button>
        ))}
      </div>

      {/* Recommendations List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {displayedRecs.map((rec) => (
          <RecommendationCard key={rec.zone_id} recommendation={rec} />
        ))}
      </div>

      {displayedRecs.length === 0 && (
        <p className="text-center text-gray-500 py-8">
          No recommendations in this priority level
        </p>
      )}
    </div>
  );
}

/* ========================================================= */
/* USAGE EXAMPLE 3: Integration in OpportunityZones Map     */
/* ========================================================= */

export function MapPopupWithRecommendation({ zone }: { zone: Zone }) {
  const { data: recommendation } = useZoneRecommendation(zone);

  return (
    <div className="w-64 space-y-3">
      <div>
        <h4 className="font-semibold text-sm">{zone.zone_type}</h4>
        <p className="text-xs text-gray-600">
          {zone.zone_lat?.toFixed(4)}, {zone.zone_lon?.toFixed(4)}
        </p>
      </div>

      {recommendation && (
        <div className={`p-2 rounded text-sm border-l-4 ${
          recommendation.priority === 'critical' ? 'border-red-500 bg-red-50' :
          recommendation.priority === 'high' ? 'border-orange-500 bg-orange-50' :
          recommendation.priority === 'medium' ? 'border-yellow-500 bg-yellow-50' :
          'border-green-500 bg-green-50'
        }`}>
          <p className="font-semibold text-xs mb-1">
            {recommendation.priority.toUpperCase()} PRIORITY
          </p>
          <p className="text-xs">{recommendation.primary_recommendation}</p>
        </div>
      )}

      <div className="grid grid-cols-2 gap-2 text-xs">
        <div>
          <p className="text-gray-500 font-semibold">Businesses</p>
          <p>{zone.business_count}</p>
        </div>
        <div>
          <p className="text-gray-500 font-semibold">Transport</p>
          <p>{zone.transport_count}</p>
        </div>
      </div>
    </div>
  );
}

/* ========================================================= */
/* USAGE EXAMPLE 4: Action-based Filtering & Display        */
/* ========================================================= */

export function ActionCentricView({ zones }: { zones: Zone[] }) {
  const { data: batchData } = useBatchRecommendations(zones);
  const [selectedAction, setSelectedAction] = useState<string | null>(null);

  if (!batchData) return null;

  // Collect all unique actions across recommendations
  const allActions = Array.from(
    new Set(
      batchData.recommendations.flatMap((r) => r.recommended_actions)
    )
  );

  // Filter recommendations by selected action
  const filteredRecs = selectedAction
    ? batchData.recommendations.filter((r) =>
        r.recommended_actions.includes(selectedAction)
      )
    : batchData.recommendations;

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-3">Focus Areas</h3>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setSelectedAction(null)}
            className={`px-4 py-2 rounded-lg font-medium text-sm ${
              selectedAction === null
                ? "bg-blue-600 text-white"
                : "bg-gray-200"
            }`}
          >
            All Zones
          </button>
          {allActions.map((action) => (
            <button
              key={action}
              onClick={() => setSelectedAction(action)}
              className={`px-4 py-2 rounded-lg font-medium text-sm capitalize ${
                selectedAction === action
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200"
              }`}
            >
              {action.replace(/_/g, " ")}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {filteredRecs.map((rec) => (
          <RecommendationCard key={rec.zone_id} recommendation={rec} />
        ))}
      </div>

      <p className="text-sm text-gray-600">
        Showing {filteredRecs.length} of {batchData.recommendations.length} zones
      </p>
    </div>
  );
}

/* ========================================================= */
/* HOW TO USE IN YOUR COMPONENTS                            */
/* ========================================================= */

/*
 * 1. FOR SINGLE ZONE DETAIL PAGE:
 *    <ZoneDetailWithRecommendation zone={selectedZone} />
 *
 * 2. FOR PRIORITY-BASED DASHBOARD:
 *    <BatchRecommendationsView zones={allZones} />
 *
 * 3. FOR MAP POPUP:
 *    Use <MapPopupWithRecommendation /> inside map marker popup
 *
 * 4. FOR ACTION-CENTRIC MANAGEMENT:
 *    <ActionCentricView zones={allZones} />
 *
 * 5. IN EXISTING OpportunityZones.tsx:
 *    - Add state for selected zone
 *    - Show RecommendationCard when zone is clicked
 *    - Add priority filter controls
 */
