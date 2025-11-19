import Navigation from "@/components/Navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, Building, ArrowRight } from "lucide-react";
import { MapContainer, TileLayer, Popup, Circle } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { useEffect } from "react";

const mockZones = [
	{
		id: 1,
		name: "Zone Alpha - Bangalore",
		type: "opportunity",
		color: "bg-red-500",
		population: 45200,
		businesses: 320,
		commute: "28 min",
		lat: 12.9716,
		lng: 77.5946,
	},
	{
		id: 2,
		name: "Zone Beta - Mysore",
		type: "commercial",
		color: "bg-blue-500",
		population: 32100,
		businesses: 1850,
		commute: "18 min",
		lat: 12.2958,
		lng: 76.6394,
	},
	{
		id: 3,
		name: "Zone Gamma - Pune Road",
		type: "balanced",
		color: "bg-green-500",
		population: 38500,
		businesses: 890,
		commute: "22 min",
		lat: 13.0827,
		lng: 77.5979,
	},
];

// Custom marker icon
const createCustomIcon = (color: string) => {
	const colorMap: { [key: string]: string } = {
		"bg-red-500": "#ef4444",
		"bg-blue-500": "#3b82f6",
		"bg-green-500": "#22c55e",
	};

	return L.divIcon({
		html: `<div style="background-color: ${colorMap[color]}; width: 30px; height: 30px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 14px;"></div>`,
		iconSize: [30, 30],
		className: "custom-marker",
	});
};

