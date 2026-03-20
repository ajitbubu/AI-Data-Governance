/**
 * DataSafeguard API Client
 * Typed client for the FastAPI backend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// ── Types ──

export interface AISystem {
  id: string;
  name: string;
  description: string | null;
  version: string | null;
  owner_id: string | null;
  team_id: string | null;
  purpose_statement: string;
  model_type: string;
  deployment_env: string;
  deployment_geo: string[] | null;
  affected_population: string | null;
  decision_automation: string;
  sector: string;
  data_sensitivity: string;
  eu_risk_tier: string;
  us_designation: string;
  risk_score: number | null;
  classification_confidence: string | null;
  classification_rationale: Record<string, unknown> | null;
  status: string;
  metadata_extra: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface AISystemListItem {
  id: string;
  name: string;
  model_type: string;
  deployment_env: string;
  sector: string;
  eu_risk_tier: string;
  us_designation: string;
  risk_score: number | null;
  status: string;
  owner_id: string | null;
  team_id: string | null;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface Stats {
  total_systems: number;
  by_eu_tier: Record<string, number>;
  by_us_designation: Record<string, number>;
  by_status: Record<string, number>;
  by_sector: Record<string, number>;
  pending_approvals: number;
}

export interface RiskClassification {
  id: string;
  system_id: string;
  eu_risk_tier: string;
  us_designation: string;
  risk_score: number;
  confidence: string;
  eu_rationale: Record<string, unknown>;
  us_rationale: Record<string, unknown>;
  matched_annex_iii_categories: string[] | null;
  matched_omb_categories: string[] | null;
  classified_at: string;
  classified_by: string;
  classifier_version: string;
}

export interface CreateSystemPayload {
  name: string;
  description?: string;
  purpose_statement: string;
  model_type: string;
  deployment_env: string;
  deployment_geo?: string[];
  affected_population?: string;
  decision_automation: string;
  sector: string;
  data_sensitivity: string;
  metadata_extra?: Record<string, unknown>;
}

export interface AuditEvent {
  id: string;
  event_type: string;
  entity_type: string;
  entity_id: string;
  actor_id: string | null;
  actor_email: string | null;
  action: string;
  changes: { before?: Record<string, unknown>; after?: Record<string, unknown> } | null;
  metadata: Record<string, unknown> | null;
  ip_address: string;
  request_id: string;
  created_at: string;
}

export interface AuditEventListItem {
  id: string;
  event_type: string;
  entity_type: string;
  entity_id: string;
  action: string;
  actor_email: string | null;
  created_at: string;
}

export interface AuditStats {
  total_events: number;
  by_event_type: Record<string, number>;
  by_entity_type: Record<string, number>;
  events_per_day: Array<{ date: string; count: number }>;
}

// ── API Functions ──

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000); // 30s timeout

  try {
    const res = await fetch(`${API_BASE}${path}`, {
      headers: { "Content-Type": "application/json", ...options?.headers },
      ...options,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(error.detail || `API Error: ${res.status}`);
    }
    return res.json();
  } catch (err: any) {
    clearTimeout(timeoutId);
    if (err.name === "AbortError") {
      throw new Error(
        "Request timed out. Please check that the API server is running and try again."
      );
    }
    // Network errors (CORS blocked, server down, etc.)
    if (err instanceof TypeError && err.message === "Failed to fetch") {
      throw new Error(
        `Cannot reach the API server at ${API_BASE}. Please verify the backend is running.`
      );
    }
    throw err;
  }
}

export const api = {
  // Systems
  listSystems: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return apiFetch<PaginatedResponse<AISystemListItem>>(`/systems${qs}`);
  },

  getSystem: (id: string) => apiFetch<AISystem>(`/systems/${id}`),

  createSystem: (data: CreateSystemPayload) =>
    apiFetch<AISystem>("/systems", { method: "POST", body: JSON.stringify(data) }),

  updateSystem: (id: string, data: Partial<CreateSystemPayload>) =>
    apiFetch<AISystem>(`/systems/${id}`, { method: "PUT", body: JSON.stringify(data) }),

  deleteSystem: (id: string) =>
    apiFetch<{ message: string }>(`/systems/${id}`, { method: "DELETE" }),

  classifySystem: (id: string) =>
    apiFetch<AISystem>(`/systems/${id}/classify`, { method: "POST" }),

  getClassification: (id: string) =>
    apiFetch<RiskClassification | null>(`/systems/${id}/classification`),

  getClassificationHistory: (id: string) =>
    apiFetch<RiskClassification[]>(`/systems/${id}/classification/history`),

  getStats: () => apiFetch<Stats>("/systems/stats"),

  getVersionHistory: (id: string) =>
    apiFetch<Array<{ id: string; version_number: number; snapshot: Record<string, unknown>; change_summary: string | null; created_at: string }>>(`/systems/${id}/history`),

  // Audit
  listAuditEvents: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return apiFetch<PaginatedResponse<AuditEventListItem>>(`/audit/events${qs}`);
  },

  getAuditEvent: (id: string) => apiFetch<AuditEvent>(`/audit/events/${id}`),

  getAuditStats: () => apiFetch<AuditStats>(`/audit/events/stats`),

  getEntityTimeline: (entityType: string, entityId: string) =>
    apiFetch<AuditEventListItem[]>(`/audit/events/timeline/${entityType}/${entityId}`),
};
