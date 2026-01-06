import React from "react";
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
})

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

  /* ---------------- MAP CENTER ---------------- */

  const center =
    zonesData.length > 0
      ? [
          zonesData.reduce((s, z) => s + (z.zone_lat ?? 0), 0) / zonesData.length,
          zonesData.reduce((s, z) => s + (z.zone_lon ?? 0), 0) / zonesData.length,
        ]
      : karnatakaCenter;

  if (isLoading) {
    return <div className="p-8">Loading zones…</div>;
  }

  if (error) {
    return <div className="p-8 text-red-500">Failed to load zones</div>;
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

        {/* MAP */}
        <Card className="shadow-lg mb-8">
          <CardContent className="p-6">
            <div className="relative w-full h-[520px] rounded-lg overflow-hidden border">
              {zonesData.length === 0 ? (
                <div className="flex items-center justify-center h-full">
                  No zone data available
                </div>
              ) : (
                <MapContainer
                  center={center as L.LatLngExpression}
                  zoom={8}
                  style={{ height: "100%", width: "100%" }}
                >
                  <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

                  {zonesData.map((zone, idx) => {
                    if (
                      typeof zone.zone_lat !== "number" ||
                      typeof zone.zone_lon !== "number"
                    )
                      return null;

                    return (
                      <Circle
                        key={idx}
                        center={[zone.zone_lat, zone.zone_lon]}
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
                              Score: {(zone.adjusted_zone_score ?? 0).toFixed(2)}
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
              )}
            </div>
          </CardContent>
        </Card>

        {/* SUMMARY */}
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle>Zone Distribution</CardTitle>
            <CardDescription>
              Opportunity-biased classification (future-oriented)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-blue-600">Opportunity Zones</span>
              <span className="font-semibold">{opportunityCount}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-green-600">Balanced Zones</span>
              <span className="font-semibold">{balancedCount}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-red-600">Commercial Zones</span>
              <span className="font-semibold">{commercialCount}</span>
            </div>
          </CardContent>
        </Card>
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
