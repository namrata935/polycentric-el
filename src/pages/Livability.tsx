import Navigation from "@/components/Navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Shield, Bus, Sparkles, Store, Footprints, DollarSign, Heart, TrendingUp, TrendingDown } from "lucide-react";
import { useState } from "react";

const zoneData = {
  "zone-a": {
    name: "Zone Alpha",
    overallScore: 72,
    scores: {
      safety: 7.2,
      transport: 6.8,
      cleanliness: 7.5,
      amenities: 6.9,
      walkability: 7.8,
      cost: 8.1,
      satisfaction: 7.0,
    },
    sentiment: {
      positive: 58,
      neutral: 28,
      negative: 14,
    },
    concerns: ["Traffic congestion", "Garbage collection delays", "Noise levels", "Night-time safety"],
    positives: ["Access to parks", "Clean streets", "Good metro connectivity", "Family-friendly"],
    comments: [
      { user: "AV", time: "2 hours ago", text: "The metro is frequent but the streets are crowded in the mornings.", sentiment: "neutral" },
      { user: "SK", time: "5 hours ago", text: "Love the new park! Great place for kids.", sentiment: "positive" },
      { user: "RP", time: "8 hours ago", text: "Garbage pickup has been inconsistent lately.", sentiment: "negative" },
      { user: "ML", time: "12 hours ago", text: "Walking to work is pleasant with all the trees.", sentiment: "positive" },
      { user: "TC", time: "1 day ago", text: "Traffic is getting worse during rush hour.", sentiment: "negative" },
      { user: "JD", time: "1 day ago", text: "Neighborhood feels safe during the day.", sentiment: "positive" },
      { user: "NS", time: "2 days ago", text: "More street lighting needed near the east side.", sentiment: "negative" },
      { user: "KW", time: "2 days ago", text: "Local shops have everything we need.", sentiment: "positive" },
    ],
  },
  "zone-b": {
    name: "Zone Beta",
    overallScore: 85,
    scores: {
      safety: 8.9,
      transport: 9.1,
      cleanliness: 8.7,
      amenities: 9.2,
      walkability: 8.5,
      cost: 5.2,
      satisfaction: 8.8,
    },
    sentiment: {
      positive: 76,
      neutral: 18,
      negative: 6,
    },
    concerns: ["High cost of living", "Limited parking", "Gentrification concerns", "Crowded cafes"],
    positives: ["Excellent restaurants", "Safe at night", "Great public transit", "Cultural venues", "Clean and modern"],
    comments: [
      { user: "BH", time: "1 hour ago", text: "This neighborhood is pricey but worth every penny.", sentiment: "positive" },
      { user: "EK", time: "3 hours ago", text: "Can't find parking anywhere on weekends.", sentiment: "negative" },
      { user: "VT", time: "6 hours ago", text: "The new coffee shops are amazing!", sentiment: "positive" },
      { user: "LM", time: "10 hours ago", text: "Public transport makes it easy to get anywhere.", sentiment: "positive" },
      { user: "DN", time: "14 hours ago", text: "Rent is getting out of control.", sentiment: "negative" },
      { user: "CM", time: "1 day ago", text: "Feel completely safe walking home late.", sentiment: "positive" },
      { user: "AS", time: "1 day ago", text: "So many great restaurants to choose from.", sentiment: "positive" },
      { user: "RT", time: "2 days ago", text: "The area is losing its original character.", sentiment: "negative" },
    ],
  },
  "zone-c": {
    name: "Zone Gamma",
    overallScore: 68,
    scores: {
      safety: 6.5,
      transport: 7.2,
      cleanliness: 6.8,
      amenities: 7.5,
      walkability: 8.2,
      cost: 7.9,
      satisfaction: 6.7,
    },
    sentiment: {
      positive: 52,
      neutral: 31,
      negative: 17,
    },
    concerns: ["Night safety issues", "Limited healthcare", "Street maintenance", "Noise from bars"],
    positives: ["Vibrant arts scene", "Affordable living", "Young community", "Walkable streets", "Creative energy"],
    comments: [
      { user: "PM", time: "1 hour ago", text: "The arts district is so inspiring!", sentiment: "positive" },
      { user: "KR", time: "4 hours ago", text: "Can be sketchy after midnight near the station.", sentiment: "negative" },
      { user: "FW", time: "7 hours ago", text: "Love the creative vibe and affordable rent.", sentiment: "positive" },
      { user: "MJ", time: "11 hours ago", text: "More streetlights needed in residential areas.", sentiment: "negative" },
      { user: "TL", time: "15 hours ago", text: "Great mix of small businesses and startups.", sentiment: "positive" },
      { user: "HS", time: "1 day ago", text: "Weekend nights can get really loud.", sentiment: "negative" },
      { user: "NC", time: "1 day ago", text: "Everything is within walking distance.", sentiment: "positive" },
      { user: "DK", time: "2 days ago", text: "Need more medical clinics in the area.", sentiment: "negative" },
    ],
  },
};

