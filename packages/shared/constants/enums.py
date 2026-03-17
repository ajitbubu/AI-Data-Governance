"""Shared enums used across all DataSafeguard services."""
from enum import Enum


class EURiskTier(str, Enum):
    PROHIBITED = "prohibited"
    HIGH = "high"
    LIMITED = "limited"
    MINIMAL = "minimal"
    NOT_CLASSIFIED = "not_classified"


class USDesignation(str, Enum):
    HIGH_IMPACT = "high_impact"
    STANDARD = "standard"
    NOT_CLASSIFIED = "not_classified"


class ModelType(str, Enum):
    CLASSIFICATION = "classification"
    GENERATION = "generation"
    RECOMMENDATION = "recommendation"
    DETECTION = "detection"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    OTHER = "other"


class DeploymentEnv(str, Enum):
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"
    RETIRED = "retired"


class DecisionAutomation(str, Enum):
    FULLY_AUTO = "fully_auto"
    SEMI_AUTO = "semi_auto"
    HUMAN_ASSISTED = "human_assisted"
    ADVISORY = "advisory"


class Sector(str, Enum):
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    EDUCATION = "education"
    EMPLOYMENT = "employment"
    LAW_ENFORCEMENT = "law_enforcement"
    IMMIGRATION = "immigration"
    CRITICAL_INFRASTRUCTURE = "critical_infrastructure"
    GOVERNMENT = "government"
    INSURANCE = "insurance"
    TRANSPORTATION = "transportation"
    CONSUMER = "consumer"
    LEGAL = "legal"
    OTHER = "other"


class DataSensitivity(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class SystemStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    UNDER_REVIEW = "under_review"
    RETIRED = "retired"
    ARCHIVED = "archived"


class ApprovalStatus(str, Enum):
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class ClassificationConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
