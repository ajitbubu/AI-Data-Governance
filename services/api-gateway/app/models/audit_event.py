"""
Immutable audit event model for compliance and forensics.

Provides append-only audit trail with no update/delete operations.
All changes to AI systems and compliance workflows are recorded here.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Text, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from .database import Base


class AuditEvent(Base):
    """
    Immutable audit event record — append-only compliance trail.

    Records all significant actions in the system including system registration,
    updates, classifications, approvals, and policy enforcement.
    """

    __tablename__ = "audit_events"
    __table_args__ = (
        Index("ix_audit_events_entity_type_id", "entity_type", "entity_id"),
        Index("ix_audit_events_event_type", "event_type"),
        Index("ix_audit_events_created_at", "created_at"),
        Index("ix_audit_events_actor_id", "actor_id"),
    )

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Event classification
    event_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )
    """
    Event type codes, e.g.:
    - SYSTEM_REGISTERED: AI system added to inventory
    - SYSTEM_UPDATED: AI system metadata changed
    - SYSTEM_ARCHIVED: AI system archived/deleted
    - CLASSIFICATION_COMPLETED: Risk classification completed
    - APPROVAL_CREATED: Approval workflow initiated
    - APPROVAL_APPROVED: Approval granted
    - APPROVAL_REJECTED: Approval denied
    - POLICY_ENFORCED: Policy rule applied
    - RISK_ALERT_TRIGGERED: Risk threshold breached
    """

    # Entity reference
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    """Type of entity affected: ai_system, approval, policy_rule, etc."""

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    """UUID of the affected entity"""

    # Actor (who performed the action)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    """User who performed the action (null for system-triggered events)"""

    actor_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    """Email of actor at time of action (denormalized for compliance reports)"""

    # Action details
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    """Specific action performed: create, read, update, delete, classify, approve, etc."""

    changes: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    """
    JSON diff of what changed. Format:
    {
        "before": {field: old_value, ...},
        "after": {field: new_value, ...}
    }
    Null for non-update events.
    """

    metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    """
    Event-specific metadata. Examples:
    - CLASSIFICATION_COMPLETED: {confidence: 0.95, rule_version: "1.0"}
    - APPROVAL_CREATED: {tier: "high_risk", required_roles: [...]}
    - SYSTEM_UPDATED: {fields_changed: [...]}
    """

    # Request context (for distributed tracing)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    """Client IP address (IPv4 or IPv6)"""

    request_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    """Correlation ID for distributed tracing"""

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    """When the event was recorded (server time, UTC)"""

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<AuditEvent(id={self.id!r}, event_type={self.event_type!r}, "
            f"entity_type={self.entity_type!r}, entity_id={self.entity_id!r})>"
        )
