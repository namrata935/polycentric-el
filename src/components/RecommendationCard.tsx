import React from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertTriangle, TrendingUp, Info, Target } from "lucide-react";
import { Recommendation } from "@/hooks/use-recommendations";

interface RecommendationCardProps {
  recommendation: Recommendation | null;
  isLoading?: boolean;
  error?: Error | null;
}

const priorityConfig = {
  critical: {
    color: "border-red-500 bg-red-50",
    icon: AlertTriangle,
    label: "Critical",
    textColor: "text-red-700",
  },
  high: {
    color: "border-orange-500 bg-orange-50",
    icon: TrendingUp,
    label: "High",
    textColor: "text-orange-700",
  },
  medium: {
    color: "border-yellow-500 bg-yellow-50",
    icon: Info,
    label: "Medium",
    textColor: "text-yellow-700",
  },
  low: {
    color: "border-green-500 bg-green-50",
    icon: Target,
    label: "Low",
    textColor: "text-green-700",
  },
};

const sentimentColorMap = {
  very_positive: "text-green-600 bg-green-50",
  positive: "text-green-500 bg-green-100",
  neutral: "text-gray-500 bg-gray-100",
  negative: "text-orange-500 bg-orange-100",
  very_negative: "text-red-600 bg-red-50",
};

export const RecommendationCard: React.FC<RecommendationCardProps> = ({
  recommendation,
  isLoading = false,
  error = null,
}) => {
  if (isLoading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Recommendation</CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-32">
          <div className="animate-pulse">Loading recommendation...</div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="w-full border-red-300">
        <CardHeader>
          <CardTitle className="text-red-600">Error</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-600">{error.message}</p>
        </CardContent>
      </Card>
    );
  }

  if (!recommendation) {
    return null;
  }

  const priorityConfig_ = priorityConfig[recommendation.priority];
  const PriorityIcon = priorityConfig_.icon;

  return (
    <Card className={`w-full border-2 ${priorityConfig_.color}`}>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <PriorityIcon
                className={`w-5 h-5 ${priorityConfig_.textColor}`}
              />
              <CardTitle className={`text-lg ${priorityConfig_.textColor}`}>
                {priorityConfig_.label} Priority
              </CardTitle>
            </div>
            <CardDescription className="text-sm">
              <span className="font-semibold">{recommendation.zone_type}</span>
              {" • "}
              <span
                className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                  sentimentColorMap[recommendation.sentiment_level]
                }`}
              >
                {recommendation.sentiment_level.replace(/_/g, " ")}
              </span>
            </CardDescription>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold">
              {recommendation.sentiment_score > 0 ? "+" : ""}
              {recommendation.sentiment_score}
            </div>
            <p className="text-xs text-gray-500">Sentiment Score</p>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Primary Recommendation */}
        <Alert className="border-l-4 border-l-blue-500 bg-blue-50">
          <AlertDescription className="text-sm font-semibold text-blue-900">
            {recommendation.primary_recommendation}
          </AlertDescription>
        </Alert>

        {/* Additional Recommendations */}
        {recommendation.all_recommendations.length > 1 && (
          <div className="space-y-2">
            <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
              Additional Insights
            </p>
            <ul className="space-y-1">
              {recommendation.all_recommendations.slice(1).map((rec, idx) => (
                <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                  <span className="text-blue-500 mt-1">•</span>
                  <span>{rec.text}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Focus Areas */}
        {recommendation.focus_areas.length > 0 && (
          <div className="pt-2 border-t">
            <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide mb-2">
              Focus Areas
            </p>
            <div className="flex flex-wrap gap-2">
              {recommendation.focus_areas.map((area) => (
                <span
                  key={area}
                  className="px-3 py-1 bg-blue-100 text-blue-700 text-xs rounded-full font-medium"
                >
                  {area.replace(/_/g, " ")}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Context Insights */}
        <div className="pt-2 border-t grid grid-cols-2 gap-3">
          <div className="space-y-1">
            <p className="text-xs text-gray-500 uppercase tracking-wider">
              Business Density
            </p>
            <p className="text-sm font-semibold capitalize text-gray-700">
              {recommendation.context.business_density}
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-gray-500 uppercase tracking-wider">
              Transport Access
            </p>
            <p className="text-sm font-semibold capitalize text-gray-700">
              {recommendation.context.transport_access}
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-gray-500 uppercase tracking-wider">
              Population Level
            </p>
            <p className="text-sm font-semibold capitalize text-gray-700">
              {recommendation.context.population_level}
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-gray-500 uppercase tracking-wider">
              Sentiment Trend
            </p>
            <p
              className={`text-sm font-semibold capitalize ${
                sentimentColorMap[recommendation.sentiment_level]
              }`}
            >
              {recommendation.context.sentiment_trend.replace(/_/g, " ")}
            </p>
          </div>
        </div>

        {/* Amenity Gaps */}
        {Object.keys(recommendation.context.amenity_gaps).length > 0 && (
          <div className="pt-2 border-t space-y-2">
            <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
              Amenity Coverage
            </p>
            <div className="space-y-1">
              {Object.entries(recommendation.context.amenity_gaps).map(
                ([amenity, coverage]) => (
                  <div key={amenity} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 capitalize">
                      {amenity.replace(/_/g, " ")}
                    </span>
                    <div className="w-20 bg-gray-200 rounded-full h-1.5">
                      <div
                        className="bg-blue-500 h-1.5 rounded-full"
                        style={{
                          width: coverage,
                        }}
                      />
                    </div>
                    <span className="text-xs text-gray-500 w-10 text-right">
                      {coverage}
                    </span>
                  </div>
                )
              )}
            </div>
          </div>
        )}

        {/* Recommended Actions */}
        {recommendation.recommended_actions.length > 0 && (
          <div className="pt-2 border-t space-y-2">
            <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
              Recommended Actions
            </p>
            <ul className="space-y-1">
              {recommendation.recommended_actions.map((action) => (
                <li
                  key={action}
                  className="text-sm text-gray-700 flex items-start gap-2"
                >
                  <span className="text-green-500 mt-1">✓</span>
                  <span className="capitalize">{action.replace(/_/g, " ")}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default RecommendationCard;
