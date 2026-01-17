import Navigation from "@/components/Navigation";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { MapPinned } from "lucide-react";
import { useState } from "react";

/* =========================
   TYPES
========================= */
type Signal = {
  label: "Demand" | "Workforce" | "Competition" | "Opportunity";
  value: "High" | "Moderate" | "Low";
};

type BackendResult = {
  zone_id: string | null;
  zone_code: string | null;
  zone_label: string | null;
  zone_type: string;
  region_name: string | null;

  zone_lat: number;
  zone_lon: number;

  final_score: number;
  confidence: string;
  summary: string;
  detailed_explanation: string;

  signals: Signal[];
};

/* =========================
   HELPERS
========================= */
function visualScore(score: number) {
  const min = 0.32;
  const max = 0.6;
  const clamped = Math.min(Math.max(score, min), max);
  return Math.round(60 + ((clamped - min) / (max - min)) * 35);
}

function zoneBorder(zoneType: string) {
  if (zoneType.toLowerCase().includes("opportunity")) return "border-blue-500";
  if (zoneType.toLowerCase().includes("balanced")) return "border-green-500";
  return "border-red-500";
}

function barWidth(level: "High" | "Moderate" | "Low") {
  if (level === "High") return 85;
  if (level === "Moderate") return 55;
  return 30;
}

function barColor(signal: string) {
  switch (signal) {
    case "Demand":
      return "bg-blue-500";
    case "Workforce":
      return "bg-green-500";
    case "Competition":
      return "bg-red-500";
    case "Opportunity":
      return "bg-purple-500";
    default:
      return "bg-gray-400";
  }
}

/* =========================
   MAP (EXPANDABLE)
========================= */
function ZoneMap({
  lat,
  lon,
  expanded,
  zoneType,
}: {
  lat: number;
  lon: number;
  expanded: boolean;
  zoneType: string;
}) {
  const size = expanded ? "640x360" : "260x260";
  const src = `https://maps.wikimedia.org/img/osm-intl,11,${lat},${lon},${size}.png`;

  return (
    <div
      className={`transition-all duration-300 ${
        expanded ? "w-[640px] h-[360px]" : "w-[260px] h-[260px]"
      }`}
    >
      <img
        src={src}
        alt="Zone map"
        className={`w-full h-full object-cover rounded-lg border-4 ${zoneBorder(
          zoneType
        )}`}
      />
    </div>
  );
}

/* =========================
   HORIZONTAL COMPARISON
========================= */
function HorizontalComparisonChart({
  title,
  signal,
  zones,
}: {
  title: string;
  signal: "Demand" | "Workforce" | "Competition" | "Opportunity";
  zones: BackendResult[];
}) {
  return (
    <div className="space-y-4">
      <h3 className="text-xl font-semibold">{title}</h3>

      <div className="space-y-4">
        {zones.map((z) => {
          const level = z.signals.find(
            (s) => s.label === signal
          )!.value;

          return (
            <div key={z.zone_id ?? z.zone_lat} className="space-y-1">
              <div className="flex justify-between text-sm">
                <span className="font-medium">
                  {z.zone_label ?? "Zone"}
                </span>
                <span className="text-muted-foreground">
                  {level}
                </span>
              </div>

              <div className="w-full h-3 bg-secondary rounded-full overflow-hidden">
                <div
                  className={`h-full ${barColor(signal)} transition-all duration-700`}
                  style={{ width: `${barWidth(level)}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      <p className="text-sm text-muted-foreground italic">
        Higher values indicate stronger alignment for this metric.
      </p>
    </div>
  );
}

/* =========================
   MAIN COMPONENT
========================= */
export default function BusinessMatcher() {
  const [category, setCategory] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<BackendResult[]>([]);
  const [expanded, setExpanded] = useState<number | null>(null);

  const findBestZones = async () => {
    if (!category || !description) return;
    setLoading(true);
    setExpanded(null);

    try {
      const res = await fetch("http://localhost:8000/semantic-zone-search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ category, description }),
      });
      setResults(await res.json());
    } finally {
      setLoading(false);
    }
  };

  const topZones = results.slice(0, 4);

  return (
    <div className="min-h-screen bg-background">
      <Navigation />

      <div className="container mx-auto px-8 py-10 space-y-14">
        {/* HEADER */}
        <div>
          <h1 className="text-5xl font-bold mb-3">
            Business Matching Engine
          </h1>
          <p className="text-lg text-muted-foreground">
            Semantic + geographic suitability analysis
          </p>
        </div>

        {/* INPUT */}
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="text-xl">Describe Your Business</CardTitle>
            <CardDescription>
              Used to evaluate demand, workforce, and opportunity
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              placeholder="Category (e.g., food, healthcare)"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            />
            <Input
              placeholder="Description (e.g., affordable family restaurant)"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
            <Button onClick={findBestZones} disabled={loading}>
              {loading ? "Analyzing..." : "Find Best Zones"}
            </Button>
          </CardContent>
        </Card>

        {/* ZONE CARDS */}
        <div className="space-y-10">
          {topZones.map((r, idx) => {
            const isOpen = expanded === idx;
            const score = visualScore(r.final_score);

            return (
              <Card
                key={idx}
                className="shadow-md cursor-pointer hover:shadow-lg"
                onClick={() => setExpanded(isOpen ? null : idx)}
              >
                <CardHeader className="bg-muted/40">
                  <div className="flex gap-8 items-start">
                    <ZoneMap
                      lat={r.zone_lat}
                      lon={r.zone_lon}
                      expanded={isOpen}
                      zoneType={r.zone_type}
                    />

                    <div className="flex-1">
                      <CardTitle className="text-2xl flex items-center gap-2">
                        <MapPinned className="w-5 h-5" />
                        {r.zone_label ?? "Unnamed Zone"}
                      </CardTitle>

                      <CardDescription className="text-base mt-1">
                        {r.region_name} · {r.zone_code} · {r.zone_id}
                      </CardDescription>

                      <div className="mt-4 italic border-l-4 pl-4 border-teal">
                        {r.summary}
                      </div>

                      <div className="mt-4 flex gap-2 flex-wrap">
                        <Badge variant="outline">{r.zone_type}</Badge>
                        <Badge variant="outline">
                          Confidence: {r.confidence}
                        </Badge>
                      </div>
                    </div>

                    <div className="text-right w-32">
                      <div className="text-4xl font-bold text-teal">
                        {score}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        Match Score
                      </div>
                    </div>
                  </div>
                </CardHeader>

                {isOpen && (
                  <CardContent className="border-t pt-6">
                    <p className="text-lg leading-relaxed">
                      {r.detailed_explanation}
                    </p>
                  </CardContent>
                )}
              </Card>
            );
          })}
        </div>

        {/* COMPARISON SECTION */}
        {topZones.length > 1 && (
          <Card className="shadow-xl">
            <CardHeader>
              <CardTitle className="text-3xl">
                Comparative Zone Analysis
              </CardTitle>
              <CardDescription>
                Side-by-side comparison of suitability metrics
              </CardDescription>
            </CardHeader>

            <CardContent className="grid md:grid-cols-2 gap-10">
              <HorizontalComparisonChart
                title="Demand Comparison"
                signal="Demand"
                zones={topZones}
              />
              <HorizontalComparisonChart
                title="Workforce Comparison"
                signal="Workforce"
                zones={topZones}
              />
              <HorizontalComparisonChart
                title="Competition Comparison"
                signal="Competition"
                zones={topZones}
              />
              <HorizontalComparisonChart
                title="Opportunity Comparison"
                signal="Opportunity"
                zones={topZones}
              />
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
