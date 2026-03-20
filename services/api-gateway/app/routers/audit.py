"""
UC-4: Audit Trail & Observability — API Router.

Endpoints:
  GET    /audit/events              List events with pagination + filters
  GET    /audit/events/stats        Aggregate statistics
  GET    /audit/events/{event_id}   Get single event detail
  GET    /audit/events/entity/{entity_type}/{entity_id}  Events for an entity
  GET    /audit/events/timeline/{entity_type}/{entity_id} Timeline for entity
  GET    /audit/events/export       CSV export
  GET    /audit/events/export/json  JSON export
"""
import uuid
import csv
import io
import json
from math import ceil
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.database import get_db
from ..repositories.audit_repo import AuditRepository
from ..schemas.audit import (
    AuditEventResponse,
    AuditEventListItem,
    AuditTimelineItem,
    AuditStatsResponse,
)
from ..schemas.common import PaginatedResponse

router = APIRouter(prefix="/audit", tags=["Audit Trail"])


def get_repository(db: AsyncSession = Depends(get_db)) -> AuditRepository:
    """Dependency to get audit repository instance."""
    return AuditRepository(db)


# ── Helper Functions ──


def _make_list_item(event) -> AuditEventListItem:
    """Convert AuditEvent to AuditEventListItem with summary."""
    summary = f"{event.action}: {event.entity_type} {event.entity_id}"
    if event.event_type:
        summary = f"{event.event_type}: {summary}"
    return AuditEventListItem(
        id=event.id,
        event_type=event.event_type,
        entity_type=event.entity_type,
        entity_id=event.entity_id,
        action=event.action,
        actor_email=event.actor_email,
        created_at=event.created_at,
        summary=summary,
    )


def _make_timeline_item(event) -> AuditTimelineItem:
    """Convert AuditEvent to AuditTimelineItem with changes summary."""
    changes_summary = None
    if event.changes and isinstance(event.changes, dict):
        before = event.changes.get("before", {})
        after = event.changes.get("after", {})
        # Build a human-readable summary of what changed
        if before and after:
            changes = []
            for key in set(list(before.keys()) + list(after.keys())):
                old_val = before.get(key)
                new_val = after.get(key)
                if old_val != new_val:
                    changes.append(f"{key}: {old_val} → {new_val}")
            if changes:
                changes_summary = "; ".join(changes)

    return AuditTimelineItem(
        id=event.id,
        event_type=event.event_type,
        action=event.action,
        changes_summary=changes_summary,
        actor_email=event.actor_email,
        created_at=event.created_at,
        metadata=event.event_metadata,
    )


# ── Retrieve Single Event ──


@router.get("/events/{event_id}", response_model=AuditEventResponse)
async def get_event(
    event_id: uuid.UUID,
    repo: AuditRepository = Depends(get_repository),
):
    """
    Get a single audit event by ID.

    Returns full event details including changes and metadata.
    """
    event = await repo.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Audit event {event_id} not found")
    return event


# ── List Events ──


