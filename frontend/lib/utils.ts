import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const EU_TIER_COLORS: Record<string, { bg: string; text: string; label: string }> = {
  prohibited: { bg: "bg-red-100", text: "text-red-800", label: "Prohibited" },
  high: { bg: "bg-orange-100", text: "text-orange-800", label: "High" },
  limited: { bg: "bg-yellow-100", text: "text-yellow-800", label: "Limited" },
  minimal: { bg: "bg-green-100", text: "text-green-800", label: "Minimal" },
  not_classified: { bg: "bg-gray-100", text: "text-gray-600", label: "Not Classified" },
};

export const US_DESIGNATION_COLORS: Record<string, { bg: string; text: string; label: string }> = {
  high_impact: { bg: "bg-red-100", text: "text-red-800", label: "High-Impact" },
  standard: { bg: "bg-blue-100", text: "text-blue-800", label: "Standard" },
  not_classified: { bg: "bg-gray-100", text: "text-gray-600", label: "Not Classified" },
};

export const STATUS_COLORS: Record<string, { bg: string; text: string }> = {
  draft: { bg: "bg-gray-100", text: "text-gray-700" },
  active: { bg: "bg-green-100", text: "text-green-700" },
  under_review: { bg: "bg-yellow-100", text: "text-yellow-700" },
  retired: { bg: "bg-red-100", text: "text-red-700" },
  archived: { bg: "bg-gray-200", text: "text-gray-500" },
};
