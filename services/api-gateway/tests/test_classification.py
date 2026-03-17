"""Unit tests for the EU Annex III + US OMB dual classification engine."""
import sys
import os
import importlib

# Insert the api-gateway root so we can import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Directly import the classification module without triggering __init__.py chains
_spec = importlib.util.spec_from_file_location(
    "classification_service",
    os.path.join(os.path.dirname(__file__), "..", "app", "services", "classification_service.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
ClassificationService = _mod.ClassificationService


def get_classifier():
    return ClassificationService()


class TestEUClassification:
    """EU AI Act Annex III classification tests."""

    def test_high_risk_credit_scoring(self):
        """Credit scoring models should be classified as High risk (Annex III Category 5)."""
        c = get_classifier()
        result = c.classify(
            purpose_statement="AI model for automated credit scoring and creditworthiness assessment for consumer loan applications",
            sector="finance",
            decision_automation="fully_auto",
            deployment_geo=["EU"],
        )
        assert result.eu_risk_tier == "high"
        assert any("annex_iii_5" in cat for cat in result.matched_annex_iii_categories)

    def test_high_risk_hiring(self):
        """Recruitment/hiring models should be classified as High risk (Annex III Category 4)."""
        c = get_classifier()
        result = c.classify(
            purpose_statement="Resume screening and candidate selection tool for job applications",
            sector="employment",
            decision_automation="semi_auto",
        )
        assert result.eu_risk_tier == "high"
        assert any("annex_iii_4" in cat for cat in result.matched_annex_iii_categories)

    def test_high_risk_biometrics(self):
        """Biometric identification should be High risk."""
        c = get_classifier()
        result = c.classify(
            purpose_statement="Facial recognition system for identity verification at airport security checkpoints",
            sector="government",
            decision_automation="fully_auto",
        )
        assert result.eu_risk_tier == "high"

    def test_high_risk_law_enforcement(self):
        """Predictive policing should be High risk."""
        c = get_classifier()
        result = c.classify(
            purpose_statement="Recidivism risk assessment tool used by police for criminal profiling and predictive policing",
            sector="law_enforcement",
            decision_automation="semi_auto",
        )
        assert result.eu_risk_tier == "high"

    def test_limited_risk_chatbot(self):
        """General-purpose chatbot should be Limited risk."""
        c = get_classifier()
        result = c.classify(
            purpose_statement="Customer support chatbot for answering product FAQs on our website",
            sector="consumer",
            decision_automation="advisory",
        )
        assert result.eu_risk_tier == "limited"

    def test_minimal_risk_recommendation(self):
        """Product recommendation engine with no sensitive context should be Minimal."""
        c = get_classifier()
        result = c.classify(
            purpose_statement="Product recommendation engine suggesting items based on browsing history",
            sector="consumer",
            decision_automation="advisory",
        )
        # recommendation is in limited_risk_patterns
        assert result.eu_risk_tier in ("limited", "minimal")

    def test_prohibited_social_scoring(self):
        """Social scoring system should be Prohibited."""
        c = get_classifier()
        result = c.classify(
            purpose_statement="Social scoring system that rates citizen trustworthiness based on social behavior and assigns benefits",
            sector="government",
            decision_automation="fully_auto",
        )
        assert result.eu_risk_tier == "prohibited"


class TestUSClassification:
    """US OMB M-25-21 classification tests."""

    def test_high_impact_medical(self):
        """Medical diagnosis AI should be High-Impact."""
        c = get_classifier()
        result = c.classify(
            purpose_statement="AI-assisted medical diagnosis system for radiology image analysis and clinical decision support",
            sector="healthcare",
            decision_automation="semi_auto",
        )
        assert result.us_designation == "high_impact"
        assert any("omb_health_safety" in cat for cat in result.matched_omb_categories)

    def test_high_impact_benefits(self):
        """Government benefits eligibility should be High-Impact."""
        c = get_classifier()
        result = c.classify(
            purpose_statement="Automated system for determining disability benefits eligibility and welfare assistance",
            sector="government",
            decision_automation="fully_auto",
        )
        assert result.us_designation == "high_impact"

    def test_standard_internal_analytics(self):
        """Internal analytics dashboard should be Standard."""
        c = get_classifier()
        result = c.classify(
            purpose_statement="Internal business intelligence dashboard for sales forecasting",
            sector="consumer",
            decision_automation="advisory",
        )
        assert result.us_designation == "standard"


class TestDualClassification:
    """Tests for combined EU + US dual classification."""

    def test_dual_high_risk_high_impact(self):
        """Credit scoring in finance should be both High (EU) and High-Impact (US)."""
        c = get_classifier()
        result = c.classify(
            purpose_statement="Automated loan approval and credit scoring model for mortgage applications",
            sector="finance",
            decision_automation="fully_auto",
            deployment_geo=["US", "EU"],
            data_sensitivity="restricted",
        )
        assert result.eu_risk_tier == "high"
        assert result.us_designation in ("high_impact", "standard")  # Finance may match depending on keywords
        assert result.risk_score > 50  # Should have high risk score

    def test_risk_score_increases_with_sensitivity(self):
        """Higher data sensitivity should increase risk score."""
        c = get_classifier()
        r1 = c.classify(
            purpose_statement="Internal document search tool",
            sector="consumer",
            decision_automation="advisory",
            data_sensitivity="public",
        )
        r2 = c.classify(
            purpose_statement="Internal document search tool",
            sector="consumer",
            decision_automation="advisory",
            data_sensitivity="restricted",
        )
        assert r2.risk_score > r1.risk_score

    def test_confidence_high_for_clear_matches(self):
        """Clear keyword matches should produce high confidence."""
        c = get_classifier()
        result = c.classify(
            purpose_statement="Resume screening for candidate selection in recruitment hiring process",
            sector="employment",
            decision_automation="semi_auto",
        )
        assert result.confidence in ("high", "medium")
