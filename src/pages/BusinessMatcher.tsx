import Navigation from "@/components/Navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Building2, TrendingUp, Users, DollarSign, GraduationCap } from "lucide-react";
import { useState } from "react";

const zoneProfiles = {
  "zone-a": {
    name: "Zone Alpha",
    workforce: "Mixed skilled labor",
    skills: ["Manufacturing", "Logistics", "Retail"],
    income: "Lower-middle income",
    age: "25-45 years (majority)",
    gaps: ["Healthcare", "Education", "Tech services"],
    employment: "62%",
  },
  "zone-b": {
    name: "Zone Beta",
    workforce: "Highly educated professionals",
    skills: ["Finance", "Technology", "Creative"],
    income: "Upper-middle to high income",
    age: "28-40 years (majority)",
    gaps: ["Family services", "Recreation", "Retail"],
    employment: "78%",
  },
  "zone-c": {
    name: "Zone Gamma",
    workforce: "Young emerging talent",
    skills: ["Service", "Arts", "Tech startups"],
    income: "Lower-middle income",
    age: "22-35 years (majority)",
    gaps: ["Enterprise offices", "Finance", "Manufacturing"],
    employment: "68%",
  },
};

const businessRecommendations = {
  "zone-a": [
    {
      name: "MedCare Community Clinic",
      tagline: "Primary healthcare for growing neighborhoods",
      fit: "Addresses healthcare gap in area with aging infrastructure and dense population",
      score: 92,
      tags: ["Healthcare", "Community", "Essential"],
    },
    {
      name: "SkillBridge Training Center",
      tagline: "Workforce development & vocational training",
      fit: "Matches local workforce profile with upskilling opportunities in logistics and tech",
      score: 88,
      tags: ["Education", "Workforce", "Growth"],
    },
    {
      name: "Urban Grocery Co-op",
      tagline: "Fresh, affordable local groceries",
      fit: "Fills retail gap with income-appropriate pricing for neighborhood demographics",
      score: 85,
      tags: ["Retail", "Food", "Local"],
    },
    {
      name: "PackSmart Logistics Hub",
      tagline: "Last-mile delivery & warehousing",
      fit: "Leverages existing manufacturing/logistics workforce and infrastructure",
      score: 82,
      tags: ["Logistics", "Employment", "Infrastructure"],
    },
    {
      name: "TechFix Repair Services",
      tagline: "Electronics & appliance repair",
      fit: "Affordable services matching income levels with job creation potential",
      score: 79,
      tags: ["Tech", "Service", "Affordable"],
    },
  ],
  "zone-b": [
    {
      name: "Bright Futures Daycare",
      tagline: "Premium childcare for working families",
      fit: "Serves dual-income professional households with young children",
      score: 94,
      tags: ["Family", "Childcare", "Premium"],
    },
    {
      name: "FitLife Wellness Center",
      tagline: "Boutique fitness & wellness studio",
      fit: "Matches affluent demographics seeking premium health and recreation options",
      score: 90,
      tags: ["Recreation", "Health", "Lifestyle"],
    },
    {
      name: "Artisan Market Hall",
      tagline: "Curated retail & dining experience",
      fit: "Addresses retail gap with upscale shopping aligned to local purchasing power",
      score: 87,
      tags: ["Retail", "Dining", "Experience"],
    },
    {
      name: "GreenSpace Coworking",
      tagline: "Flexible workspace for remote professionals",
      fit: "Complements high concentration of tech and creative workers in the area",
      score: 84,
      tags: ["Workspace", "Tech", "Flexibility"],
    },
    {
      name: "Culinary Collective",
      tagline: "Farm-to-table restaurant & cafe",
      fit: "Taps into foodie culture and disposable income of local professionals",
      score: 81,
      tags: ["Dining", "Local", "Quality"],
    },
  ],
  "zone-c": [
    {
      name: "LaunchPad Startup Incubator",
      tagline: "Accelerator for early-stage ventures",
      fit: "Nurtures existing startup ecosystem and young entrepreneurial talent",
      score: 93,
      tags: ["Tech", "Startups", "Innovation"],
    },
    {
      name: "Metro Finance Credit Union",
      tagline: "Community banking & financial literacy",
      fit: "Addresses finance gap with accessible banking for emerging professionals",
      score: 89,
      tags: ["Finance", "Community", "Literacy"],
    },
    {
      name: "Creative Forge Studios",
      tagline: "Shared workspace for artists & makers",
      fit: "Supports thriving arts community with affordable studio space",
      score: 86,
      tags: ["Arts", "Creative", "Affordable"],
    },
    {
      name: "TechHub Training Campus",
      tagline: "Coding bootcamps & tech education",
      fit: "Aligns with tech-savvy demographic and job market demand",
      score: 83,
      tags: ["Education", "Tech", "Career"],
    },
    {
      name: "Sustainable Goods Marketplace",
      tagline: "Eco-friendly retail & services",
      fit: "Resonates with environmentally-conscious young professional demographic",
      score: 80,
      tags: ["Retail", "Sustainable", "Lifestyle"],
    },
  ],
};