@router.get("/events", response_model=PaginatedResponse[AuditEventListItem])
async def list_events(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    event_type: str | None = Query(
        None, description="Filter by event type (e.g., SYSTEM_REGISTERED)"
    ),
    entity_type: str | None = Query(None, description="Filter by entity type"),
    entity_id: uuid.UUID | None = Query(None, description="Filter by entity UUID"),
    actor_id: uuid.UUID | None = Query(None, description="Filter by actor UUID"),
    date_from: datetime | None = Query(None, description="Start date (inclusive)"),
    date_to: datetime | None = Query(None, description="End date (inclusive)"),
    search: str | None = Query(None, description="Search in action and actor_email"),
    sort_by: str = Query("created_at", description="Column to sort by"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    repo: AuditRepository = Depends(get_repository),
):
    """
    List audit events with comprehensive filtering, search, and pagination.

    Supports filtering by:
    - event_type: Event classification (SYSTEM_REGISTERED, CLASSIFICATION_COMPLETED, etc.)
    - entity_type: Type of resource affected (ai_system, approval, etc.)
    - entity_id: Specific resource UUID
    - actor_id: User who performed action
    - date_from/date_to: Date range
    - search: Full-text search on action and email

    Results are paginated. Use page and page_size to navigate.
    """
    events, total = await repo.list_events(
        page=page,
        page_size=page_size,
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        actor_id=actor_id,
        date_from=date_from,
        date_to=date_to,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    items = [_make_list_item(event) for event in events]
    total_pages = ceil(total / page_size) if total > 0 else 0

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


# ── Statistics ──


@router.get("/events/stats", response_model=AuditStatsResponse)
async def get_stats(repo: AuditRepository = Depends(get_repository)):
    """
    Get aggregate audit statistics.

    Returns:
    - total_events: Total count of all audit events
    - by_event_type: Count breakdown by event type
    - by_entity_type: Count breakdown by entity type
    - events_per_day: Daily event counts for last 30 days
    """
    return await repo.get_event_stats()


# ── Entity Events ──


@router.get(
    "/events/entity/{entity_type}/{entity_id}", response_model=list[AuditEventResponse]
)
async def get_entity_events(
    entity_type: str,
    entity_id: uuid.UUID,
    repo: AuditRepository = Depends(get_repository),
):
    """
    Get all audit events for a specific entity (system, approval, etc.).

    Returns complete event history for that resource, ordered by created_at descending.
    Useful for reconstructing the full lifecycle of a system or approval.
    """
    return await repo.get_events_for_entity(entity_type, entity_id)


# ── Timeline ──


@router.get(
    "/events/timeline/{entity_type}/{entity_id}", response_model=list[AuditTimelineItem]
)
async def get_timeline(
    entity_type: str,
    entity_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=500, description="Max events to return"),
    repo: AuditRepository = Depends(get_repository),
):
    """
    Get a chronological timeline of events for an entity (for timeline UI).

    Returns compact timeline items with human-readable change summaries.
    Limited to most recent N events (default 50).
    """
    events = await repo.get_timeline(entity_type, entity_id, limit=limit)
    return [_make_timeline_item(event) for event in events]


# ── Export ──


@router.get("/events/export")
async def export_events_csv(
    event_type: str | None = Query(None),
    entity_type: str | None = Query(None),
    entity_id: uuid.UUID | None = Query(None),
    actor_id: uuid.UUID | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    search: str | None = Query(None),
    repo: AuditRepository = Depends(get_repository),
):
    """
    Export audit events as CSV.

    Supports same filters as list endpoint. Returns all matching events
    (no pagination) for auditors to download complete audit trails.

    CSV columns: id, event_type, entity_type, entity_id, action, actor_email, created_at, ip_address, request_id
    """
    events = await repo.export_events(
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        actor_id=actor_id,
        date_from=date_from,
        date_to=date_to,
        search=search,
    )

    # Generate CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "id",
            "event_type",
            "entity_type",
            "entity_id",
            "action",
            "actor_email",
            "created_at",
            "ip_address",
            "request_id",
        ]
    )

    for event in events:
        writer.writerow(
            [
                str(event.id),
                event.event_type,
                event.entity_type,
                str(event.entity_id),
                event.action,
                event.actor_email or "",
                event.created_at.isoformat(),
                event.ip_address,
                event.request_id,
            ]
        )

    # Return as streaming response
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_events.csv"},
    )


@router.get("/events/export/json")
async def export_events_json(
    event_type: str | None = Query(None),
    entity_type: str | None = Query(None),
    entity_id: uuid.UUID | None = Query(None),
    actor_id: uuid.UUID | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    search: str | None = Query(None),
    repo: AuditRepository = Depends(get_repository),
):
    """
    Export audit events as JSON.

    Returns all matching events as JSON array with full event details.
    """
    events = await repo.export_events(
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        actor_id=actor_id,
        date_from=date_from,
        date_to=date_to,
        search=search,
    )

    # Convert to JSON-serializable format
    events_data = []
    for event in events:
        events_data.append(
            {
                "id": str(event.id),
                "event_type": event.event_type,
                "entity_type": event.entity_type,
                "entity_id": str(event.entity_id),
                "actor_id": str(event.actor_id) if event.actor_id else None,
                "actor_email": event.actor_email,
                "action": event.action,
                "changes": event.changes,
                "metadata": event.event_metadata,
                "ip_address": event.ip_address,
                "request_id": event.request_id,
                "created_at": event.created_at.isoformat(),
            }
        )

    return StreamingResponse(
        iter([json.dumps(events_data, indent=2)]),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=audit_events.json"},
    )
