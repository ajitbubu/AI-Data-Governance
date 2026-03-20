"""Pydantic schemas for Audit Trail & Observability (UC-4)."""
import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field, ConfigDict


# ── Response Schemas ──

class AuditEventResponse(BaseModel):
    """Full audit event representation with all fields."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    event_type: str = Field(
        ..., description="Event type (e.g., SYSTEM_REGISTERED, CLASSIFICATION_COMPLETED)"
    )
    entity_type: str = Field(..., description="Type of entity affected (e.g., ai_system)")
    entity_id: uuid.UUID = Field(..., description="UUID of the affected entity")
    actor_id: uuid.UUID | None = Field(None, description="User who performed the action")
    actor_email: str | None = Field(None, description="Email of actor at time of action")
    action: str = Field(..., description="Specific action (create, update, classify, approve)")
    changes: dict[str, Any] | None = Field(
        None, description="JSON diff with 'before' and 'after' keys"
    )
    metadata: dict[str, Any] | None = Field(None, description="Event-specific metadata")
    ip_address: str = Field(..., description="Client IP address")
    request_id: str = Field(..., description="Correlation ID for distributed tracing")
    created_at: datetime = Field(..., description="When event was recorded (ISO 8601 UTC)")


class AuditEventListItem(BaseModel):
    """Compact audit event for list views (reduced payload for pagination)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    event_type: str
    entity_type: str
    entity_id: uuid.UUID
    action: str
    actor_email: str | None
    created_at: datetime
    summary: str = Field(
        ..., description="Human-readable summary (e.g., 'System registered as High risk')"
    )


class AuditTimelineItem(BaseModel):
    """Compact event for entity timeline/activity feed view."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    event_type: str
    action: str
    changes_summary: str | None = Field(
        None, description="Human-readable summary of changes (e.g., 'EU tier: minimal → high')"
    )
    actor_email: str | None
    created_at: datetime
    metadata: dict[str, Any] | None


class AuditStatsResponse(BaseModel):
    """Aggregate audit statistics for dashboard."""

    total_events: int = Field(..., description="Total audit events in system")
    by_event_type: dict[str, int] = Field(
        ..., description="Count of events by event type"
    )
    by_entity_type: dict[str, int] = Field(
        ..., description="Count of events by entity type"
    )
    events_per_day: list[dict[str, Any]] = Field(
        ..., description="Daily event counts for last 30 days"
    )


class AuditExportRequest(BaseModel):
    """Filter parameters for audit event export."""

    event_type: str | None = Field(None, description="Filter by event type")
    entity_type: str | None = Field(None, description="Filter by entity type")
    entity_id: uuid.UUID | None = Field(None, description="Filter by entity UUID")
    actor_id: uuid.UUID | None = Field(None, description="Filter by actor UUID")
    date_from: datetime | None = Field(None, description="Start date (inclusive)")
    date_to: datetime | None = Field(None, description="End date (inclusive)")
    search: str | None = Field(None, description="Search in action and actor_email")
