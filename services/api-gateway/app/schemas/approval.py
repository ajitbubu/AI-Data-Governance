"""Pydantic schemas for approval workflows."""
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ApprovalActionCreate(BaseModel):
    action: str  # approve, reject, comment, escalate
    comment: str | None = None


class ApprovalActionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workflow_id: uuid.UUID
    action: str
    comment: str | None = None
    acted_by: uuid.UUID
    created_at: datetime


class ApprovalWorkflowResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    system_id: uuid.UUID
    trigger_type: str
    trigger_detail: dict | None = None
    previous_eu_tier: str | None = None
    proposed_eu_tier: str | None = None
    previous_us_designation: str | None = None
    proposed_us_designation: str | None = None
    status: str
    priority: int
    sla_deadline: datetime | None = None
    escalated: bool
    requested_by: uuid.UUID | None = None
    created_at: datetime
    resolved_at: datetime | None = None
    actions: list[ApprovalActionResponse] = []
