"""
EU AI Act Annex III + US OMB M-25-21 Dual Classification Engine.

This is the core risk classification logic for UC-1. It evaluates an AI system's
metadata to produce a dual classification:
  - EU AI Act: Prohibited / High / Limited / Minimal
  - US OMB M-25-21: High-Impact / Standard
"""
from dataclasses import dataclass


# ══════════════════════════════════════════════════════════════
# EU AI ACT ANNEX III — 8 HIGH-RISK CATEGORIES
# ══════════════════════════════════════════════════════════════

ANNEX_III_CATEGORIES = [
    {
        "id": "annex_iii_1",
        "name": "Biometrics",
        "description": "AI systems intended for biometric identification, categorisation, or emotion recognition",
        "keywords": [
            "biometric", "facial recognition", "face detection", "fingerprint",
            "iris scan", "voice recognition", "emotion recognition", "emotion detection",
            "gait analysis", "behavioral biometric", "liveness detection",
            "identity verification", "biometric categorisation",
        ],
        "sectors": ["law_enforcement", "government", "immigration"],
    },
    {
        "id": "annex_iii_2",
        "name": "Critical Infrastructure",
        "description": "AI systems intended as safety components in critical infrastructure management",
        "keywords": [
            "critical infrastructure", "power grid", "water supply", "gas supply",
            "heating", "electricity", "traffic management", "road traffic",
            "digital infrastructure", "safety component", "energy management",
            "nuclear", "dam control", "air traffic",
        ],
        "sectors": ["critical_infrastructure", "transportation", "government"],
    },
    {
        "id": "annex_iii_3",
        "name": "Education & Vocational Training",
        "description": "AI systems for determining access to or assignment in education and training",
        "keywords": [
            "education", "student admission", "academic assessment", "grading",
            "exam proctoring", "learning assessment", "vocational training",
            "student evaluation", "academic performance", "school admission",
            "university admission", "scholarship", "educational placement",
        ],
        "sectors": ["education"],
    },
    {
        "id": "annex_iii_4",
        "name": "Employment & Worker Management",
        "description": "AI systems for recruitment, selection, HR decisions, and worker management",
        "keywords": [
            "recruitment", "hiring", "resume screening", "cv screening",
            "candidate selection", "job application", "performance evaluation",
            "employee monitoring", "promotion", "termination", "workforce management",
            "task allocation", "worker surveillance", "talent acquisition",
            "interview scoring", "applicant tracking",
        ],
        "sectors": ["employment"],
    },
    {
        "id": "annex_iii_5",
        "name": "Essential Private & Public Services",
        "description": "AI systems for access to essential services including credit scoring, insurance, and benefits",
        "keywords": [
            "credit scoring", "credit assessment", "creditworthiness", "loan approval",
            "insurance pricing", "insurance risk", "benefits eligibility",
            "social assistance", "emergency services", "911 dispatch",
            "priority dispatch", "triage", "essential service",
            "welfare", "social security", "public benefit",
        ],
        "sectors": ["finance", "insurance", "healthcare", "government"],
    },
    {
        "id": "annex_iii_6",
        "name": "Law Enforcement",
        "description": "AI systems used by law enforcement for profiling, risk assessment, and evidence analysis",
        "keywords": [
            "law enforcement", "police", "criminal profiling", "risk assessment",
            "recidivism", "polygraph", "evidence analysis", "crime prediction",
            "predictive policing", "suspect identification", "forensic",
            "criminal justice", "parole", "bail", "sentencing",
        ],
        "sectors": ["law_enforcement"],
    },
    {
        "id": "annex_iii_7",
        "name": "Migration, Asylum & Border Control",
        "description": "AI systems used in migration and border management",
        "keywords": [
            "migration", "asylum", "border control", "visa", "immigration",
            "passport", "travel document", "border management", "refugee",
            "immigration screening", "deportation", "residence permit",
        ],
        "sectors": ["immigration", "government"],
    },
    {
        "id": "annex_iii_8",
        "name": "Administration of Justice & Democratic Processes",
        "description": "AI systems used to assist judicial authorities or influence elections",
        "keywords": [
            "judicial", "court", "sentencing", "legal research", "case outcome",
            "dispute resolution", "arbitration", "election", "voting",
            "democratic process", "political campaign", "voter targeting",
        ],
        "sectors": ["legal", "government"],
    },
]

