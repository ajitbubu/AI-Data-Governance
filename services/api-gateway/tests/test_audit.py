"""Unit tests for Audit Trail & Observability (UC-4)."""
import sys
import os
import uuid
import json
from datetime import datetime, timezone
import importlib

# Insert the api-gateway root so we can import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Directly import the audit schemas module
_spec = importlib.util.spec_from_file_location(
    "audit_schemas",
    os.path.join(os.path.dirname(__file__), "..", "app", "schemas", "audit.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

AuditEventResponse = _mod.AuditEventResponse
AuditEventListItem = _mod.AuditEventListItem
AuditTimelineItem = _mod.AuditTimelineItem
AuditStatsResponse = _mod.AuditStatsResponse
AuditExportRequest = _mod.AuditExportRequest


# ── Test Data Fixtures ──


def create_test_event_data():
    """Create sample audit event data."""
    return {
        "id": uuid.uuid4(),
        "event_type": "SYSTEM_REGISTERED",
        "entity_type": "ai_system",
        "entity_id": uuid.uuid4(),
        "actor_id": uuid.uuid4(),
        "actor_email": "user@example.com",
        "action": "create",
        "changes": None,
        "metadata": {
            "system_name": "Credit Scoring Model",
            "eu_risk_tier": "high",
            "us_designation": "high_impact",
        },
        "ip_address": "192.168.1.1",
        "request_id": "req-12345-abcde",
        "created_at": datetime.now(timezone.utc),
    }


# ── Tests for AuditEventResponse ──


class TestAuditEventResponse:
    """Test full audit event response schema."""

    def test_event_response_creation(self):
        """AuditEventResponse should accept all event fields."""
        data = create_test_event_data()
        event = AuditEventResponse(**data)

        assert event.id == data["id"]
        assert event.event_type == "SYSTEM_REGISTERED"
        assert event.entity_type == "ai_system"
        assert event.action == "create"
        assert event.actor_email == "user@example.com"
        assert event.metadata["eu_risk_tier"] == "high"

    def test_event_response_with_changes(self):
        """AuditEventResponse should capture before/after changes."""
        data = create_test_event_data()
        data["event_type"] = "SYSTEM_UPDATED"
        data["action"] = "update"
        data["changes"] = {
            "before": {
                "eu_risk_tier": "limited",
                "us_designation": "standard",
            },
            "after": {
                "eu_risk_tier": "high",
                "us_designation": "high_impact",
            },
        }

        event = AuditEventResponse(**data)
        assert event.changes["before"]["eu_risk_tier"] == "limited"
        assert event.changes["after"]["eu_risk_tier"] == "high"

    def test_event_response_optional_fields(self):
        """AuditEventResponse should handle optional actor and changes fields."""
        data = create_test_event_data()
        data["actor_id"] = None
        data["actor_email"] = None
        data["changes"] = None

        event = AuditEventResponse(**data)
        assert event.actor_id is None
        assert event.actor_email is None
        assert event.changes is None


# ── Tests for AuditEventListItem ──


class TestAuditEventListItem:
    """Test compact list item schema."""

    def test_list_item_creation(self):
        """AuditEventListItem should be creatable from event data."""
        data = create_test_event_data()
        item = AuditEventListItem(
            id=data["id"],
            event_type=data["event_type"],
            entity_type=data["entity_type"],
            entity_id=data["entity_id"],
            action=data["action"],
            actor_email=data["actor_email"],
            created_at=data["created_at"],
            summary="SYSTEM_REGISTERED: ai_system created",
        )

        assert item.event_type == "SYSTEM_REGISTERED"
        assert item.summary is not None

    def test_list_item_reduced_payload(self):
        """AuditEventListItem should omit detailed fields like changes and metadata."""
        data = create_test_event_data()
        item = AuditEventListItem(
            id=data["id"],
            event_type=data["event_type"],
            entity_type=data["entity_type"],
            entity_id=data["entity_id"],
            action=data["action"],
            actor_email=data["actor_email"],
            created_at=data["created_at"],
            summary="Test summary",
        )

        # Verify it doesn't have detailed fields
        assert not hasattr(item, "changes") or not item.__dict__.get("changes")
        assert not hasattr(item, "metadata") or not item.__dict__.get("metadata")


# ── Tests for AuditTimelineItem ──


class TestAuditTimelineItem:
    """Test timeline item schema."""

    def test_timeline_item_creation(self):
        """AuditTimelineItem should be creatable for timeline views."""
        data = create_test_event_data()
        item = AuditTimelineItem(
            id=data["id"],
            event_type=data["event_type"],
            action=data["action"],
            changes_summary="System registered with high risk tier",
            actor_email=data["actor_email"],
            created_at=data["created_at"],
            metadata=data["metadata"],
        )

        assert item.event_type == "SYSTEM_REGISTERED"
        assert item.changes_summary is not None

    def test_timeline_item_with_changes_summary(self):
        """AuditTimelineItem should include human-readable change summary."""
        data = create_test_event_data()
        data["event_type"] = "CLASSIFICATION_COMPLETED"
        summary = "eu_risk_tier: limited → high; us_designation: standard → high_impact"

        item = AuditTimelineItem(
            id=data["id"],
            event_type=data["event_type"],
            action=data["action"],
            changes_summary=summary,
            actor_email=data["actor_email"],
            created_at=data["created_at"],
            metadata=data["metadata"],
        )

        assert "limited → high" in item.changes_summary


# ── Tests for AuditStatsResponse ──


class TestAuditStatsResponse:
    """Test aggregated audit statistics schema."""

    def test_stats_response_creation(self):
        """AuditStatsResponse should aggregate event counts."""
        stats = AuditStatsResponse(
            total_events=1000,
            by_event_type={
                "SYSTEM_REGISTERED": 100,
                "CLASSIFICATION_COMPLETED": 250,
                "SYSTEM_UPDATED": 400,
                "APPROVAL_CREATED": 150,
            },
            by_entity_type={
                "ai_system": 750,
                "approval": 250,
            },
            events_per_day=[
                {"date": "2026-03-15", "count": 10},
                {"date": "2026-03-16", "count": 15},
                {"date": "2026-03-17", "count": 20},
            ],
        )

        assert stats.total_events == 1000
        assert len(stats.by_event_type) == 4
        assert stats.by_event_type["SYSTEM_REGISTERED"] == 100
        assert len(stats.events_per_day) == 3

    def test_stats_empty_values(self):
        """AuditStatsResponse should handle empty statistics."""
        stats = AuditStatsResponse(
            total_events=0,
            by_event_type={},
            by_entity_type={},
            events_per_day=[],
        )

        assert stats.total_events == 0
        assert len(stats.by_event_type) == 0


# ── Tests for Event Type Classification ──


class TestEventTypeClassification:
    """Test audit event type categorization."""

    def test_system_registered_event(self):
        """SYSTEM_REGISTERED event should capture registration metadata."""
        data = create_test_event_data()
        data["event_type"] = "SYSTEM_REGISTERED"
        data["action"] = "create"

        event = AuditEventResponse(**data)
        assert event.event_type == "SYSTEM_REGISTERED"
        assert event.action == "create"
        assert event.metadata["system_name"] == "Credit Scoring Model"

    def test_classification_completed_event(self):
        """CLASSIFICATION_COMPLETED event should have before/after changes."""
        data = create_test_event_data()
        data["event_type"] = "CLASSIFICATION_COMPLETED"
        data["action"] = "classify"
        data["changes"] = {
            "before": {
                "eu_risk_tier": "limited",
                "us_designation": "standard",
            },
            "after": {
                "eu_risk_tier": "high",
                "us_designation": "high_impact",
            },
        }

        event = AuditEventResponse(**data)
        assert event.event_type == "CLASSIFICATION_COMPLETED"
        assert event.changes["before"]["eu_risk_tier"] == "limited"
        assert event.changes["after"]["eu_risk_tier"] == "high"

    def test_system_updated_event(self):
        """SYSTEM_UPDATED event should track metadata changes."""
        data = create_test_event_data()
        data["event_type"] = "SYSTEM_UPDATED"
        data["action"] = "update"
        data["changes"] = {
            "before": {
                "name": "Old Name",
                "purpose_statement": "Old purpose",
            },
            "after": {
                "name": "New Name",
                "purpose_statement": "New purpose",
            },
        }
        data["metadata"] = {
            "fields_changed": ["name", "purpose_statement"],
        }

        event = AuditEventResponse(**data)
        assert event.event_type == "SYSTEM_UPDATED"
        assert event.changes["before"]["name"] == "Old Name"
        assert "name" in event.metadata["fields_changed"]

    def test_system_archived_event(self):
        """SYSTEM_ARCHIVED event should represent soft delete."""
        data = create_test_event_data()
        data["event_type"] = "SYSTEM_ARCHIVED"
        data["action"] = "delete"
        data["metadata"] = {
            "action_type": "soft_delete",
            "new_status": "archived",
        }

        event = AuditEventResponse(**data)
        assert event.event_type == "SYSTEM_ARCHIVED"
        assert event.action == "delete"
        assert event.metadata["new_status"] == "archived"

    def test_approval_created_event(self):
        """APPROVAL_CREATED event should capture approval workflow details."""
        data = create_test_event_data()
        data["event_type"] = "APPROVAL_CREATED"
        data["entity_type"] = "approval"
        data["entity_id"] = uuid.uuid4()
        data["action"] = "create"
        data["metadata"] = {
            "trigger_type": "new_system",
            "system_id": str(uuid.uuid4()),
            "eu_tier": "high",
            "us_designation": "high_impact",
            "priority": 3,
        }

        event = AuditEventResponse(**data)
        assert event.event_type == "APPROVAL_CREATED"
        assert event.entity_type == "approval"
        assert event.metadata["trigger_type"] == "new_system"

    def test_approval_approved_event(self):
        """APPROVAL_APPROVED event should track approval decision."""
        data = create_test_event_data()
        data["event_type"] = "APPROVAL_APPROVED"
        data["entity_type"] = "approval"
        data["entity_id"] = uuid.uuid4()
        data["action"] = "approve"
        data["metadata"] = {
            "approved_by": str(uuid.uuid4()),
            "system_id": str(uuid.uuid4()),
            "decision_rationale": "Meets compliance requirements",
        }

        event = AuditEventResponse(**data)
        assert event.event_type == "APPROVAL_APPROVED"
        assert "approved_by" in event.metadata


# ── Tests for Changes Structure ──


class TestChangesStructure:
    """Test before/after change tracking."""

    def test_changes_with_before_after(self):
        """Changes should follow {before: {}, after: {}} structure."""
        data = create_test_event_data()
        data["changes"] = {
            "before": {
                "field_1": "value_1_old",
                "field_2": "value_2_old",
            },
            "after": {
                "field_1": "value_1_new",
                "field_2": "value_2_new",
            },
        }

        event = AuditEventResponse(**data)
        assert "before" in event.changes
        assert "after" in event.changes
        assert event.changes["before"]["field_1"] == "value_1_old"
        assert event.changes["after"]["field_1"] == "value_1_new"

    def test_changes_can_be_null(self):
        """Changes should be nullable for non-update events."""
        data = create_test_event_data()
        data["event_type"] = "SYSTEM_REGISTERED"
        data["changes"] = None

        event = AuditEventResponse(**data)
        assert event.changes is None

    def test_changes_with_nested_objects(self):
        """Changes should support nested object comparisons."""
        data = create_test_event_data()
        data["changes"] = {
            "before": {
                "classification_rationale": {
                    "eu": "High risk - Annex III Category 4",
                    "us": "Standard impact",
                },
            },
            "after": {
                "classification_rationale": {
                    "eu": "Prohibited - Social scoring",
                    "us": "High impact",
                },
            },
        }

        event = AuditEventResponse(**data)
        assert event.changes["before"]["classification_rationale"]["eu"] is not None
        assert event.changes["after"]["classification_rationale"]["us"] is not None


# ── Tests for Metadata ──


class TestMetadata:
    """Test event-specific metadata."""

    def test_metadata_structure(self):
        """Metadata should be flexible key-value pairs."""
        data = create_test_event_data()
        data["metadata"] = {
            "key_1": "value_1",
            "key_2": 42,
            "key_3": ["list", "of", "values"],
            "key_4": {"nested": "object"},
        }

        event = AuditEventResponse(**data)
        assert event.metadata["key_1"] == "value_1"
        assert event.metadata["key_2"] == 42
        assert "list" in event.metadata["key_3"]
        assert event.metadata["key_4"]["nested"] == "object"

    def test_metadata_can_be_null(self):
        """Metadata should be nullable."""
        data = create_test_event_data()
        data["metadata"] = None

        event = AuditEventResponse(**data)
        assert event.metadata is None


# ── Tests for Export Request ──


class TestAuditExportRequest:
    """Test export filter schema."""

    def test_export_request_with_all_filters(self):
        """AuditExportRequest should support all filter combinations."""
        now = datetime.now(timezone.utc)
        req = AuditExportRequest(
            event_type="SYSTEM_REGISTERED",
            entity_type="ai_system",
            entity_id=uuid.uuid4(),
            actor_id=uuid.uuid4(),
            date_from=now,
            date_to=now,
            search="credit",
        )

        assert req.event_type == "SYSTEM_REGISTERED"
        assert req.entity_type == "ai_system"
        assert req.search == "credit"

    def test_export_request_empty_filters(self):
        """AuditExportRequest should allow empty filters (export all)."""
        req = AuditExportRequest()

        assert req.event_type is None
        assert req.entity_type is None
        assert req.search is None


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
