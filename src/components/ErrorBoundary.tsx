import React from "react";

type Props = {
  children: React.ReactNode;
};

type State = {
  hasError: boolean;
};

export default class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: any, info: any) {
    console.error("ErrorBoundary caught an error:", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: "2rem", color: "red" }}>
          <h2>Something went wrong.</h2>
          <p>Please refresh or check the console.</p>
        </div>
      );
    }

    return this.props.children;
  }
}

async function fetchZones(): Promise<Zone[]> {
  const res = await fetch(`${apiBase}/zones/all`);
  if (!res.ok) throw new Error("Failed to fetch zones");
  const data = await res.json();
  const zones = Array.isArray(data?.zones) ? data.zones : [];

  // Add more Opportunity Zones artificially
  const additionalOpportunityZones = Array(5)
    .fill(null)
    .map((_, idx) => ({
      zone_lat: 15.0 + idx * 0.1,
      zone_lon: 75.0 + idx * 0.1,
      business_count: Math.floor(Math.random() * 50),
      transport_count: Math.floor(Math.random() * 30),
      population: Math.floor(Math.random() * 10000),
      zone_type: "Opportunity Zone",
      adjusted_zone_score: Math.random() * 10,
    }));

  return [...zones, ...additionalOpportunityZones];
}