# Prohibited AI practices under EU AI Act Art. 5
PROHIBITED_PATTERNS = [
    {
        "id": "art5_social_scoring",
        "name": "Social Scoring",
        "keywords": ["social scoring", "social credit", "citizen score", "trustworthiness score based on social behavior"],
    },
    {
        "id": "art5_subliminal",
        "name": "Subliminal Manipulation",
        "keywords": ["subliminal", "manipulate behavior", "exploit vulnerability", "psychological manipulation"],
    },
    {
        "id": "art5_realtime_biometric",
        "name": "Real-time Remote Biometric Identification in Public Spaces",
        "keywords": ["real-time biometric public", "mass surveillance biometric", "public space face recognition"],
    },
    {
        "id": "art5_emotion_workplace",
        "name": "Emotion Recognition in Workplace/Education (Prohibited Context)",
        "keywords": ["emotion recognition workplace", "emotion detection school", "emotional state employee"],
    },
]

# Limited risk — Art. 52 transparency obligations
LIMITED_RISK_PATTERNS = [
    "chatbot", "conversational ai", "virtual assistant", "deepfake",
    "synthetic media", "image generation", "text generation", "content generation",
    "recommendation system", "recommender", "personalization engine",
]


# ══════════════════════════════════════════════════════════════
# US OMB M-25-21 HIGH-IMPACT AI CATEGORIES
# ══════════════════════════════════════════════════════════════

OMB_HIGH_IMPACT_CATEGORIES = [
    {
        "id": "omb_health_safety",
        "name": "Health & Safety",
        "description": "AI that affects individual or public health and safety",
        "keywords": [
            "medical diagnosis", "clinical decision", "patient treatment",
            "drug dosing", "medical imaging", "radiology", "pathology",
            "health screening", "public health", "safety-critical",
            "autonomous vehicle", "surgical robot",
        ],
        "sectors": ["healthcare", "transportation"],
        "automation_triggers": ["fully_auto", "semi_auto"],
    },
    {
        "id": "omb_rights_civil_liberties",
        "name": "Rights & Civil Liberties",
        "description": "AI that affects individual rights, civil liberties, or civil rights",
        "keywords": [
            "surveillance", "monitoring", "facial recognition", "biometric",
            "free speech", "privacy", "civil rights", "discrimination",
            "profiling", "due process",
        ],
        "sectors": ["law_enforcement", "government"],
        "automation_triggers": ["fully_auto", "semi_auto"],
    },
    {
        "id": "omb_benefits_services",
        "name": "Access to Benefits & Services",
        "description": "AI that determines access to government benefits, services, or opportunities",
        "keywords": [
            "benefits eligibility", "welfare", "social security",
            "disability determination", "unemployment", "housing assistance",
            "food assistance", "veteran benefits", "government service",
        ],
        "sectors": ["government"],
        "automation_triggers": ["fully_auto", "semi_auto", "human_assisted"],
    },
    {
        "id": "omb_critical_infrastructure",
        "name": "Critical Infrastructure",
        "description": "AI used in critical infrastructure or national security",
        "keywords": [
            "critical infrastructure", "power grid", "water treatment",
            "financial system", "telecommunications", "defense",
            "national security", "nuclear",
        ],
        "sectors": ["critical_infrastructure", "government"],
        "automation_triggers": ["fully_auto", "semi_auto"],
    },
]


@dataclass
class ClassificationResult:
    eu_risk_tier: str
    us_designation: str
    risk_score: float
    confidence: str
    eu_rationale: dict
    us_rationale: dict
    matched_annex_iii_categories: list[str]
    matched_omb_categories: list[str]


