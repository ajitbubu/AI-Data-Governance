"""Approval workflow models for risk classification changes."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Text, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from .database import Base


class ApprovalWorkflow(Base):
    """Approval state machine: DRAFT → PENDING_REVIEW → APPROVED/REJECTED."""
    __tablename__ = "approval_workflows"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    system_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ai_systems.id"), nullable=False, index=True)

    # What triggered this workflow
    trigger_type: Mapped[str] = mapped_column(String(50), nullable=False)  # classification_change, new_system, manual_review
    trigger_detail: Mapped[dict | None] = mapped_column(JSONB)

    # Previous and proposed classification
    previous_eu_tier: Mapped[str | None] = mapped_column(String(50))
    proposed_eu_tier: Mapped[str | None] = mapped_column(String(50))
    previous_us_designation: Mapped[str | None] = mapped_column(String(50))
    proposed_us_designation: Mapped[str | None] = mapped_column(String(50))

    # State
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending_review")
    priority: Mapped[int] = mapped_column(Integer, default=1)  # 1=low, 2=medium, 3=high, 4=critical

    # SLA tracking
    sla_deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    escalated: Mapped[bool] = mapped_column(default=False)

    # Requestor
    requested_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    system = relationship("AISystem", back_populates="approval_workflows")
    actions: Mapped[list["ApprovalAction"]] = relationship(back_populates="workflow", order_by="ApprovalAction.created_at")


class ApprovalAction(Base):
    """Individual approval/rejection action within a workflow."""
    __tablename__ = "approval_actions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("approval_workflows.id"), nullable=False, index=True)

    action: Mapped[str] = mapped_column(String(50), nullable=False)  # approve, reject, comment, escalate
    comment: Mapped[str | None] = mapped_column(Text)
    acted_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    workflow: Mapped[ApprovalWorkflow] = relationship(back_populates="actions")