const BusinessMatcher = () => {
  const [selectedZone, setSelectedZone] = useState<keyof typeof zoneProfiles>("zone-a");
  
  const profile = zoneProfiles[selectedZone];
  const businesses = businessRecommendations[selectedZone];

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <div className="container mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8 animate-fade-in">
          <h1 className="font-heading text-4xl font-bold text-foreground mb-2">
            Business Matching Engine
          </h1>
          <p className="text-muted-foreground text-lg">
            Suggesting suitable businesses for each area.
          </p>
        </div>

        {/* Zone Selector */}
        <div className="mb-8 animate-fade-in" style={{ animationDelay: "100ms" }}>
          <label className="block text-sm font-medium mb-2">Select Zone</label>
          <Select value={selectedZone} onValueChange={(value) => setSelectedZone(value as keyof typeof zoneProfiles)}>
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

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Zone Profile */}
          <Card className="lg:col-span-1 shadow-lg animate-fade-in" style={{ animationDelay: "200ms" }}>
            <CardHeader>
              <CardTitle className="font-heading">{profile.name} Profile</CardTitle>
              <CardDescription>Demographics & economic indicators</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex items-center gap-2 text-sm font-medium mb-2">
                  <Users className="w-4 h-4 text-teal" />
                  <span>Workforce</span>
                </div>
                <p className="text-sm text-muted-foreground">{profile.workforce}</p>
              </div>

              <div>
                <div className="flex items-center gap-2 text-sm font-medium mb-2">
                  <GraduationCap className="w-4 h-4 text-teal" />
                  <span>Key Skills</span>
                </div>
                <div className="flex flex-wrap gap-1">
                  {profile.skills.map((skill) => (
                    <Badge key={skill} variant="secondary" className="text-xs">
                      {skill}
                    </Badge>
                  ))}
                </div>
              </div>

              <div>
                <div className="flex items-center gap-2 text-sm font-medium mb-2">
                  <DollarSign className="w-4 h-4 text-teal" />
                  <span>Income Level</span>
                </div>
                <p className="text-sm text-muted-foreground">{profile.income}</p>
              </div>

              <div>
                <div className="flex items-center gap-2 text-sm font-medium mb-2">
                  <TrendingUp className="w-4 h-4 text-teal" />
                  <span>Employment Rate</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex-1 h-2 bg-secondary rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-teal rounded-full" 
                      style={{ width: profile.employment }}
                    />
                  </div>
                  <span className="text-sm font-semibold">{profile.employment}</span>
                </div>
              </div>

              <div>
                <div className="text-sm font-medium mb-2">Commercial Gaps</div>
                <div className="flex flex-wrap gap-1">
                  {profile.gaps.map((gap) => (
                    <Badge key={gap} variant="outline" className="text-xs">
                      {gap}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Business Recommendations */}
          <div className="lg:col-span-2 space-y-4">
            <div className="animate-fade-in" style={{ animationDelay: "300ms" }}>
              <h2 className="font-heading text-2xl font-semibold mb-2">
                Recommended Businesses
              </h2>
              <p className="text-muted-foreground text-sm mb-4">
                Based on zone profile analysis and commercial gap assessment
              </p>
            </div>

            <div className="grid grid-cols-1 gap-4">
              {businesses.map((business, idx) => (
                <Card 
                  key={business.name}
                  className="shadow-md hover:shadow-lg transition-all animate-fade-in"
                  style={{ animationDelay: `${400 + idx * 50}ms` }}
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <Building2 className="w-5 h-5 text-primary" />
                          <CardTitle className="font-heading text-lg">{business.name}</CardTitle>
                        </div>
                        <CardDescription className="text-sm italic">
                          {business.tagline}
                        </CardDescription>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-teal">{business.score}</div>
                        <div className="text-xs text-muted-foreground">Match Score</div>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div>
                      <div className="text-xs font-medium text-muted-foreground mb-1">Why it fits</div>
                      <p className="text-sm">{business.fit}</p>
                    </div>

                    <div className="w-full h-2 bg-secondary rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-teal to-primary rounded-full transition-all duration-500"
                        style={{ width: `${business.score}%` }}
                      />
                    </div>

                    <div className="flex flex-wrap gap-1">
                      {business.tags.map((tag) => (
                        <Badge key={tag} className="text-xs bg-teal/10 text-teal border-teal/20">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            <Card className="shadow-lg animate-fade-in" style={{ animationDelay: "700ms" }}>
              <CardHeader>
                <CardTitle className="font-heading text-sm">About This Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted-foreground">
                  This section simulates a semantic matching engine that pairs businesses with neighborhoods based on demographic profiles, 
                  commercial gaps, workforce characteristics, and economic indicators. All data shown is mock data for demonstration purposes.
                  In a production environment, this would leverage real demographic data, business registries, and machine learning models.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BusinessMatcher;
