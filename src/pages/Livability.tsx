import Navigation from "@/components/Navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { AlertCircle, AlertTriangle, CheckCircle, MapPin, Database, TrendingDown, TrendingUp, Shield, CarFront, Loader2 } from "lucide-react";
import { useState, useEffect } from "react";

interface ZoneSentiment {
  zone_id: string;
  location: {
    latitude: number;
    longitude: number;
  };
  zone_info: {
    zone_type: string;
    business_count: number;
    transport_count: number;
    population: number;
    opportunity_score: number;
  };
  sentiment_analysis: {
    sentiment_score: number;
    sentiment_category: string;
    data_quality: string;
    sources_used: string[];
    primary_source: string;
    key_insights: {
      interpretation: string;
      top_issues: string[];
      priority_level: string;
      neighborhood?: string;
    };
    source_details: {
      reddit_bangalore?: {
        sentiment_score: number;
        positive_ratio: number;
        negative_ratio: number;
        sample_size: number;
        top_issues: string[];
      };
      accident_safety?: {
        sentiment_score: number;
        accident_count: number;
        interpretation: string;
      };
      model_based?: {
        sentiment_score: number;
        interpretation: string;
      };
    };
  };
}

const Livability = () => {
  const [zones, setZones] = useState<ZoneSentiment[]>([]);
  const [selectedZone, setSelectedZone] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch sentiment data from backend
  useEffect(() => {
    const fetchSentimentData = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:5000/api/sentiment-analysis');
        
        if (!response.ok) {
          throw new Error('Failed to fetch sentiment data');
        }
        
        const data = await response.json();
        setZones(data.zones || []);
        
        // Set first zone as default
        if (data.zones && data.zones.length > 0) {
          setSelectedZone(data.zones[0].zone_id);
        }
        
        setError(null);
      } catch (err) {
        console.error('Error fetching sentiment data:', err);
        setError('Failed to load sentiment data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchSentimentData();
  }, []);

  // Get current zone data
  const currentZone = zones.find(z => z.zone_id === selectedZone);

  // Helper functions
  const getSentimentColor = (score: number) => {
    if (score >= 0.5) return "text-green-600";
    if (score >= 0.2) return "text-green-500";
    if (score >= -0.2) return "text-yellow-600";
    if (score >= -0.5) return "text-orange-600";
    return "text-red-600";
  };

  const getSentimentBgColor = (score: number) => {
    if (score >= 0.5) return "bg-green-500";
    if (score >= 0.2) return "bg-green-400";
    if (score >= -0.2) return "bg-yellow-500";
    if (score >= -0.5) return "bg-orange-500";
    return "bg-red-500";
  };

  const getPriorityColor = (level: string) => {
    switch (level) {
      case "CRITICAL": return "destructive";
      case "HIGH": return "destructive";
      case "MEDIUM": return "secondary";
      case "LOW": return "outline";
      default: return "outline";
    }
  };

  const getDataQualityIcon = (quality: string) => {
    switch (quality) {
      case "high": return <CheckCircle className="w-4 h-4 text-green-600" />;
      case "medium": return <AlertTriangle className="w-4 h-4 text-yellow-600" />;
      case "low": return <AlertCircle className="w-4 h-4 text-orange-600" />;
      default: return <AlertCircle className="w-4 h-4" />;
    }
  };

  const getSourceLabel = (source: string) => {
    switch (source) {
      case "reddit_bangalore": return "Community Feedback";
      case "accident_safety": return "Safety Data";
      case "model_based": return "Model Estimate";
      default: return source;
    }
  };

  // Convert sentiment score (-1 to 1) to percentage (0 to 100)
  const scoreToPercentage = (score: number) => {
    return Math.round(((score + 1) / 2) * 100);
  };

  // Calculate positive/negative ratios for display
  const calculateRatios = (zone: ZoneSentiment) => {
    const reddit = zone.sentiment_analysis.source_details.reddit_bangalore;
    if (reddit) {
      return {
        positive: Math.round(reddit.positive_ratio * 100),
        negative: Math.round(reddit.negative_ratio * 100),
        neutral: Math.round((1 - reddit.positive_ratio - reddit.negative_ratio) * 100)
      };
    }
    
    // Fallback: estimate from sentiment score
    const score = zone.sentiment_analysis.sentiment_score;
    if (score > 0) {
      const positive = Math.round((score + 1) * 40);
      return { positive, negative: 100 - positive - 20, neutral: 20 };
    } else {
      const negative = Math.round((Math.abs(score)) * 40);
      return { positive: 100 - negative - 20, negative, neutral: 20 };
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <div className="container mx-auto px-6 py-24 flex items-center justify-center">
          <div className="text-center">
            <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4 text-primary" />
            <p className="text-muted-foreground">Loading sentiment analysis data...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !currentZone) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <div className="container mx-auto px-6 py-24">
          <Card className="max-w-2xl mx-auto">
            <CardContent className="pt-6">
              <div className="text-center">
                <AlertCircle className="w-12 h-12 mx-auto mb-4 text-destructive" />
                <p className="text-lg font-semibold mb-2">Unable to Load Data</p>
                <p className="text-muted-foreground">{error || "No zones available"}</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  const sentiment = currentZone.sentiment_analysis;
  const ratios = calculateRatios(currentZone);

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <div className="container mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8 animate-fade-in">
          <h1 className="font-heading text-4xl font-bold text-foreground mb-2">
            Zone Sentiment Analysis
          </h1>
          <p className="text-muted-foreground text-lg">
            Multi-source sentiment insights for Karnataka zones
          </p>
        </div>

        {/* Zone Selector */}
        <div className="mb-8 animate-fade-in" style={{ animationDelay: "100ms" }}>
          <label className="block text-sm font-medium mb-2">Select Zone</label>
          <Select value={selectedZone} onValueChange={setSelectedZone}>
            <SelectTrigger className="w-full md:w-[400px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {zones.map((zone) => {
                const neighborhood = zone.sentiment_analysis.key_insights.neighborhood;
                const zoneType = zone.zone_info.zone_type;
                const coords = `${zone.location.latitude.toFixed(3)}°N, ${zone.location.longitude.toFixed(3)}°E`;
                
                return (
                  <SelectItem key={zone.zone_id} value={zone.zone_id}>
                    {neighborhood 
                      ? `${neighborhood} - ${zoneType} (${coords})`
                      : `${zoneType} at ${coords}`
                    }
                  </SelectItem>
                );
              })}
            </SelectContent>
          </Select>
        </div>

        {/* Main Sentiment Score */}
        <Card className="mb-8 shadow-lg animate-fade-in" style={{ animationDelay: "200ms" }}>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="font-heading text-2xl">Overall Sentiment Score</CardTitle>
                <CardDescription>
                  Based on {sentiment.sources_used.length} data source{sentiment.sources_used.length > 1 ? 's' : ''}
                </CardDescription>
              </div>
              <Badge variant={getPriorityColor(sentiment.key_insights.priority_level)}>
                {sentiment.key_insights.priority_level}
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-8 mb-6">
              {/* Score Display */}
              <div className="flex flex-col items-center">
                <div className={`text-6xl font-bold mb-2 ${getSentimentColor(sentiment.sentiment_score)}`}>
                  {scoreToPercentage(sentiment.sentiment_score)}
                </div>
                <div className="text-sm text-muted-foreground">Sentiment Index</div>
                <div className="text-xs text-muted-foreground mt-1">
                  ({sentiment.sentiment_score.toFixed(3)})
                </div>
              </div>

              {/* Visual Bar */}
              <div className="flex-1">
                <div className="mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">Sentiment Distribution</span>
                    <div className="flex items-center gap-2">
                      {getDataQualityIcon(sentiment.data_quality)}
                      <span className="text-xs capitalize">{sentiment.data_quality} Confidence</span>
                    </div>
                  </div>
                  <div className="w-full h-8 bg-secondary rounded-full overflow-hidden flex">
                    <div 
                      className="bg-green-500 flex items-center justify-center text-xs text-white font-medium" 
                      style={{ width: `${ratios.positive}%` }}
                    >
                      {ratios.positive > 15 && `${ratios.positive}%`}
                    </div>
                    <div 
                      className="bg-yellow-500 flex items-center justify-center text-xs text-white font-medium" 
                      style={{ width: `${ratios.neutral}%` }}
                    >
                      {ratios.neutral > 15 && `${ratios.neutral}%`}
                    </div>
                    <div 
                      className="bg-red-500 flex items-center justify-center text-xs text-white font-medium" 
                      style={{ width: `${ratios.negative}%` }}
                    >
                      {ratios.negative > 15 && `${ratios.negative}%`}
                    </div>
                  </div>
                  <div className="flex justify-between text-xs text-muted-foreground mt-1">
                    <span>Positive ({ratios.positive}%)</span>
                    <span>Neutral ({ratios.neutral}%)</span>
                    <span>Negative ({ratios.negative}%)</span>
                  </div>
                </div>

                {/* Zone Info */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <div className="bg-muted/50 p-3 rounded-lg">
                    <div className="text-xs text-muted-foreground mb-1">Zone Type</div>
                    <div className="font-semibold text-sm">{currentZone.zone_info.zone_type}</div>
                  </div>
                  <div className="bg-muted/50 p-3 rounded-lg">
                    <div className="text-xs text-muted-foreground mb-1">Population</div>
                    <div className="font-semibold text-sm">{currentZone.zone_info.population.toLocaleString()}</div>
                  </div>
                  <div className="bg-muted/50 p-3 rounded-lg">
                    <div className="text-xs text-muted-foreground mb-1">Businesses</div>
                    <div className="font-semibold text-sm">{currentZone.zone_info.business_count}</div>
                  </div>
                  <div className="bg-muted/50 p-3 rounded-lg">
                    <div className="text-xs text-muted-foreground mb-1">Opportunity</div>
                    <div className="font-semibold text-sm">{(currentZone.zone_info.opportunity_score * 100).toFixed(0)}%</div>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Data Sources */}
          <Card className="shadow-lg animate-fade-in" style={{ animationDelay: "300ms" }}>
            <CardHeader>
              <CardTitle className="font-heading flex items-center gap-2">
                <Database className="w-5 h-5" />
                Data Sources
              </CardTitle>
              <CardDescription>Sentiment data origin and quality</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {sentiment.sources_used
                .filter(source => source !== 'accident_safety') // Hide accident data
                .map((source) => {
                  const details = sentiment.source_details[source as keyof typeof sentiment.source_details];
                  const isPrimary = source === sentiment.primary_source;
                  
                  return (
                    <div key={source} className={`p-3 rounded-lg border ${isPrimary ? 'border-primary bg-primary/5' : 'border-border'}`}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-sm">{getSourceLabel(source)}</span>
                        {isPrimary && <Badge variant="outline" className="text-xs">Primary</Badge>}
                      </div>
                      
                      {details && (
                        <div className="space-y-1">
                          {source === 'reddit_bangalore' && 'sample_size' in details && (
                            <>
                              <div className="text-xs text-muted-foreground">
                                Score: <span className="font-semibold">{details.sentiment_score?.toFixed(3)}</span>
                              </div>
                              <div className="text-xs text-muted-foreground">
                                Sample: <span className="font-semibold">{details.sample_size} posts</span>
                              </div>
                              <div className="text-xs text-muted-foreground mt-2">
                                <span className="font-semibold">Feedback Distribution:</span>
                                <div className="mt-1">
                                  Positive: {Math.round(details.positive_ratio * 100)}% | 
                                  Negative: {Math.round(details.negative_ratio * 100)}%
                                </div>
                              </div>
                            </>
                          )}
                          
                          {source === 'model_based' && 'interpretation' in details && (
                            <>
                              <div className="text-xs text-muted-foreground">
                                Score: <span className="font-semibold">{details.sentiment_score?.toFixed(3)}</span>
                              </div>
                              <div className="text-xs text-muted-foreground italic mt-2">
                                {details.interpretation}
                              </div>
                            </>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              
              {/* Data Quality Note */}
              <div className="pt-3 border-t text-xs text-muted-foreground">
                <div className="flex items-center gap-2 mb-1">
                  {getDataQualityIcon(sentiment.data_quality)}
                  <span className="font-semibold capitalize">{sentiment.data_quality} Quality Data</span>
                </div>
                {sentiment.data_quality === 'high' && (
                  <p className="text-xs">Based on real community feedback from social media</p>
                )}
                {sentiment.data_quality === 'medium' && (
                  <p className="text-xs">Based on urban indicators and model estimates</p>
                )}
                {sentiment.data_quality === 'low' && (
                  <p className="text-xs">Based on zone characteristics and model predictions</p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Key Issues */}
          <Card className="lg:col-span-2 shadow-lg animate-fade-in" style={{ animationDelay: "400ms" }}>
            <CardHeader>
              <CardTitle className="font-heading">Key Insights</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Top Issues */}
              {sentiment.key_insights.top_issues.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold mb-3 text-red-700 dark:text-red-400 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4" />
                    Top Concerns
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {sentiment.key_insights.top_issues.map((issue) => (
                      <Badge 
                        key={issue} 
                        variant="outline" 
                        className="border-red-200 text-red-800 dark:text-red-300 capitalize"
                      >
                        {issue}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Location Info */}
              <div className="pt-4 border-t">
                <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
                  <MapPin className="w-4 h-4" />
                  Location Details
                </h4>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  {sentiment.key_insights.neighborhood && (
                    <div>
                      <span className="text-muted-foreground">Neighborhood: </span>
                      <span className="font-semibold">{sentiment.key_insights.neighborhood}</span>
                    </div>
                  )}
                  <div>
                    <span className="text-muted-foreground">Coordinates: </span>
                    <span className="font-mono text-xs">
                      {currentZone.location.latitude.toFixed(4)}, {currentZone.location.longitude.toFixed(4)}
                    </span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Category: </span>
                    <span className="font-semibold capitalize">{sentiment.sentiment_category}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Priority: </span>
                    <Badge variant={getPriorityColor(sentiment.key_insights.priority_level)} className="ml-1">
                      {sentiment.key_insights.priority_level}
                    </Badge>
                  </div>
                </div>
              </div>

              {/* Source Details */}
              {sentiment.source_details.reddit_bangalore && (
                <div className="pt-4 border-t">
                  <h4 className="text-sm font-semibold mb-3">Community Feedback Details</h4>
                  <div className="grid grid-cols-3 gap-3">
                    <div className="text-center p-3 bg-green-50 dark:bg-green-950 rounded-lg">
                      <div className="text-2xl font-bold text-green-600">
                        {Math.round(sentiment.source_details.reddit_bangalore.positive_ratio * 100)}%
                      </div>
                      <div className="text-xs text-muted-foreground">Positive</div>
                    </div>
                    <div className="text-center p-3 bg-red-50 dark:bg-red-950 rounded-lg">
                      <div className="text-2xl font-bold text-red-600">
                        {Math.round(sentiment.source_details.reddit_bangalore.negative_ratio * 100)}%
                      </div>
                      <div className="text-xs text-muted-foreground">Negative</div>
                    </div>
                    <div className="text-center p-3 bg-muted rounded-lg">
                      <div className="text-2xl font-bold">
                        {sentiment.source_details.reddit_bangalore.sample_size}
                      </div>
                      <div className="text-xs text-muted-foreground">Posts</div>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Interpretation Panel */}
        <Card className="shadow-lg animate-fade-in" style={{ animationDelay: "500ms" }}>
          <CardHeader>
            <CardTitle className="font-heading">Analysis Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="prose prose-sm max-w-none text-muted-foreground">
              <p className="mb-3">
                <strong className="text-foreground">Sentiment Overview:</strong> This zone shows a{" "}
                <span className={`font-semibold ${getSentimentColor(sentiment.sentiment_score)}`}>
                  {sentiment.sentiment_category}
                </span>{" "}
                sentiment ({sentiment.sentiment_score.toFixed(3)}) based on{" "}
                {sentiment.sources_used.filter(s => s !== 'accident_safety').length} data source
                {sentiment.sources_used.filter(s => s !== 'accident_safety').length > 1 ? 's' : ''}. 
                {" "}
              </p>
              
              {sentiment.key_insights.top_issues.length > 0 && (
                <p className="mb-3">
                  <strong className="text-foreground">Key Concerns:</strong> Residents and data indicate primary issues with{" "}
                  {sentiment.key_insights.top_issues.slice(0, 3).join(", ")}. These areas require attention for improving livability.
                </p>
              )}

              <p>
                <strong className="text-foreground">Data Quality:</strong> This analysis has{" "}
                <span className="font-semibold capitalize">{sentiment.data_quality}</span> confidence.
                {sentiment.data_quality === 'high' && " The presence of real community feedback provides strong insights for decision-making."}
                {sentiment.data_quality === 'low' && " Model-based estimates provide directional guidance; consider supplementing with additional data collection."}
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Disclaimer */}
        <div className="mt-6 p-4 bg-muted/50 rounded-lg text-sm text-muted-foreground">
          <strong>Data Sources:</strong> This analysis integrates community feedback from social media 
          and urban planning indicators. Sentiment scores reflect public perception and zone characteristics 
          to support data-driven urban development decisions.
        </div>
      </div>
    </div>
  );
};

export default Livability;
        