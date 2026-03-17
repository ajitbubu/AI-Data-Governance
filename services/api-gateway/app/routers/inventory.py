"""
UC-1: AI System Inventory & Risk Classification — API Router.

Endpoints:
  POST   /systems              Register new AI system (auto-classifies)
  GET    /systems              List all systems (paginated, filterable)
  GET    /systems/stats        Aggregate statistics
  GET    /systems/export       CSV export
  GET    /systems/{id}         Get system detail
  PUT    /systems/{id}         Update system metadata
  DELETE /systems/{id}         Soft delete (archive)
  POST   /systems/{id}/classify   Re-trigger classification
  GET    /systems/{id}/classification   Get current classification
  GET    /systems/{id}/classification/history   Classification history
  GET    /systems/{id}/history     Version history
"""
import uuid
import csv
import io
from math import ceil
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.database import get_db
from ..services.inventory_service import InventoryService
from ..schemas.ai_system import (
    AISystemCreate, AISystemUpdate, AISystemResponse,
    AISystemListItem, AISystemVersionResponse, RiskClassificationResponse,
)
from ..schemas.common import PaginatedResponse, MessageResponse, StatsResponse

router = APIRouter(prefix="/systems", tags=["AI System Inventory"])


def get_service(db: AsyncSession = Depends(get_db)) -> InventoryService:
    return InventoryService(db)


# ── Registration ──

@router.post("", response_model=AISystemResponse, status_code=201)
async def register_system(
    data: AISystemCreate,
    service: InventoryService = Depends(get_service),
):
    """Register a new AI system. Automatically runs dual classification (EU + US)."""
    system = await service.register_system(data)
    return system


# ── List & Search ──

@router.get("", response_model=PaginatedResponse[AISystemListItem])
async def list_systems(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    eu_risk_tier: str | None = None,
    us_designation: str | None = None,
    sector: str | None = None,
    deployment_env: str | None = None,
    search: str | None = None,
    sort_by: str = "updated_at",
    sort_order: str = "desc",
    service: InventoryService = Depends(get_service),
):
    """List AI systems with filtering, search, and pagination."""
    items, total = await service.list_systems(
        page=page, page_size=page_size,
        status=status, eu_risk_tier=eu_risk_tier,
        us_designation=us_designation, sector=sector,
        deployment_env=deployment_env, search=search,
        sort_by=sort_by, sort_order=sort_order,
    )
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size) if total > 0 else 0,
    )


# ── Stats ──

@router.get("/stats", response_model=StatsResponse)
async def get_stats(service: InventoryService = Depends(get_service)):
    """Aggregate statistics for executive dashboard."""
    return await service.get_stats()


# ── Export ──

@router.get("/export")
async def export_systems(
    service: InventoryService = Depends(get_service),
):
    """Export all systems as CSV for auditors."""
    items, _ = await service.list_systems(page=1, page_size=10000)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Name", "Model Type", "Sector", "Deployment Env",
        "EU Risk Tier", "US Designation", "Risk Score", "Status", "Updated At"
    ])
    for item in items:
        writer.writerow([
            str(item.id), item.name, item.model_type, item.sector,
            item.deployment_env, item.eu_risk_tier, item.us_designation,
            item.risk_score, item.status, item.updated_at.isoformat(),
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ai_systems_export.csv"},
    )


# ── Detail ──

@router.get("/{system_id}", response_model=AISystemResponse)
async def get_system(
    system_id: uuid.UUID,
    service: InventoryService = Depends(get_service),
):
    """Get full detail for a single AI system."""
    system = await service.get_system(system_id)
    if not system:
        raise HTTPException(status_code=404, detail="AI system not found")
    return system


# ── Update ──

@router.put("/{system_id}", response_model=AISystemResponse)
async def update_system(
    system_id: uuid.UUID,
    data: AISystemUpdate,
    service: InventoryService = Depends(get_service),
):
    """Update system metadata. Creates a version snapshot."""
    system = await service.update_system(system_id, data)
    if not system:
        raise HTTPException(status_code=404, detail="AI system not found")
    return system


# ── Delete ──

@router.delete("/{system_id}", response_model=MessageResponse)
async def delete_system(
    system_id: uuid.UUID,
    service: InventoryService = Depends(get_service),
):
    """Soft delete (archive) an AI system."""
    success = await service.delete_system(system_id)
    if not success:
        raise HTTPException(status_code=404, detail="AI system not found")
    return MessageResponse(message="System archived successfully")


# ── Classification ──

@router.post("/{system_id}/classify", response_model=AISystemResponse)
async def classify_system(
    system_id: uuid.UUID,
    service: InventoryService = Depends(get_service),
):
    """Re-trigger risk classification for a system."""
    system = await service.reclassify_system(system_id)
    if not system:
        raise HTTPException(status_code=404, detail="AI system not found")
    return system


@router.get("/{system_id}/classification", response_model=RiskClassificationResponse | None)
async def get_classification(
    system_id: uuid.UUID,
    service: InventoryService = Depends(get_service),
):
    """Get the latest classification result for a system."""
    return await service.get_classification(system_id)


@router.get("/{system_id}/classification/history", response_model=list[RiskClassificationResponse])
async def get_classification_history(
    system_id: uuid.UUID,
    service: InventoryService = Depends(get_service),
):
    """Get full classification history for audit trail."""
    return await service.get_classification_history(system_id)


# ── Version History ──

@router.get("/{system_id}/history", response_model=list[AISystemVersionResponse])
async def get_system_history(
    system_id: uuid.UUID,
    service: InventoryService = Depends(get_service),
):
    """Get version history (snapshots) for a system."""
    return await service.get_versions(system_id)
