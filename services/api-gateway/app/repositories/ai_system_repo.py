"""Data access layer for AI System Inventory."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import select, func, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.ai_system import AISystem, AISystemVersion, RiskClassification
from ..models.approval import ApprovalWorkflow
from ..schemas.ai_system import AISystemCreate, AISystemUpdate


class AISystemRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── CRUD ──

    async def create(self, data: AISystemCreate, created_by: uuid.UUID | None = None) -> AISystem:
        system = AISystem(
            **data.model_dump(exclude_unset=True),
            created_by=created_by,
        )
        self.db.add(system)
        await self.db.commit()
        await self.db.refresh(system)
        return system

    async def get_by_id(self, system_id: uuid.UUID) -> AISystem | None:
        result = await self.db.execute(
            select(AISystem).where(AISystem.id == system_id)
        )
        return result.scalar_one_or_none()

    async def list_systems(
        self,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        eu_risk_tier: str | None = None,
        us_designation: str | None = None,
        sector: str | None = None,
        deployment_env: str | None = None,
        search: str | None = None,
        sort_by: str = "updated_at",
        sort_order: str = "desc",
    ) -> tuple[list[AISystem], int]:
        query = select(AISystem)
        count_query = select(func.count(AISystem.id))

        # Filters
        conditions = []
        if status:
            conditions.append(AISystem.status == status)
        if eu_risk_tier:
            conditions.append(AISystem.eu_risk_tier == eu_risk_tier)
        if us_designation:
            conditions.append(AISystem.us_designation == us_designation)
        if sector:
            conditions.append(AISystem.sector == sector)
        if deployment_env:
            conditions.append(AISystem.deployment_env == deployment_env)
        if search:
            conditions.append(
                AISystem.name.ilike(f"%{search}%") | AISystem.description.ilike(f"%{search}%")
            )

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        # Count
        total = (await self.db.execute(count_query)).scalar() or 0

        # Sort
        sort_col = getattr(AISystem, sort_by, AISystem.updated_at)
        if sort_order == "desc":
            query = query.order_by(desc(sort_col))
        else:
            query = query.order_by(sort_col)

        # Paginate
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def update(self, system_id: uuid.UUID, data: AISystemUpdate) -> AISystem | None:
        system = await self.get_by_id(system_id)
        if not system:
            return None

        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        for field, value in update_data.items():
            setattr(system, field, value)

        system.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(system)
        return system

    async def soft_delete(self, system_id: uuid.UUID) -> bool:
        system = await self.get_by_id(system_id)
        if not system:
            return False
        system.status = "archived"
        system.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        return True

    # ── Versioning ──

    async def create_version(self, system: AISystem, change_summary: str | None = None, changed_by: uuid.UUID | None = None) -> AISystemVersion:
        # Get next version number
        result = await self.db.execute(
            select(func.max(AISystemVersion.version_number))
            .where(AISystemVersion.system_id == system.id)
        )
        max_version = result.scalar() or 0

        snapshot = {
            "name": system.name,
            "description": system.description,
            "purpose_statement": system.purpose_statement,
            "model_type": system.model_type,
            "deployment_env": system.deployment_env,
            "sector": system.sector,
            "eu_risk_tier": system.eu_risk_tier,
            "us_designation": system.us_designation,
            "risk_score": system.risk_score,
            "status": system.status,
        }

        version = AISystemVersion(
            system_id=system.id,
            version_number=max_version + 1,
            snapshot=snapshot,
            change_summary=change_summary,
            changed_by=changed_by,
        )
        self.db.add(version)
        await self.db.commit()
        await self.db.refresh(version)
        return version

    async def get_versions(self, system_id: uuid.UUID) -> list[AISystemVersion]:
        result = await self.db.execute(
            select(AISystemVersion)
            .where(AISystemVersion.system_id == system_id)
            .order_by(desc(AISystemVersion.version_number))
        )
        return result.scalars().all()

    # ── Classification ──

    async def save_classification(self, classification: RiskClassification) -> RiskClassification:
        self.db.add(classification)
        await self.db.commit()
        await self.db.refresh(classification)
        return classification

    async def get_latest_classification(self, system_id: uuid.UUID) -> RiskClassification | None:
        result = await self.db.execute(
            select(RiskClassification)
            .where(RiskClassification.system_id == system_id)
            .order_by(desc(RiskClassification.classified_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_classification_history(self, system_id: uuid.UUID) -> list[RiskClassification]:
        result = await self.db.execute(
            select(RiskClassification)
            .where(RiskClassification.system_id == system_id)
            .order_by(desc(RiskClassification.classified_at))
        )
        return result.scalars().all()

    # ── Stats ──

    async def get_stats(self) -> dict:
        total = (await self.db.execute(select(func.count(AISystem.id)))).scalar() or 0

        # By EU tier
        eu_result = await self.db.execute(
            select(AISystem.eu_risk_tier, func.count(AISystem.id))
            .group_by(AISystem.eu_risk_tier)
        )
        by_eu_tier = dict(eu_result.all())

        # By US designation
        us_result = await self.db.execute(
            select(AISystem.us_designation, func.count(AISystem.id))
            .group_by(AISystem.us_designation)
        )
        by_us_designation = dict(us_result.all())

        # By status
        status_result = await self.db.execute(
            select(AISystem.status, func.count(AISystem.id))
            .group_by(AISystem.status)
        )
        by_status = dict(status_result.all())

        # By sector
        sector_result = await self.db.execute(
            select(AISystem.sector, func.count(AISystem.id))
            .group_by(AISystem.sector)
        )
        by_sector = dict(sector_result.all())

        # Pending approvals
        pending = (await self.db.execute(
            select(func.count(ApprovalWorkflow.id))
            .where(ApprovalWorkflow.status == "pending_review")
        )).scalar() or 0

        return {
            "total_systems": total,
            "by_eu_tier": by_eu_tier,
            "by_us_designation": by_us_designation,
            "by_status": by_status,
            "by_sector": by_sector,
            "pending_approvals": pending,
        }
