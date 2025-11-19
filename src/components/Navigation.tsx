import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import { MapPin, Building2, Heart } from "lucide-react";

const Navigation = () => {
  const location = useLocation();

  const links = [
    {
      to: "/opportunity-zones",
      label: "Opportunity Zones",
      icon: MapPin,
    },
    {
      to: "/business-matcher",
      label: "Business Matcher",
      icon: Building2,
    },
    {
      to: "/livability",
      label: "Livability Pulse",
      icon: Heart,
    },
  ];

  return (
    <nav className="border-b bg-card/50 backdrop-blur-sm sticky top-0 z-50 shadow-sm">
      <div className="container mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
              <div className="w-4 h-4 border-2 border-primary-foreground rounded-sm" />
            </div>
            <span className="font-heading font-bold text-lg text-foreground">
              PolyCentric Urban Insights
            </span>
          </div>

          <div className="flex items-center gap-1">
            {links.map((link) => {
              const Icon = link.icon;
              const isActive = location.pathname === link.to;
              
              return (
                <Link
                  key={link.to}
                  to={link.to}
                  className={cn(
                    "flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all duration-200",
                    isActive
                      ? "bg-primary text-primary-foreground shadow-sm"
                      : "text-muted-foreground hover:text-foreground hover:bg-secondary"
                  )}
                >
                  <Icon className="w-4 h-4" />
                  {link.label}
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