const OpportunityZones = () => {
	const karnatakaCenter = [15.3173, 75.7139]; // Karnataka center

	return (
		<div className="min-h-screen bg-background">
			<Navigation />

			<div className="container mx-auto px-6 py-8">
				{/* Header */}
				<div className="mb-8 animate-fade-in">
					<h1 className="font-heading text-4xl font-bold text-foreground mb-2">
						Opportunity Zone Identification
					</h1>
					<p className="text-muted-foreground text-lg">
						Highlighting population–job imbalances across Karnataka.
					</p>
				</div>

				{/* Map Section */}
				<div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
					<Card className="lg:col-span-2 shadow-lg animate-fade-in" style={{ animationDelay: "100ms" }}>
						<CardContent className="p-6">
							<div className="relative w-full h-[500px] rounded-lg overflow-hidden border border-border">
								<MapContainer center={karnatakaCenter as L.LatLngExpression} zoom={9} style={{ height: "100%", width: "100%" }}>
									<TileLayer
										url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
										attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
									/>
									{mockZones.map((zone) => (
										<Circle
											key={zone.id}
											center={[zone.lat, zone.lng]}
											radius={5000}
											pathOptions={{
												color: {
													"bg-red-500": "#ef4444",
													"bg-blue-500": "#3b82f6",
													"bg-green-500": "#22c55e",
												}[zone.color] || "#000",
												fillColor: {
													"bg-red-500": "#ef4444",
													"bg-blue-500": "#3b82f6",
													"bg-green-500": "#22c55e",
												}[zone.color] || "#000",
												fillOpacity: 0.5,
												weight: 2,
											}}
										>
											<Popup>
												<div className="p-3 text-sm">
													<h3 className="font-semibold mb-1">{zone.name}</h3>
													<p className="text-xs text-muted-foreground capitalize mb-2">{zone.type} Zone</p>
													<div className="text-xs space-y-1">
														<div className="flex justify-between">
															<span>Population:</span>
															<span className="font-semibold">{zone.population.toLocaleString()}</span>
														</div>
														<div className="flex justify-between">
															<span>Businesses:</span>
															<span className="font-semibold">{zone.businesses}</span>
														</div>
														<div className="flex justify-between">
															<span>Avg Commute:</span>
															<span className="font-semibold">{zone.commute}</span>
														</div>
													</div>
												</div>
											</Popup>
										</Circle>
									))}
								</MapContainer>
							</div>
						</CardContent>
					</Card>

					{/* Insight Panel */}
					<Card className="shadow-lg animate-fade-in" style={{ animationDelay: "200ms" }}>
						<CardHeader>
							<CardTitle className="font-heading">Key Insights</CardTitle>
							<CardDescription>Understanding the patterns</CardDescription>
						</CardHeader>
						<CardContent className="space-y-4">
							<div className="p-4 bg-red-50 border border-red-200 rounded-lg">
								<h4 className="font-heading font-semibold text-sm mb-2 text-red-900">
									Opportunity Zones
								</h4>
								<p className="text-xs text-red-800">
									High population density with limited job access. These areas may benefit from new
									commercial hubs.
								</p>
							</div>

							<div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
								<h4 className="font-heading font-semibold text-sm mb-2 text-blue-900">
									Commercial Clusters
								</h4>
								<p className="text-xs text-blue-800">
									Dense business activity with lower residential population. Consider mixed-use
									development.
								</p>
							</div>

							<div className="p-4 bg-green-50 border border-green-200 rounded-lg">
								<h4 className="font-heading font-semibold text-sm mb-2 text-green-900">
									Balanced Areas
								</h4>
								<p className="text-xs text-green-800">
									Healthy mix of population and employment opportunities. Maintain current development
									patterns.
								</p>
							</div>

							<div className="pt-4 border-t">
								<p className="text-xs text-muted-foreground">
									Analysis based on K-Means clustering of population density, business concentration, and
									commute patterns.
								</p>
							</div>
						</CardContent>
					</Card>
				</div>

				{/* Cluster Summary Cards */}
				<div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
					{mockZones.map((zone, idx) => (
						<Card
							key={zone.id}
							className="shadow-lg hover:shadow-xl transition-shadow animate-fade-in"
							style={{ animationDelay: `${300 + idx * 100}ms` }}
						>
							<CardHeader>
								<div className="flex items-center justify-between mb-2">
									<CardTitle className="font-heading text-lg">{zone.name}</CardTitle>
									<div className={cn("w-3 h-3 rounded-full", zone.color)} />
								</div>
								<CardDescription className="capitalize">{zone.type} Zone</CardDescription>
							</CardHeader>
							<CardContent className="space-y-3">
								<div className="flex items-center justify-between">
									<div className="flex items-center gap-2 text-sm text-muted-foreground">
										<Users className="w-4 h-4" />
										<span>Population</span>
									</div>
									<span className="font-semibold">{zone.population.toLocaleString()}</span>
								</div>

								<div className="flex items-center justify-between">
									<div className="flex items-center gap-2 text-sm text-muted-foreground">
										<Building className="w-4 h-4" />
										<span>Businesses</span>
									</div>
									<span className="font-semibold">{zone.businesses.toLocaleString()}</span>
								</div>

								<div className="flex items-center justify-between">
									<div className="flex items-center gap-2 text-sm text-muted-foreground">
										<ArrowRight className="w-4 h-4" />
										<span>Avg Commute</span>
									</div>
									<span className="font-semibold">{zone.commute}</span>
								</div>

								<div className="pt-3 border-t">
									<p className="text-xs text-muted-foreground">
										{zone.type === "opportunity" &&
											"Potential for commercial development to reduce commute times."}
										{zone.type === "commercial" &&
											"Consider residential development to create live-work balance."}
										{zone.type === "balanced" && "Maintain current mixed-use development approach."}
									</p>
								</div>
							</CardContent>
						</Card>
					))}
				</div>

				{/* Analytics Section */}
				<Card className="shadow-lg animate-fade-in" style={{ animationDelay: "600ms" }}>
					<CardHeader>
						<CardTitle className="font-heading">Zone Distribution</CardTitle>
						<CardDescription>Overview of cluster categories</CardDescription>
					</CardHeader>
					<CardContent>
						<div className="space-y-4">
							<div>
								<div className="flex items-center justify-between mb-2">
									<span className="text-sm font-medium">Opportunity Zones</span>
									<span className="text-sm font-semibold">35%</span>
								</div>
								<div className="w-full h-3 bg-secondary rounded-full overflow-hidden">
									<div className="h-full bg-red-500 rounded-full" style={{ width: "35%" }} />
								</div>
							</div>

							<div>
								<div className="flex items-center justify-between mb-2">
									<span className="text-sm font-medium">Commercial Dense</span>
									<span className="text-sm font-semibold">25%</span>
								</div>
								<div className="w-full h-3 bg-secondary rounded-full overflow-hidden">
									<div className="h-full bg-blue-500 rounded-full" style={{ width: "25%" }} />
								</div>
							</div>

							<div>
								<div className="flex items-center justify-between mb-2">
									<span className="text-sm font-medium">Balanced Mixed-Use</span>
									<span className="text-sm font-semibold">30%</span>
								</div>
								<div className="w-full h-3 bg-secondary rounded-full overflow-hidden">
									<div className="h-full bg-green-500 rounded-full" style={{ width: "30%" }} />
								</div>
							</div>

							<div>
								<div className="flex items-center justify-between mb-2">
									<span className="text-sm font-medium">Emerging Zones</span>
									<span className="text-sm font-semibold">10%</span>
								</div>
								<div className="w-full h-3 bg-secondary rounded-full overflow-hidden">
									<div className="h-full bg-amber rounded-full" style={{ width: "10%" }} />
								</div>
							</div>
						</div>
					</CardContent>
				</Card>
			</div>
		</div>
	);
};

const cn = (...classes: (string | undefined)[]) => classes.filter(Boolean).join(" ");

export default OpportunityZones;