const Livability = () => {
  const [selectedZone, setSelectedZone] = useState<keyof typeof zoneData>("zone-a");
  
  const data = zoneData[selectedZone];

  const scoreIcons = {
    safety: Shield,
    transport: Bus,
    cleanliness: Sparkles,
    amenities: Store,
    walkability: Footprints,
    cost: DollarSign,
    satisfaction: Heart,
  };

  const scoreLabels = {
    safety: "Safety",
    transport: "Transport",
    cleanliness: "Cleanliness",
    amenities: "Amenities",
    walkability: "Walkability",
    cost: "Affordability",
    satisfaction: "Satisfaction",
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <div className="container mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8 animate-fade-in">
          <h1 className="font-heading text-4xl font-bold text-foreground mb-2">
            Community Livability & Sentiment Pulse
          </h1>
          <p className="text-muted-foreground text-lg">
            Understanding resident well-being through local feedback.
          </p>
        </div>

        {/* Zone Selector */}
        <div className="mb-8 animate-fade-in" style={{ animationDelay: "100ms" }}>
          <label className="block text-sm font-medium mb-2">Select Zone</label>
          <Select value={selectedZone} onValueChange={(value) => setSelectedZone(value as keyof typeof zoneData)}>
            <SelectTrigger className="w-full md:w-[300px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="zone-a">Zone Alpha</SelectItem>
              <SelectItem value="zone-b">Zone Beta</SelectItem>
              <SelectItem value="zone-c">Zone Gamma</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Livability Score Hero */}
        <Card className="mb-8 shadow-lg animate-fade-in" style={{ animationDelay: "200ms" }}>
          <CardHeader>
            <CardTitle className="font-heading text-2xl">Overall Livability Score</CardTitle>
            <CardDescription>Composite measure of neighborhood well-being</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-8 mb-8">
              <div className="flex flex-col items-center">
                <div className="text-6xl font-bold text-teal mb-2">{data.overallScore}</div>
                <div className="text-sm text-muted-foreground">out of 100</div>
              </div>
              
              <div className="flex-1 grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(data.scores).map(([key, value]) => {
                  const Icon = scoreIcons[key as keyof typeof scoreIcons];
                  const label = scoreLabels[key as keyof typeof scoreLabels];
                  
                  return (
                    <div key={key} className="flex flex-col items-center p-4 bg-muted/50 rounded-lg">
                      <Icon className="w-5 h-5 text-teal mb-2" />
                      <div className="text-xl font-bold">{value}</div>
                      <div className="text-xs text-muted-foreground text-center">{label}</div>
                    </div>
                  );
                })}
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Sentiment & Themes */}
          <div className="space-y-6">
            {/* Sentiment Breakdown */}
            <Card className="shadow-lg animate-fade-in" style={{ animationDelay: "300ms" }}>
              <CardHeader>
                <CardTitle className="font-heading">Sentiment Breakdown</CardTitle>
                <CardDescription>Overall community mood</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="w-4 h-4 text-green-600" />
                      <span className="text-sm font-medium">Positive</span>
                    </div>
                    <span className="text-sm font-semibold">{data.sentiment.positive}%</span>
                  </div>
                  <div className="w-full h-3 bg-secondary rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-green-500 rounded-full" 
                      style={{ width: `${data.sentiment.positive}%` }}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 rounded-full bg-amber" />
                      <span className="text-sm font-medium">Neutral</span>
                    </div>
                    <span className="text-sm font-semibold">{data.sentiment.neutral}%</span>
                  </div>
                  <div className="w-full h-3 bg-secondary rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-amber rounded-full" 
                      style={{ width: `${data.sentiment.neutral}%` }}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <TrendingDown className="w-4 h-4 text-red-600" />
                      <span className="text-sm font-medium">Negative</span>
                    </div>
                    <span className="text-sm font-semibold">{data.sentiment.negative}%</span>
                  </div>
                  <div className="w-full h-3 bg-secondary rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-red-500 rounded-full" 
                      style={{ width: `${data.sentiment.negative}%` }}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Key Themes */}
            <Card className="shadow-lg animate-fade-in" style={{ animationDelay: "400ms" }}>
              <CardHeader>
                <CardTitle className="font-heading">Key Themes</CardTitle>
                <CardDescription>What residents are talking about</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="text-sm font-semibold mb-3 text-red-700 dark:text-red-400">Top Concerns</h4>
                  <div className="flex flex-wrap gap-2">
                    {data.concerns.map((concern) => (
                      <Badge key={concern} variant="outline" className="border-red-200 text-red-800 dark:text-red-300">
                        {concern}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div className="pt-4 border-t">
                  <h4 className="text-sm font-semibold mb-3 text-green-700 dark:text-green-400">Top Positives</h4>
                  <div className="flex flex-wrap gap-2">
                    {data.positives.map((positive) => (
                      <Badge key={positive} variant="outline" className="border-green-200 text-green-800 dark:text-green-300">
                        {positive}
                      </Badge>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Resident Comments */}
          <Card className="lg:col-span-2 shadow-lg animate-fade-in" style={{ animationDelay: "500ms" }}>
            <CardHeader>
              <CardTitle className="font-heading">Resident Feedback</CardTitle>
              <CardDescription>Recent community comments and experiences</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
                {data.comments.map((comment, idx) => (
                  <div 
                    key={idx}
                    className="flex gap-3 p-4 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors"
                  >
                    <div className="w-10 h-10 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-semibold text-sm shrink-0">
                      {comment.user}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-sm">{comment.user}</span>
                        <span className="text-xs text-muted-foreground">• {comment.time}</span>
                        <div 
                          className={cn(
                            "w-2 h-2 rounded-full ml-auto",
                            comment.sentiment === "positive" && "bg-green-500",
                            comment.sentiment === "neutral" && "bg-amber",
                            comment.sentiment === "negative" && "bg-red-500"
                          )}
                        />
                      </div>
                      <p className="text-sm text-foreground">{comment.text}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Interpretation Panel */}
        <Card className="shadow-lg animate-fade-in" style={{ animationDelay: "600ms" }}>
          <CardHeader>
            <CardTitle className="font-heading">Insights & Recommendations</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="prose prose-sm max-w-none text-muted-foreground">
              <p className="mb-3">
                <strong className="text-foreground">General Trends:</strong> Residents in {data.name} show {data.sentiment.positive > 60 ? "strong" : data.sentiment.positive > 40 ? "moderate" : "mixed"} satisfaction with their neighborhood. 
                The overall livability score of {data.overallScore}/100 reflects a balance of strengths and areas for improvement.
              </p>
              <p className="mb-3">
                <strong className="text-foreground">What Residents Value:</strong> The community consistently highlights {data.positives.slice(0, 3).join(", ")} as key positive attributes. 
                These strengths should be preserved and enhanced in future development plans.
              </p>
              <p>
                <strong className="text-foreground">Priority Improvements:</strong> Addressing concerns around {data.concerns.slice(0, 2).join(" and ")} could significantly boost resident satisfaction 
                and overall livability scores. Investment in these areas is recommended for near-term planning cycles.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

const cn = (...classes: (string | undefined)[]) => classes.filter(Boolean).join(" ");

export default Livability;
