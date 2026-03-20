"use client";

import { Badge } from "@/components/ui";

export interface AuditEventBadgeProps {
  eventType: string;
  size?: "sm" | "md";
}

const eventTypeMap: Record<string, { label: string; color: "green" | "blue" | "gray" | "purple" | "yellow" | "red" | "orange" }> = {
  SYSTEM_REGISTERED: { label: "Registered", color: "green" },
  SYSTEM_UPDATED: { label: "Updated", color: "blue" },
  SYSTEM_ARCHIVED: { label: "Archived", color: "gray" },
  CLASSIFICATION_COMPLETED: { label: "Classified", color: "purple" },
  APPROVAL_CREATED: { label: "Approval Needed", color: "yellow" },
  APPROVAL_APPROVED: { label: "Approved", color: "green" },
  APPROVAL_REJECTED: { label: "Rejected", color: "red" },
  POLICY_ENFORCED: { label: "Policy Applied", color: "orange" },
  RISK_ALERT_TRIGGERED: { label: "Risk Alert", color: "red" },
};

export function AuditEventBadge({ eventType, size = "md" }: AuditEventBadgeProps) {
  const config = eventTypeMap[eventType] || { label: eventType, color: "gray" };

  return (
    <Badge variant={config.color} size={size}>
      {config.label}
    </Badge>
  );
}
