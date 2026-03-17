"""
Audit service for compliance trail emission.

Provides async audit event recording with automatic context capture
(request ID, actor information) for governance and forensics.
"""
import uuid
from typing import Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from ..models.audit_event import AuditEvent
from ..middleware import get_request_id, get_user_id, get_user_email
from ..models.database import AsyncSessionLocal

logger = structlog.get_logger(__name__)


class AuditService:
    """Service for emitting and persisting audit events."""

    def __init__(self, db_session: AsyncSession):
        """
        Initialize audit service.

        Args:
            db_session: SQLAlchemy async session for database operations
        """
        self.db = db_session

    async def emit(
        self,
        event_type: str,
        entity_type: str,
        entity_id: uuid.UUID,
        action: str,
        changes: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, Any]] = None,
        ip_address: str = "0.0.0.0",
    ) -> AuditEvent:
        """
        Emit an audit event to the trail.

        Automatically captures request context (request_id, actor) from contextvars.

        Args:
            event_type: Classification of event (e.g., SYSTEM_REGISTERED)
            entity_type: Type of entity affected (e.g., ai_system)
            entity_id: UUID of affected entity
            action: Specific action (e.g., create, update, classify)
            changes: Optional JSON diff of changes
            metadata: Optional event-specific metadata
            ip_address: Client IP address

        Returns:
            Persisted AuditEvent object
        """
        # Auto-capture context
        request_id = get_request_id()
        actor_id = None
        actor_email = None

        user_id = get_user_id()
        user_email = get_user_email()

        if user_id:
            actor_id = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        if user_email:
            actor_email = user_email

        # Create audit event
        event = AuditEvent(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            actor_id=actor_id,
            actor_email=actor_email,
            action=action,
            changes=changes,
            metadata=metadata,
            ip_address=ip_address,
            request_id=request_id,
        )

        # Persist to database
        self.db.add(event)
        await self.db.flush()

        # Log emission
        logger.info(
            "audit_event_emitted",
            event_id=event.id,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            actor_id=actor_id,
            action=action,
            request_id=request_id,
        )

        return event


async def get_audit_service(
    db_session: AsyncSession = None,
) -> AuditService:
    """
    Dependency to get audit service instance.

    If no session provided, creates a new one.

    Args:
        db_session: Optional existing database session

    Returns:
        AuditService instance
    """
    if db_session is None:
        db_session = AsyncSessionLocal()

    return AuditService(db_session)
