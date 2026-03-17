"""AI System Inventory ORM models — the core of UC-1."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    String, DateTime, Text, Numeric, ForeignKey, Integer, Float, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from .database import Base


class AISystem(Base):
    """Central AI system registry — 25+ metadata fields per system."""
    __tablename__ = "ai_systems"
    __table_args__ = (
        Index("ix_ai_systems_eu_risk_tier", "eu_risk_tier"),
        Index("ix_ai_systems_us_designation", "us_designation"),
        Index("ix_ai_systems_status", "status"),
        Index("ix_ai_systems_sector", "sector"),
        Index("ix_ai_systems_team_id", "team_id"),
    )

    # Identity
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    version: Mapped[str | None] = mapped_column(String(50))

    # Ownership
    owner_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    team_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("teams.id"))

    # Purpose & Impact — used by Annex III matcher
    purpose_statement: Mapped[str] = mapped_column(Text, nullable=False)
    model_type: Mapped[str] = mapped_column(String(50), nullable=False, default="other")
    deployment_env: Mapped[str] = mapped_column(String(50), nullable=False, default="development")
    deployment_geo: Mapped[list[str] | None] = mapped_column(ARRAY(String(50)))
    affected_population: Mapped[str | None] = mapped_column(Text)
    decision_automation: Mapped[str] = mapped_column(String(50), nullable=False, default="advisory")
    sector: Mapped[str] = mapped_column(String(50), nullable=False, default="other")
    data_sensitivity: Mapped[str] = mapped_column(String(50), nullable=False, default="internal")

    # Data & Dependencies
    training_data_sources: Mapped[dict | None] = mapped_column(JSONB)
    upstream_dependencies: Mapped[dict | None] = mapped_column(JSONB)
    downstream_consumers: Mapped[dict | None] = mapped_column(JSONB)

    # External registry links
    mlflow_model_id: Mapped[str | None] = mapped_column(String(255))
    sagemaker_arn: Mapped[str | None] = mapped_column(String(500))
    vertex_model_id: Mapped[str | None] = mapped_column(String(255))
    huggingface_id: Mapped[str | None] = mapped_column(String(255))

    # Risk Classification (dual: EU + US)
    eu_risk_tier: Mapped[str] = mapped_column(String(50), nullable=False, default="not_classified")
    us_designation: Mapped[str] = mapped_column(String(50), nullable=False, default="not_classified")
    risk_score: Mapped[float | None] = mapped_column(Float)
    classification_confidence: Mapped[str | None] = mapped_column(String(20))
    classification_rationale: Mapped[dict | None] = mapped_column(JSONB)

    # Status
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")

    # Extensible metadata
    metadata_extra: Mapped[dict | None] = mapped_column(JSONB)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    versions: Mapped[list["AISystemVersion"]] = relationship(back_populates="system", order_by="desc(AISystemVersion.version_number)")
    classifications: Mapped[list["RiskClassification"]] = relationship(back_populates="system", order_by="desc(RiskClassification.classified_at)")
    approval_workflows: Mapped[list["ApprovalWorkflow"]] = relationship("ApprovalWorkflow", back_populates="system")


class AISystemVersion(Base):
    """Immutable snapshot of AI system state for audit trail."""
    __tablename__ = "ai_system_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    system_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ai_systems.id"), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    change_summary: Mapped[str | None] = mapped_column(Text)
    changed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    system: Mapped[AISystem] = relationship(back_populates="versions")


class RiskClassification(Base):
    """Classification result — one per classification run."""
    __tablename__ = "risk_classifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    system_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ai_systems.id"), nullable=False, index=True)

    # Results
    eu_risk_tier: Mapped[str] = mapped_column(String(50), nullable=False)
    us_designation: Mapped[str] = mapped_column(String(50), nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[str] = mapped_column(String(20), nullable=False)

    # Rationale — structured explanation
    eu_rationale: Mapped[dict] = mapped_column(JSONB, nullable=False)
    us_rationale: Mapped[dict] = mapped_column(JSONB, nullable=False)
    matched_annex_iii_categories: Mapped[list | None] = mapped_column(JSONB)
    matched_omb_categories: Mapped[list | None] = mapped_column(JSONB)

    # Rule metadata
    rule_version: Mapped[str | None] = mapped_column(String(50))
    classifier_version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0.0")

    classified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    classified_by: Mapped[str] = mapped_column(String(50), nullable=False, default="system")

    system: Mapped[AISystem] = relationship(back_populates="classifications")


class ClassificationRule(Base):
    """Versioned classification rules (YAML/JSON) — configurable by admins."""
    __tablename__ = "classification_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)  # eu_annex_iii, us_omb, custom
    rule_definition: Mapped[dict] = mapped_column(JSONB, nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
