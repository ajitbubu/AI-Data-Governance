"""Data access layer for Audit Events (UC-4 Audit Trail & Observability)."""
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func, desc, and_, or_, cast, String, Date
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.audit_event import AuditEvent


class AuditRepository:
    """Repository for querying audit events with filtering, pagination, and aggregation."""

    def __init__(self, db: AsyncSession):
        """
        Initialize audit repository.

        Args:
            db: SQLAlchemy async session for database operations
        """
        self.db = db

    # ── Retrieve ──

    async def get_by_id(self, event_id: uuid.UUID) -> AuditEvent | None:
        """
        Retrieve a single audit event by ID.

        Args:
            event_id: UUID of the audit event

        Returns:
            AuditEvent or None if not found
        """
        result = await self.db.execute(
            select(AuditEvent).where(AuditEvent.id == event_id)
        )
        return result.scalar_one_or_none()

    # ── List & Search ──

    async def list_events(
        self,
        page: int = 1,
        page_size: int = 20,
        event_type: str | None = None,
        entity_type: str | None = None,
        entity_id: uuid.UUID | None = None,
        actor_id: uuid.UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[AuditEvent], int]:
        """
        List audit events with comprehensive filtering and pagination.

        Args:
            page: Page number (1-indexed)
            page_size: Items per page
            event_type: Filter by event type (e.g., SYSTEM_REGISTERED)
            entity_type: Filter by entity type (e.g., ai_system)
            entity_id: Filter by specific entity UUID
            actor_id: Filter by user who performed action
            date_from: Start date filter (inclusive)
            date_to: End date filter (inclusive)
            search: Full-text search on action and metadata
            sort_by: Column to sort by (created_at, event_type, action, etc.)
            sort_order: asc or desc

        Returns:
            Tuple of (list of events, total count)
        """
        query = select(AuditEvent)
        count_query = select(func.count(AuditEvent.id))

        # Build filter conditions
        conditions = []

        if event_type:
            conditions.append(AuditEvent.event_type == event_type)

        if entity_type:
            conditions.append(AuditEvent.entity_type == entity_type)

        if entity_id:
            conditions.append(AuditEvent.entity_id == entity_id)

        if actor_id:
            conditions.append(AuditEvent.actor_id == actor_id)

        if date_from:
            conditions.append(AuditEvent.created_at >= date_from)

        if date_to:
            # Include entire end date
            end_of_day = date_to.replace(hour=23, minute=59, second=59, microsecond=999999)
            conditions.append(AuditEvent.created_at <= end_of_day)

        if search:
            # Search in action and actor_email
            search_pattern = f"%{search}%"
            conditions.append(
                or_(
                    AuditEvent.action.ilike(search_pattern),
                    AuditEvent.actor_email.ilike(search_pattern),
                )
            )

        if conditions:
            filter_clause = and_(*conditions)
            query = query.where(filter_clause)
            count_query = count_query.where(filter_clause)

        # Count total
        total = (await self.db.execute(count_query)).scalar() or 0

        # Sort
        sort_col = getattr(AuditEvent, sort_by, AuditEvent.created_at)
        if sort_order == "desc":
            query = query.order_by(desc(sort_col))
        else:
            query = query.order_by(sort_col)

        # Paginate
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        return result.scalars().all(), total

    # ── Entity Timeline ──

    async def get_events_for_entity(
        self,
        entity_type: str,
        entity_id: uuid.UUID,
    ) -> list[AuditEvent]:
        """
        Get all audit events for a specific entity.

        Useful for reconstructing the full history of a system or approval workflow.

        Args:
            entity_type: Type of entity (e.g., ai_system)
            entity_id: UUID of the entity

        Returns:
            List of all audit events for that entity, ordered by created_at desc
        """
        result = await self.db.execute(
            select(AuditEvent)
            .where(
                and_(
                    AuditEvent.entity_type == entity_type,
                    AuditEvent.entity_id == entity_id,
                )
            )
            .order_by(desc(AuditEvent.created_at))
        )
        return result.scalars().all()

    async def get_timeline(
        self,
        entity_type: str,
        entity_id: uuid.UUID,
        limit: int = 50,
    ) -> list[AuditEvent]:
        """
        Get a chronological timeline of events for an entity (for timeline UI).

        Args:
            entity_type: Type of entity
            entity_id: UUID of entity
            limit: Maximum number of recent events

        Returns:
            List of events, newest first
        """
        result = await self.db.execute(
            select(AuditEvent)
            .where(
                and_(
                    AuditEvent.entity_type == entity_type,
                    AuditEvent.entity_id == entity_id,
                )
            )
            .order_by(desc(AuditEvent.created_at))
            .limit(limit)
        )
        return result.scalars().all()

    # ── Aggregation & Stats ──

    async def get_event_stats(self) -> dict:
        """
        Get aggregate statistics on audit events.

        Returns statistics including:
        - total_events: Total count of all events
        - by_event_type: Count breakdown by event type
        - by_entity_type: Count breakdown by entity type
        - events_per_day: Daily event counts for last 30 days

        Returns:
            Dictionary with aggregated statistics
        """
        # Total events
        total = (await self.db.execute(select(func.count(AuditEvent.id)))).scalar() or 0

        # By event type
        event_type_result = await self.db.execute(
            select(AuditEvent.event_type, func.count(AuditEvent.id))
            .group_by(AuditEvent.event_type)
        )
        by_event_type = dict(event_type_result.all()) if event_type_result else {}

        # By entity type
        entity_type_result = await self.db.execute(
            select(AuditEvent.entity_type, func.count(AuditEvent.id))
            .group_by(AuditEvent.entity_type)
        )
        by_entity_type = dict(entity_type_result.all()) if entity_type_result else {}

        # Events per day (last 30 days)
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        daily_result = await self.db.execute(
            select(
                cast(AuditEvent.created_at, Date).label("date"),
                func.count(AuditEvent.id).label("count"),
            )
            .where(AuditEvent.created_at >= thirty_days_ago)
            .group_by(cast(AuditEvent.created_at, Date))
            .order_by("date")
        )
        events_per_day = [
            {"date": str(row.date), "count": row.count} for row in daily_result.all()
        ]

        return {
            "total_events": total,
            "by_event_type": by_event_type,
            "by_entity_type": by_entity_type,
            "events_per_day": events_per_day,
        }

    # ── Export ──

    async def export_events(
        self,
        event_type: str | None = None,
        entity_type: str | None = None,
        entity_id: uuid.UUID | None = None,
        actor_id: uuid.UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        search: str | None = None,
    ) -> list[AuditEvent]:
        """
        Export all matching audit events without pagination.

        Used for CSV/JSON export. Returns all matching events so auditors can export
        complete audit trails.

        Args:
            event_type: Filter by event type
            entity_type: Filter by entity type
            entity_id: Filter by entity ID
            actor_id: Filter by actor ID
            date_from: Start date filter
            date_to: End date filter
            search: Search term

        Returns:
            List of all matching audit events
        """
        query = select(AuditEvent)
        conditions = []

        if event_type:
            conditions.append(AuditEvent.event_type == event_type)

        if entity_type:
            conditions.append(AuditEvent.entity_type == entity_type)

        if entity_id:
            conditions.append(AuditEvent.entity_id == entity_id)

        if actor_id:
            conditions.append(AuditEvent.actor_id == actor_id)

        if date_from:
            conditions.append(AuditEvent.created_at >= date_from)

        if date_to:
            end_of_day = date_to.replace(hour=23, minute=59, second=59, microsecond=999999)
            conditions.append(AuditEvent.created_at <= end_of_day)

        if search:
            search_pattern = f"%{search}%"
            conditions.append(
                or_(
                    AuditEvent.action.ilike(search_pattern),
                    AuditEvent.actor_email.ilike(search_pattern),
                )
            )

        if conditions:
            query = query.where(and_(*conditions))

        # Order by created_at ascending for logical export order
        query = query.order_by(AuditEvent.created_at.asc())

        result = await self.db.execute(query)
        return result.scalars().all()
