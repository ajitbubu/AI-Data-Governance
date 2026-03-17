import { Badge } from "@/components/ui/badge";
import { EU_TIER_COLORS, US_DESIGNATION_COLORS } from "@/lib/utils";

interface EURiskBadgeProps {
  tier: string;
  size?: "sm" | "md" | "lg";
}

export function EURiskBadge({ tier, size = "md" }: EURiskBadgeProps) {
  const colors = EU_TIER_COLORS[tier] || EU_TIER_COLORS.not_classified;
  const variantMap: Record<string, "default" | "destructive" | "warning" | "success" | "outline" | "secondary"> = {
    prohibited: "destructive",
    high: "warning",
    limited: "warning",
    minimal: "success",
    not_classified: "outline",
  };

  return (
    <Badge variant={variantMap[tier] || "outline"} size={size}>
      {colors.label}
    </Badge>
  );
}

interface USDesignationBadgeProps {
  designation: string;
  size?: "sm" | "md" | "lg";
}

export function USDesignationBadge({ designation, size = "md" }: USDesignationBadgeProps) {
  const colors = US_DESIGNATION_COLORS[designation] || US_DESIGNATION_COLORS.not_classified;
  const variantMap: Record<string, "default" | "destructive" | "warning" | "success" | "outline" | "secondary"> = {
    high_impact: "destructive",
    standard: "default",
    not_classified: "outline",
  };

  return (
    <Badge variant={variantMap[designation] || "outline"} size={size}>
      {colors.label}
    </Badge>
  );
}

interface RiskScoreBadgeProps {
  score: number;
  size?: "sm" | "md" | "lg";
}

export function RiskScoreBadge({ score, size = "md" }: RiskScoreBadgeProps) {
  let variant: "default" | "destructive" | "warning" | "success" | "outline" | "secondary" = "success";
  if (score > 70) variant = "destructive";
  else if (score > 40) variant = "warning";

  return (
    <Badge variant={variant} size={size}>
      {score.toFixed(1)}
    </Badge>
  );
}