class ClassificationService:
    """Dual risk classification engine: EU AI Act + US OMB M-25-21."""

    def classify(
        self,
        purpose_statement: str,
        sector: str,
        decision_automation: str,
        deployment_geo: list[str] | None = None,
        data_sensitivity: str = "internal",
        affected_population: str | None = None,
        model_type: str = "other",
    ) -> ClassificationResult:
        """Run dual classification and return structured result."""

        purpose_lower = purpose_statement.lower()
        affected_lower = (affected_population or "").lower()
        combined_text = f"{purpose_lower} {affected_lower}"

        # ── EU Classification ──
        eu_result = self._classify_eu(combined_text, sector, decision_automation, deployment_geo or [])

        # ── US Classification ──
        us_result = self._classify_us(combined_text, sector, decision_automation)

        # ── Composite Risk Score (0-100) ──
        risk_score = self._compute_risk_score(
            eu_result["tier"], us_result["designation"],
            data_sensitivity, decision_automation
        )

        # ── Confidence ──
        confidence = self._assess_confidence(eu_result, us_result)

        return ClassificationResult(
            eu_risk_tier=eu_result["tier"],
            us_designation=us_result["designation"],
            risk_score=risk_score,
            confidence=confidence,
            eu_rationale=eu_result,
            us_rationale=us_result,
            matched_annex_iii_categories=eu_result.get("matched_categories", []),
            matched_omb_categories=us_result.get("matched_categories", []),
        )

    def _classify_eu(self, text: str, sector: str, automation: str, geo: list[str]) -> dict:
        """Classify under EU AI Act risk tiers."""

        # Check prohibited first (Art. 5)
        prohibited_matches = []
        for pattern in PROHIBITED_PATTERNS:
            for kw in pattern["keywords"]:
                if kw in text:
                    prohibited_matches.append(pattern["id"])
                    break

        if prohibited_matches:
            return {
                "tier": "prohibited",
                "matched_categories": prohibited_matches,
                "reason": "Matches prohibited AI practices under EU AI Act Art. 5",
                "article": "Art. 5",
            }

        # Check high-risk (Annex III)
        annex_matches = []
        for category in ANNEX_III_CATEGORIES:
            score = 0
            matched_keywords = []

            # Keyword matching
            for kw in category["keywords"]:
                if kw in text:
                    score += 1
                    matched_keywords.append(kw)

            # Sector bonus
            if sector in category.get("sectors", []):
                score += 2

            if score >= 2:  # Threshold: at least 2 signals
                annex_matches.append({
                    "category_id": category["id"],
                    "category_name": category["name"],
                    "score": score,
                    "matched_keywords": matched_keywords,
                    "sector_match": sector in category.get("sectors", []),
                })

        if annex_matches:
            # Sort by score descending
            annex_matches.sort(key=lambda x: x["score"], reverse=True)
            return {
                "tier": "high",
                "matched_categories": [m["category_id"] for m in annex_matches],
                "category_details": annex_matches,
                "reason": f"Matches {len(annex_matches)} Annex III high-risk categories",
                "article": "Art. 6 + Annex III",
            }

        # Check limited risk (Art. 52)
        limited_matches = [p for p in LIMITED_RISK_PATTERNS if p in text]
        if limited_matches:
            return {
                "tier": "limited",
                "matched_categories": [],
                "matched_patterns": limited_matches,
                "reason": "Transparency obligations apply under Art. 52",
                "article": "Art. 52",
            }

        # Default: minimal risk
        return {
            "tier": "minimal",
            "matched_categories": [],
            "reason": "No high-risk or limited-risk indicators detected",
            "article": "N/A — minimal risk, no obligations beyond voluntary codes of conduct",
        }

    def _classify_us(self, text: str, sector: str, automation: str) -> dict:
        """Classify under US OMB M-25-21 high-impact AI categories."""

        omb_matches = []
        for category in OMB_HIGH_IMPACT_CATEGORIES:
            score = 0
            matched_keywords = []

            for kw in category["keywords"]:
                if kw in text:
                    score += 1
                    matched_keywords.append(kw)

            if sector in category.get("sectors", []):
                score += 2

            if automation in category.get("automation_triggers", []):
                score += 1

            if score >= 2:
                omb_matches.append({
                    "category_id": category["id"],
                    "category_name": category["name"],
                    "score": score,
                    "matched_keywords": matched_keywords,
                })

        if omb_matches:
            omb_matches.sort(key=lambda x: x["score"], reverse=True)
            return {
                "designation": "high_impact",
                "matched_categories": [m["category_id"] for m in omb_matches],
                "category_details": omb_matches,
                "reason": f"Matches {len(omb_matches)} OMB M-25-21 high-impact categories",
                "framework": "OMB M-25-21",
            }

        return {
            "designation": "standard",
            "matched_categories": [],
            "reason": "No high-impact indicators detected under OMB M-25-21",
            "framework": "OMB M-25-21",
        }

    def _compute_risk_score(self, eu_tier: str, us_designation: str, data_sensitivity: str, automation: str) -> float:
        """Compute composite 0-100 risk score from classification signals."""
        score = 0.0

        # EU tier weight (40%)
        eu_weights = {"prohibited": 40, "high": 32, "limited": 16, "minimal": 4, "not_classified": 0}
        score += eu_weights.get(eu_tier, 0)

        # US designation weight (25%)
        us_weights = {"high_impact": 25, "standard": 5, "not_classified": 0}
        score += us_weights.get(us_designation, 0)

        # Data sensitivity weight (20%)
        ds_weights = {"restricted": 20, "confidential": 15, "internal": 8, "public": 2}
        score += ds_weights.get(data_sensitivity, 0)

        # Automation level weight (15%)
        auto_weights = {"fully_auto": 15, "semi_auto": 10, "human_assisted": 5, "advisory": 2}
        score += auto_weights.get(automation, 0)

        return min(round(score, 1), 100.0)

    def _assess_confidence(self, eu_result: dict, us_result: dict) -> str:
        """Assess classification confidence based on match quality."""
        eu_categories = len(eu_result.get("matched_categories", []))
        us_categories = len(us_result.get("matched_categories", []))

        if eu_categories >= 2 or us_categories >= 2:
            return "high"
        elif eu_categories >= 1 or us_categories >= 1:
            return "medium"
        else:
            return "low"
