"use client";

import { Card, CardContent, CardDescription, CardTitle } from "./card";
import { Skeleton } from "./skeleton";
import { cn } from "@/lib/utils";

export interface StatCardProps {
  label: string;
  value: number | string;
  description?: string;
  trend?: {
    value: number;
    direction: "up" | "down";
  };
  icon?: React.ReactNode;
  size?: "compact" | "expanded";
  loading?: boolean;
  color?: "blue" | "green" | "red" | "orange" | "yellow";
}

const colorStyles = {
  blue: "bg-blue-50 border-blue-200",
  green: "bg-green-50 border-green-200",
  red: "bg-red-50 border-red-200",
  orange: "bg-orange-50 border-orange-200",
  yellow: "bg-yellow-50 border-yellow-200",
};

const trendColorMap = {
  up: "text-green-600",
  down: "text-red-600",
};

export function StatCard({
  label,
  value,
  description,
  trend,
  icon,
  size = "expanded",
  loading = false,
  color = "blue",
}: StatCardProps) {
  if (loading) {
    return (
      <Card className={cn("border-2", colorStyles[color])}>
        <CardContent className="pt-6">
          <Skeleton variant="text" height={16} width="60%" className="mb-4" />
          <Skeleton variant="rect" height={40} width="80%" className="mb-2" />
          <Skeleton variant="text" height={12} width="40%" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn("border-2", colorStyles[color])}>
      <CardContent className={cn(size === "expanded" ? "pt-6" : "p-4")}>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardDescription>{label}</CardDescription>
            <div className={cn("font-bold text-gray-900 mt-2", size === "expanded" ? "text-3xl" : "text-2xl")}>
              {value}
            </div>
            {description && (
              <p className="text-xs text-gray-600 mt-1">{description}</p>
            )}
            {trend && (
              <div className={cn("text-xs font-medium mt-2", trendColorMap[trend.direction])}>
                {trend.direction === "up" ? "↑" : "↓"} {trend.value}%
              </div>
            )}
          </div>
          {icon && <div className="text-2xl ml-4">{icon}</div>}
        </div>
      </CardContent>
    </Card>
  );
}
