"""Business logic orchestrator for AI System Inventory (UC-1)."""
import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from ..repositories.ai_system_repo import AISystemRepository
from ..models.ai_system import RiskClassification
from ..models.approval import ApprovalWorkflow
from ..schemas.ai_system import AISystemCreate, AISystemUpdate
from .classification_service import ClassificationService
from .audit_service import AuditService


class InventoryService:
    def __init__(self, db: AsyncSession):
        self.repo = AISystemRepository(db)
        self.classifier = ClassificationService()
        self.db = db
        self.audit = AuditService(db)

    async def register_system(self, data: AISystemCreate, created_by: uuid.UUID | None = None):
        """Register a new AI system with automatic classification."""
        # 1. Create the system
        system = await self.repo.create(data, created_by=created_by)

        # 2. Run classification
        result = self.classifier.classify(
            purpose_statement=system.purpose_statement,
            sector=system.sector,
            decision_automation=system.decision_automation,
            deployment_geo=system.deployment_geo,
            data_sensitivity=system.data_sensitivity,
            affected_population=system.affected_population,
            model_type=system.model_type,
        )

        # 3. Update system with classification
        system.eu_risk_tier = result.eu_risk_tier
        system.us_designation = result.us_designation
        system.risk_score = result.risk_score
        system.classification_confidence = result.confidence
        system.classification_rationale = {
            "eu": result.eu_rationale,
            "us": result.us_rationale,
        }
        await self.db.commit()
        await self.db.refresh(system)

        # 4. Save classification record
        classification = RiskClassification(
            system_id=system.id,
            eu_risk_tier=result.eu_risk_tier,
            us_designation=result.us_designation,
            risk_score=result.risk_score,
            confidence=result.confidence,
            eu_rationale=result.eu_rationale,
            us_rationale=result.us_rationale,
            matched_annex_iii_categories=result.matched_annex_iii_categories,
            matched_omb_categories=result.matched_omb_categories,
            classified_by="system",
        )
        await self.repo.save_classification(classification)

        # 5. Create initial version snapshot
        await self.repo.create_version(system, change_summary="Initial registration", changed_by=created_by)

        # 6. Emit audit event for system registration
        await self.audit.emit(
            event_type="SYSTEM_REGISTERED",
            entity_type="ai_system",
            entity_id=system.id,
            action="create",
            metadata={
                "system_name": system.name,
                "eu_risk_tier": result.eu_risk_tier,
                "us_designation": result.us_designation,
                "risk_score": result.risk_score,
                "confidence": result.confidence,
            },
        )

        # 7. If high-risk or prohibited, create approval workflow
        if result.eu_risk_tier in ("high", "prohibited") or result.us_designation == "high_impact":
            priority = 4 if result.eu_risk_tier == "prohibited" else 3
            workflow = ApprovalWorkflow(
                system_id=system.id,
                trigger_type="new_system",
                trigger_detail={"eu_tier": result.eu_risk_tier, "us_designation": result.us_designation},
                proposed_eu_tier=result.eu_risk_tier,
                proposed_us_designation=result.us_designation,
                status="pending_review",
                priority=priority,
                sla_deadline=datetime.now(timezone.utc) + timedelta(hours=48),
                requested_by=created_by,
            )
            self.db.add(workflow)
            await self.db.commit()

            # Emit audit event for approval creation
            await self.audit.emit(
                event_type="APPROVAL_CREATED",
                entity_type="approval",
                entity_id=workflow.id,
                action="create",
                metadata={
                    "trigger_type": "new_system",
                    "system_id": str(system.id),
                    "eu_tier": result.eu_risk_tier,
                    "us_designation": result.us_designation,
                    "priority": priority,
                },
            )

        return system

    async def reclassify_system(self, system_id: uuid.UUID, triggered_by: uuid.UUID | None = None):
        """Re-run classification for an existing system (e.g., after metadata update)."""
        system = await self.repo.get_by_id(system_id)
        if not system:
            return None

        previous_eu = system.eu_risk_tier
        previous_us = system.us_designation

        result = self.classifier.classify(
            purpose_statement=system.purpose_statement,
            sector=system.sector,
            decision_automation=system.decision_automation,
            deployment_geo=system.deployment_geo,
            data_sensitivity=system.data_sensitivity,
            affected_population=system.affected_population,
            model_type=system.model_type,
        )

        # Update system
        system.eu_risk_tier = result.eu_risk_tier
        system.us_designation = result.us_designation
        system.risk_score = result.risk_score
        system.classification_confidence = result.confidence
        system.classification_rationale = {"eu": result.eu_rationale, "us": result.us_rationale}
        await self.db.commit()
        await self.db.refresh(system)

        # Save classification record
        classification = RiskClassification(
            system_id=system.id,
            eu_risk_tier=result.eu_risk_tier,
            us_designation=result.us_designation,
            risk_score=result.risk_score,
            confidence=result.confidence,
            eu_rationale=result.eu_rationale,
            us_rationale=result.us_rationale,
            matched_annex_iii_categories=result.matched_annex_iii_categories,
            matched_omb_categories=result.matched_omb_categories,
            classified_by="system",
        )
        await self.repo.save_classification(classification)

        # Emit audit event for classification completion
        await self.audit.emit(
            event_type="CLASSIFICATION_COMPLETED",
            entity_type="ai_system",
            entity_id=system.id,
            action="classify",
            changes={
                "before": {
                    "eu_risk_tier": previous_eu,
                    "us_designation": previous_us,
                },
                "after": {
                    "eu_risk_tier": result.eu_risk_tier,
                    "us_designation": result.us_designation,
                },
            },
            metadata={
                "risk_score": result.risk_score,
                "confidence": result.confidence,
            },
        )

        # If classification changed, trigger approval
        if result.eu_risk_tier != previous_eu or result.us_designation != previous_us:
            await self.repo.create_version(
                system,
                change_summary=f"Reclassification: EU {previous_eu}→{result.eu_risk_tier}, US {previous_us}→{result.us_designation}",
                changed_by=triggered_by,
            )

            # Risk escalation → approval needed
            eu_severity = {"minimal": 0, "limited": 1, "high": 2, "prohibited": 3, "not_classified": -1}
            if eu_severity.get(result.eu_risk_tier, 0) > eu_severity.get(previous_eu, 0):
                workflow = ApprovalWorkflow(
                    system_id=system.id,
                    trigger_type="classification_change",
                    trigger_detail={
                        "previous_eu": previous_eu,
                        "new_eu": result.eu_risk_tier,
                        "previous_us": previous_us,
                        "new_us": result.us_designation,
                    },
                    previous_eu_tier=previous_eu,
                    proposed_eu_tier=result.eu_risk_tier,
                    previous_us_designation=previous_us,
                    proposed_us_designation=result.us_designation,
                    status="pending_review",
                    priority=3,
                    sla_deadline=datetime.now(timezone.utc) + timedelta(hours=48),
                    requested_by=triggered_by,
                )
                self.db.add(workflow)
                await self.db.commit()

                # Emit audit event for approval creation
                await self.audit.emit(
                    event_type="APPROVAL_CREATED",
                    entity_type="approval",
                    entity_id=workflow.id,
                    action="create",
                    metadata={
                        "trigger_type": "classification_change",
                        "system_id": str(system.id),
                        "previous_eu": previous_eu,
                        "new_eu": result.eu_risk_tier,
                        "previous_us": previous_us,
                        "new_us": result.us_designation,
                    },
                )

        return system

    async def get_system(self, system_id: uuid.UUID):
        return await self.repo.get_by_id(system_id)

    async def list_systems(self, **kwargs):
        return await self.repo.list_systems(**kwargs)

    async def update_system(self, system_id: uuid.UUID, data: AISystemUpdate, updated_by: uuid.UUID | None = None):
        """Update system metadata with audit trail."""
        # Get current state for audit
        current = await self.repo.get_by_id(system_id)
        if not current:
            return None

        # Capture before state
        before = {
            "name": current.name,
            "description": current.description,
            "purpose_statement": current.purpose_statement,
            "model_type": current.model_type,
            "deployment_env": current.deployment_env,
            "sector": current.sector,
            "data_sensitivity": current.data_sensitivity,
        }

        # Apply update
        system = await self.repo.update(system_id, data)
        if system:
            # Capture after state
            after = {
                "name": system.name,
                "description": system.description,
                "purpose_statement": system.purpose_statement,
                "model_type": system.model_type,
                "deployment_env": system.deployment_env,
                "sector": system.sector,
                "data_sensitivity": system.data_sensitivity,
            }

            # Create version snapshot
            await self.repo.create_version(system, change_summary="Metadata updated", changed_by=updated_by)

            # Emit audit event with changes
            await self.audit.emit(
                event_type="SYSTEM_UPDATED",
                entity_type="ai_system",
                entity_id=system.id,
                action="update",
                changes={
                    "before": before,
                    "after": after,
                },
                metadata={
                    "system_name": system.name,
                    "fields_changed": list(data.model_dump(exclude_unset=True).keys()),
                },
            )

        return system

    async def delete_system(self, system_id: uuid.UUID):
        """Soft-delete (archive) a system with audit trail."""
        result = await self.repo.soft_delete(system_id)
        if result:
            # Emit audit event
            await self.audit.emit(
                event_type="SYSTEM_ARCHIVED",
                entity_type="ai_system",
                entity_id=system_id,
                action="delete",
                metadata={
                    "action_type": "soft_delete",
                    "new_status": "archived",
                },
            )
        return result

    async def get_versions(self, system_id: uuid.UUID):
        return await self.repo.get_versions(system_id)

    async def get_classification(self, system_id: uuid.UUID):
        return await self.repo.get_latest_classification(system_id)

    async def get_classification_history(self, system_id: uuid.UUID):
        return await self.repo.get_classification_history(system_id)

    async def get_stats(self):
        return await self.repo.get_stats()
