"""Pydantic schemas for AI System Inventory (UC-1)."""
import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# ── Create / Update ──

class AISystemCreate(BaseModel):
    """Schema for registering a new AI system."""
    name: str = Field(..., min_length=1, max_length=255, description="Human-readable system name")
    description: str | None = None
    version: str | None = None
    owner_id: uuid.UUID | None = None
    team_id: uuid.UUID | None = None
    purpose_statement: str = Field(..., min_length=10, description="Used by Annex III classifier for risk matching")
    model_type: str = Field(default="other")
    deployment_env: str = Field(default="development")
    deployment_geo: list[str] | None = None
    affected_population: str | None = None
    decision_automation: str = Field(default="advisory")
    sector: str = Field(default="other")
    data_sensitivity: str = Field(default="internal")
    training_data_sources: dict | None = None
    upstream_dependencies: dict | None = None
    downstream_consumers: dict | None = None
    mlflow_model_id: str | None = None
    sagemaker_arn: str | None = None
    vertex_model_id: str | None = None
    huggingface_id: str | None = None
    metadata_extra: dict | None = None


class AISystemUpdate(BaseModel):
    """Schema for updating an existing AI system."""
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    version: str | None = None
    owner_id: uuid.UUID | None = None
    team_id: uuid.UUID | None = None
    purpose_statement: str | None = Field(None, min_length=10)
    model_type: str | None = None
    deployment_env: str | None = None
    deployment_geo: list[str] | None = None
    affected_population: str | None = None
    decision_automation: str | None = None
    sector: str | None = None
    data_sensitivity: str | None = None
    training_data_sources: dict | None = None
    upstream_dependencies: dict | None = None
    downstream_consumers: dict | None = None
    mlflow_model_id: str | None = None
    sagemaker_arn: str | None = None
    vertex_model_id: str | None = None
    huggingface_id: str | None = None
    status: str | None = None
    metadata_extra: dict | None = None


# ── Response ──

class RiskClassificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    system_id: uuid.UUID
    eu_risk_tier: str
    us_designation: str
    risk_score: float
    confidence: str
    eu_rationale: dict
    us_rationale: dict
    matched_annex_iii_categories: list | None = None
    matched_omb_categories: list | None = None
    rule_version: str | None = None
    classifier_version: str
    classified_at: datetime
    classified_by: str


class AISystemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None = None
    version: str | None = None
    owner_id: uuid.UUID | None = None
    team_id: uuid.UUID | None = None
    purpose_statement: str
    model_type: str
    deployment_env: str
    deployment_geo: list[str] | None = None
    affected_population: str | None = None
    decision_automation: str
    sector: str
    data_sensitivity: str
    training_data_sources: dict | None = None
    upstream_dependencies: dict | None = None
    downstream_consumers: dict | None = None
    mlflow_model_id: str | None = None
    sagemaker_arn: str | None = None
    vertex_model_id: str | None = None
    huggingface_id: str | None = None
    eu_risk_tier: str
    us_designation: str
    risk_score: float | None = None
    classification_confidence: str | None = None
    classification_rationale: dict | None = None
    status: str
    metadata_extra: dict | None = None
    created_at: datetime
    updated_at: datetime
    created_by: uuid.UUID | None = None


class AISystemVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    system_id: uuid.UUID
    version_number: int
    snapshot: dict
    change_summary: str | None = None
    changed_by: uuid.UUID | None = None
    created_at: datetime


class AISystemListItem(BaseModel):
    """Lightweight schema for list views."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    model_type: str
    deployment_env: str
    sector: str
    eu_risk_tier: str
    us_designation: str
    risk_score: float | None = None
    status: str
    owner_id: uuid.UUID | None = None
    team_id: uuid.UUID | None = None
    updated_at: datetime
