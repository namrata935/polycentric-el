import React, { useState } from "react";
import Navigation from "@/components/Navigation";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { MapContainer, TileLayer, Popup, Circle } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { useQuery } from "@tanstack/react-query";
import ErrorBoundary from "@/components/ErrorBoundary";
import { Info, Eye, EyeOff } from "lucide-react";

/* ---------------- TYPES ---------------- */

type Zone = {
  zone_lat?: number;
  zone_lon?: number;
  business_count?: number;
  transport_count?: number;
  population?: number;
  zone_type?: "Commercial Zone" | "Balanced Zone" | "Opportunity Zone";
  adjusted_zone_score?: number;
};

const apiBase = import.meta.env.VITE_API_URL || "http://localhost:5000";

/* ---------------- HELPERS ---------------- */

const zoneColor = (zoneType?: string) => {
  if (zoneType === "Commercial Zone") return "#ef4444"; // red
  if (zoneType === "Balanced Zone") return "#22c55e";   // green
  return "#3b82f6";                                     // blue (Opportunity)
};

const getScoreLabel = (score: number) => {
  if (score >= 0.7) return "High saturation";
  if (score >= 0.4) return "Moderate saturation";
  return "Low saturation";
};

const karnatakaCenter: L.LatLngExpression = [15.3173, 75.7139];

/* ---------------- API ---------------- */

async function fetchZones(): Promise<Zone[]> {
  const res = await fetch(`${apiBase}/zones/all`);
  if (!res.ok) throw new Error("Failed to fetch zones");
  const data = await res.json();
  return Array.isArray(data?.zones) ? data.zones : [];
}

/* ========================================================= */
/* ===================== MAIN PAGE ========================= */
/* ========================================================= */

function OpportunityZonesContent() {
  const { data: zonesData = [], isLoading, error } = useQuery({
    queryKey: ["zones", "force-refresh"],
    queryFn: fetchZones,
  });

  const [visibleZoneTypes, setVisibleZoneTypes] = useState<Set<string>>(
    new Set(["Commercial Zone", "Balanced Zone", "Opportunity Zone"])
  );

  const [showScoreInfo, setShowScoreInfo] = useState(false);
  const [legendCollapsed, setLegendCollapsed] = useState(false);

  /* ---------------- COUNTS (FOR SUMMARY) ---------------- */

  const opportunityCount = zonesData.filter(
    (z) => z.zone_type === "Opportunity Zone"
  ).length;

  const balancedCount = zonesData.filter(
    (z) => z.zone_type === "Balanced Zone"
  ).length;

  const commercialCount = zonesData.filter(
    (z) => z.zone_type === "Commercial Zone"
  ).length;

  const totalZones = zonesData.length;

  const filteredZones = zonesData.filter((z) =>
    visibleZoneTypes.has(z.zone_type || "")
  );

  /* ---------------- MAP CENTER ---------------- */

  const center: L.LatLngExpression =
    zonesData.length > 0
      ? [
          zonesData.reduce((s, z) => s + (z.zone_lat ?? 0), 0) / zonesData.length,
          zonesData.reduce((s, z) => s + (z.zone_lon ?? 0), 0) / zonesData.length,
        ]
      : karnatakaCenter;

  const toggleZoneType = (zoneType: string) => {
    setVisibleZoneTypes((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(zoneType)) {
        newSet.delete(zoneType);
      } else {
        newSet.add(zoneType);
      }
      return newSet;
    });
  };

  // ✅ NEW: Show All / Clear All
  const showAll = () => {
    setVisibleZoneTypes(new Set(["Commercial Zone", "Balanced Zone", "Opportunity Zone"]));
  };

  const clearAll = () => {
    setVisibleZoneTypes(new Set());
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <div className="container mx-auto px-6 py-8">
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading zones…</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <div className="p-8 text-red-500">Failed to load zones</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation />

      <div className="container mx-auto px-6 py-8">
        {/* HEADER */}
        <div className="mb-8">
          <h1 className="font-heading text-4xl font-bold mb-2">
            Opportunity Zone Analysis
          </h1>
          <p className="text-muted-foreground text-lg">
            Visualizing commercial saturation and future growth potential across Karnataka.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* ZONE LEGEND (STICKY SIDEBAR) */}
          <div className="lg:col-span-1">
            <Card className="shadow-lg lg:sticky lg:top-6">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-lg">Zone Types</CardTitle>
                    <CardDescription>Click to filter map</CardDescription>
                  </div>
                  <button
                    onClick={() => setLegendCollapsed(!legendCollapsed)}
                    className="lg:hidden p-2 hover:bg-gray-100 rounded"
                  >
                    {legendCollapsed ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                  </button>
                </div>
              </CardHeader>
              
              {!legendCollapsed && (
                <CardContent className="space-y-4">
                  {/* ✅ NEW: Filter Count + Quick Actions */}
                  <div className="flex items-center justify-between text-xs text-gray-600 pb-2 border-b">
                    <span>
                      Showing <span className="font-semibold text-gray-900">{filteredZones.length}</span> of <span className="font-semibold text-gray-900">{totalZones}</span> zones
                    </span>
                  </div>

                  <div className="flex gap-2">
                    <button
                      onClick={showAll}
                      className="flex-1 px-3 py-1.5 text-xs font-medium bg-blue-50 text-blue-700 rounded hover:bg-blue-100 transition-colors"
                    >
                      Show All
                    </button>
                    <button
                      onClick={clearAll}
                      className="flex-1 px-3 py-1.5 text-xs font-medium bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                    >
                      Clear All
                    </button>
                  </div>

                  {/* Opportunity Zone */}
                  <div
                    onClick={() => toggleZoneType("Opportunity Zone")}
                    className={`p-3 rounded-lg border-2 cursor-pointer transition-all hover:shadow-md hover:-translate-y-0.5 ${
                      visibleZoneTypes.has("Opportunity Zone")
                        ? "border-blue-500 bg-blue-50"
                        : "border-gray-200 bg-gray-50 opacity-50"
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className="w-4 h-4 rounded-full bg-blue-500 mt-1 flex-shrink-0"></div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <h3 className="font-semibold text-sm text-blue-700">
                            Opportunity Zone
                          </h3>
                          <span className="text-xs font-semibold text-blue-600 bg-blue-100 px-2 py-0.5 rounded-full">
                            {opportunityCount}
                          </span>
                        </div>
                        <p className="text-xs text-gray-600 mt-1">
                          Low current saturation with high future growth potential.
                        </p>
                        <p className="text-xs font-medium text-blue-600 mt-1">
                          💡 Best for: New businesses & startups
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Balanced Zone */}
                  <div
                    onClick={() => toggleZoneType("Balanced Zone")}
                    className={`p-3 rounded-lg border-2 cursor-pointer transition-all hover:shadow-md hover:-translate-y-0.5 ${
                      visibleZoneTypes.has("Balanced Zone")
                        ? "border-green-500 bg-green-50"
                        : "border-gray-200 bg-gray-50 opacity-50"
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className="w-4 h-4 rounded-full bg-green-500 mt-1 flex-shrink-0"></div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <h3 className="font-semibold text-sm text-green-700">
                            Balanced Zone
                          </h3>
                          <span className="text-xs font-semibold text-green-600 bg-green-100 px-2 py-0.5 rounded-full">
                            {balancedCount}
                          </span>
                        </div>
                        <p className="text-xs text-gray-600 mt-1">
                          Moderate business & transport availability with stable population.
                        </p>
                        <p className="text-xs font-medium text-green-600 mt-1">
                          📊 Best for: Steady expansion
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Commercial Zone */}
                  <div
                    onClick={() => toggleZoneType("Commercial Zone")}
                    className={`p-3 rounded-lg border-2 cursor-pointer transition-all hover:shadow-md hover:-translate-y-0.5 ${
                      visibleZoneTypes.has("Commercial Zone")
                        ? "border-red-500 bg-red-50"
                        : "border-gray-200 bg-gray-50 opacity-50"
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className="w-4 h-4 rounded-full bg-red-500 mt-1 flex-shrink-0"></div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <h3 className="font-semibold text-sm text-red-700">
                            Commercial Zone
                          </h3>
                          <span className="text-xs font-semibold text-red-600 bg-red-100 px-2 py-0.5 rounded-full">
                            {commercialCount}
                          </span>
                        </div>
                        <p className="text-xs text-gray-600 mt-1">
                          High business concentration with strong transport & footfall.
                        </p>
                        <p className="text-xs font-medium text-red-600 mt-1">
                          🏪 Best for: Retail & services
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* SCORE EXPLANATION */}
                  <div className="pt-4 border-t">
                    <button
                      onClick={() => setShowScoreInfo(!showScoreInfo)}
                      className="flex items-center gap-2 text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors"
                    >
                      <Info className="w-4 h-4" />
                      How is zone score calculated?
                    </button>
                    {showScoreInfo && (
                      <div className="mt-3 p-3 bg-gray-50 rounded-lg text-xs text-gray-600 space-y-1 animate-in fade-in duration-200">
                        <p>Zone scores range from 0 to 1 based on:</p>
                        <ul className="list-disc list-inside space-y-1 ml-2">
                          <li>Population density weight</li>
                          <li>Business concentration</li>
                          <li>Transport accessibility</li>
                          <li>Opportunity bias factor</li>
                        </ul>
                        <p className="pt-2 italic">
                          Higher scores indicate better-established zones, while lower scores suggest emerging opportunities.
                        </p>
                      </div>
                    )}
                  </div>
                </CardContent>
              )}
            </Card>
          </div>

          {/* MAP + SUMMARY */}
          <div className="lg:col-span-3 space-y-6">
            {/* MAP */}
            <Card className="shadow-lg">
              <CardContent className="p-6">
                <div className="relative w-full h-[520px] rounded-lg overflow-hidden border">
                  {zonesData.length === 0 ? (
                    <div className="flex items-center justify-center h-full">
                      No zone data available
                    </div>
                  ) : (
                    <>
                      <MapContainer
                        center={center as L.LatLngExpression}
                        zoom={8}
                        style={{ height: "100%", width: "100%" }}
                      >
                        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

                        {filteredZones.map((zone, idx) => {
                          if (
                            typeof zone.zone_lat !== "number" ||
                            typeof zone.zone_lon !== "number"
                          )
                            return null;

                          const score = zone.adjusted_zone_score ?? 0;

                          return (
                            <Circle
                              key={idx}
                              center={[zone.zone_lat, zone.zone_lon] as L.LatLngExpression}
                              radius={6500}
                              pathOptions={{
                                color: zoneColor(zone.zone_type),
                                fillColor: zoneColor(zone.zone_type),
                                fillOpacity: 0.55,
                                weight: 2,
                              }}
                            >
                              <Popup>
                                <div className="text-sm space-y-1">
                                  <b>{zone.zone_type}</b>
                                  <div>
                                    Score: {score.toFixed(2)} <span className="text-gray-500">({getScoreLabel(score)})</span>
                                  </div>
                                  <div className="w-full bg-gray-200 rounded-full h-1.5 my-1">
                                    <div
                                      className="h-1.5 rounded-full"
                                      style={{
                                        width: `${score * 100}%`,
                                        backgroundColor: zoneColor(zone.zone_type),
                                      }}
                                    ></div>
                                  </div>
                                  <div>
                                    Population: {zone.population?.toLocaleString() ?? "—"}
                                  </div>
                                  <div>Businesses: {zone.business_count ?? 0}</div>
                                  <div>Transport: {zone.transport_count ?? 0}</div>
                                </div>
                              </Popup>
                            </Circle>
                          );
                        })}
                      </MapContainer>

                      {/* ✅ NEW: Empty State Overlay */}
                      {filteredZones.length === 0 && (
                        <div className="absolute inset-0 flex items-center justify-center bg-white/95 z-[1000]">
                          <div className="text-center p-6">
                            <EyeOff className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                            <p className="text-gray-600 font-medium">No zones selected</p>
                            <p className="text-sm text-gray-500 mt-1">Click a zone type in the legend to display</p>
                            <button
                              onClick={showAll}
                              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                            >
                              Show All Zones
                            </button>
                          </div>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* ENHANCED SUMMARY WITH INSIGHTS */}
            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle>Zone Distribution Insights</CardTitle>
                <CardDescription>
                  Opportunity-biased classification (future-oriented)
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Stats Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div className="p-4 bg-blue-50 rounded-lg border border-blue-200 transition-all hover:shadow-md">
                    <div className="text-2xl font-bold text-blue-700">
                      {opportunityCount}
                    </div>
                    <div className="text-xs text-blue-600 font-medium mt-1">
                      Opportunity Zones
                    </div>
                    <div className="text-xs text-gray-600 mt-1">
                      {totalZones > 0
                        ? `${Math.round((opportunityCount / totalZones) * 100)}% of total`
                        : "—"}
                    </div>
                  </div>

                  <div className="p-4 bg-green-50 rounded-lg border border-green-200 transition-all hover:shadow-md">
                    <div className="text-2xl font-bold text-green-700">
                      {balancedCount}
                    </div>
                    <div className="text-xs text-green-600 font-medium mt-1">
                      Balanced Zones
                    </div>
                    <div className="text-xs text-gray-600 mt-1">
                      {totalZones > 0
                        ? `${Math.round((balancedCount / totalZones) * 100)}% of total`
                        : "—"}
                    </div>
                  </div>

                  <div className="p-4 bg-red-50 rounded-lg border border-red-200 transition-all hover:shadow-md">
                    <div className="text-2xl font-bold text-red-700">
                      {commercialCount}
                    </div>
                    <div className="text-xs text-red-600 font-medium mt-1">
                      Commercial Zones
                    </div>
                    <div className="text-xs text-gray-600 mt-1">
                      {totalZones > 0
                        ? `${Math.round((commercialCount / totalZones) * 100)}% of total`
                        : "—"}
                    </div>
                  </div>
                </div>

                {/* Insights */}
                <div className="pt-4 border-t space-y-3">
                  <h4 className="font-semibold text-sm text-gray-700">
                    Key Insights
                  </h4>
                  
                  {opportunityCount > balancedCount + commercialCount && (
                    <div className="p-3 bg-blue-50 rounded-lg text-sm text-gray-700">
                      <span className="font-semibold text-blue-700">
                        {Math.round((opportunityCount / totalZones) * 100)}%
                      </span>{" "}
                      of Karnataka falls under Opportunity Zones — indicating strong potential for decentralized growth and emerging market development.
                    </div>
                  )}

                  {commercialCount > 0 && (
                    <div className="p-3 bg-red-50 rounded-lg text-sm text-gray-700">
                      Commercial Zones are heavily clustered around urban centers, representing{" "}
                      <span className="font-semibold text-red-700">
                        {Math.round((commercialCount / totalZones) * 100)}%
                      </span>{" "}
                      of analyzed areas with established business infrastructure.
                    </div>
                  )}

                  {balancedCount > 0 && (
                    <div className="p-3 bg-green-50 rounded-lg text-sm text-gray-700">
                      Balanced Zones represent{" "}
                      <span className="font-semibold text-green-700">
                        {Math.round((balancedCount / totalZones) * 100)}%
                      </span>{" "}
                      of the region, offering stable conditions for sustainable business expansion without saturation risks.
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ========================================================= */
/* ===================== EXPORT SAFE ======================= */
/* ========================================================= */

export default function OpportunityZones() {
  return (
    <ErrorBoundary>
      <OpportunityZonesContent />
    </ErrorBoundary>
  );
}