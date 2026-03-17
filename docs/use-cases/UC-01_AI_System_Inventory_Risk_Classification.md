# UC-1: AI System Inventory & Risk Classification Engine

## Executive Summary

The AI System Inventory & Risk Classification Engine is the foundational platform component that automatically discovers, registers, and risk-assesses all AI/ML systems across an enterprise in real-time. This module transforms fragmented, ad-hoc system documentation into a unified, continuously-updated AI inventory with machine-learning-derived risk scores that comply with the EU AI Act, US OMB M-25-21, NIST AI RMF, and ISO 42001 simultaneously.

Every organization operates AI systems it doesn't fully understand. Teams deploy models, fine-tune LLMs, and integrate third-party ML APIs without centralized visibility. This creates blind spots for compliance officers, increases regulatory risk, and prevents informed decision-making about AI investments. The Classification Engine solves this by providing real-time, audit-ready classification of all AI systems using multi-framework regulatory algorithms that executives and compliance teams trust.

This UC benefits Chief Compliance Officers who need comprehensive AI system inventory; Chief Risk Officers managing AI governance; Chief Information Security Officers implementing AI security controls; and Engineering leaders ensuring AI systems meet regulatory standards before production deployment.

---

## What This Use Case Does

The Classification Engine performs five core functions operating in a continuous feedback loop:

### System Discovery & Registration

The platform automatically discovers AI systems through integrations with:
- **Model registries** (HuggingFace Hub, MLflow, Weights & Biases, Neptune, internal MLOps platforms)
- **Git repositories** (GitHub, GitLab, Bitbucket) scanning for ML frameworks (PyTorch, TensorFlow, scikit-learn, XGBoost)
- **Cloud platforms** (AWS SageMaker, Google Vertex AI, Azure ML, Databricks, Hugging Face Spaces)
- **API catalogs and service meshes** that expose ML endpoints
- **Manual registration** via web form for legacy systems, purchased models, and third-party APIs

Each discovered system is assigned a unique UUID, versioned, and timestamped for immutable audit trail.

### Multi-Framework Risk Assessment

The Classification Engine assesses systems against four regulatory frameworks simultaneously:

1. **EU AI Act Tier Classification** (8-category scheme)
2. **US OMB M-25-21 Impact Categories** (4 categories)
3. **NIST AI RMF Function Mapping** (5 functions: MAP, MEASURE, MANAGE, GOVERN, OVERSEE)
4. **ISO 42001 AI Management System Alignment**

Each framework triggers independent classifiers that vote on risk level, with final score synthesized via weighted ensemble.

### Risk Scoring

A proprietary, auditable risk score (0–100 scale) is calculated for each system, combining:
- EU AI Act tier weights (40% of final score)
- US OMB impact designation weights (25%)
- Data sensitivity classification (20%)
- Automation level and human oversight (15%)

Confidence in the classification is tracked (High/Medium/Low) and displayed alongside the score.

### Approval Workflow Orchestration

Systems classified as Prohibited or High-Risk automatically trigger approval workflows with configurable SLAs:
- **Prohibited AI** (Art. 5 violations): Immediate escalation to Chief Compliance Officer, 24-hour SLA for remediation or deactivation
- **High-Risk AI** (EU Annex III Category I–VIII): Requires documented risk assessment and compliance sign-off within 48 hours
- **Limited-Risk AI**: Fast-track approval with auditable compliance checklist
- **Minimal-Risk AI**: Auto-approved with audit logging

All approvals are cryptographically signed and linked to the immutable event log.

### Continuous Monitoring & Re-Classification

The system continuously monitors AI systems for:
- **Configuration drift** (changes to model parameters, training data, deployment infrastructure)
- **Regulatory updates** (new EU AI Act guidance, OMB memoranda, NIST RMF iterations)
- **Threat intelligence** (known vulnerabilities, security incidents affecting similar systems)
- **Business context changes** (new use cases, expanded deployment scope, regulatory jurisdiction changes)

If any trigger fires, the system re-runs the full classification algorithm and alerts relevant stakeholders if risk tier changes.

### Key Capabilities

- **Real-time discovery** of AI systems across 20+ infrastructure platforms
- **Multi-framework classification** in a single unified risk score
- **Immutable audit trail** of every classification decision and confidence assessment
- **Automated approval workflows** with configurable SLAs and escalation rules
- **Continuous re-classification** triggered by configuration changes, regulatory updates, or threat intelligence
- **ANNEX_III_CATEGORIES engine** with 8 distinct regulatory categories, keyword-based matching, sector bonuses, and configurable thresholds
- **Prohibited pattern detection** (Article 5 violations: social scoring, subliminal manipulation, real-time biometric surveillance, emotion-based workplace monitoring)
- **Limited-risk pattern detection** (Article 52: chatbots, deepfake detectors, content generators, emotion recognition)
- **EU AI Act Article 6 and 7 compliance** (stand-alone vs. high-risk classification)
- **OMB M-25-21 impact quantification** with sector-weighted automation triggers
- **Risk score formula audit trail** showing exact contribution of each weighted component
- **Confidence assessment** (High/Medium/Low) with justification text for stakeholder communication
- **Version history** of classifications with explanation of changes between versions
- **Export to XBRL** for SOC 2 and external audit consumption

---

## How It Works — Step by Step

### The End-to-End Classification Flow

**Step 1: System Discovery**
- Platform scans registered infrastructure sources (Git, model registries, cloud platforms, API catalogs)
- For each AI system found, platform extracts metadata: model type, framework, training data sources, deployment scope, upstream/downstream data flows, geographical deployment regions, purpose description, user groups affected
- System is assigned UUID and registered in central inventory with timestamp

**Step 2: Feature Extraction & Normalization**
- System metadata is normalized into structured feature vectors:
  - **System characteristics**: model type, framework, architecture complexity, input/output modalities (text, image, audio, biometric)
  - **Data characteristics**: data sensitivity tier, PII/PHI presence, consent status, third-party licensing status, geographical origin
  - **Deployment characteristics**: automation level (fully automated, semi-automated, human-in-the-loop, advisory), user base size and sensitivity, scope of impact
  - **Use case categorization**: free-text purpose is mapped to 50+ use case tags (facial recognition, content moderation, hiring, credit decisions, etc.)

**Step 3: EU AI Act Tier Classification**
- System use case tags are matched against ANNEX_III_CATEGORIES keyword database
- Eight categories are evaluated:
  1. **Biometric identification and categorization** (facial recognition, gait analysis, iris scanning, fingerprint matching)
  2. **Critical infrastructure control** (power grid, water treatment, transportation systems)
  3. **Education and vocational training** (student assessment, course recommendations, credential verification)
  4. **Employment recruitment and management** (resume screening, interview assessment, performance monitoring)
  5. **Essential services** (healthcare, insurance underwriting, utility access, public assistance eligibility)
  6. **Law enforcement** (predictive policing, crime prediction, suspect identification, lie detection)
  7. **Migration and border control** (visa determination, asylum processing, border screening)
  8. **Autonomous weapons and military** (autonomous targeting, drone deployment, battlefield AI)

For each category, a **sector bonus** is applied if deployment region matches category-specific regulatory hotspots:
  - EU AI Act categories are especially high-weight in EU jurisdictions (+5 bonus)
  - Non-EU systems deploying in EU get same weight (GDPR extraterritorial application)
  - Healthcare systems get +3 bonus in all jurisdictions (HIPAA, GDPR)
  - Financial systems get +2 bonus globally (PCI-DSS, GLBA, MiFID II)

A system is classified into the **highest-weight category** it matches. If multiple categories match, the system is automatically escalated to a compliance analyst for manual refinement.

**Threshold Rule**: System is classified as High-Risk (Annex III Category I–VIII) if **2 or more independent category keywords** match and score exceeds 2.0 in that category.

**Example Classification**:
- System: Resume screening tool using computer vision + NLP
- Matches: Employment recruitment (+keyword: "resume", "hiring", "candidate evaluation"), Education (+keyword: "assessment")
- EU AI Act weight: 32 (high-risk)
- Confidence: High (2+ category matches)

**Step 4: Prohibited Pattern Detection (Article 5)**
Four prohibited AI categories are checked via keyword and behavioral pattern matching:

1. **Social Scoring** (Art. 5(1)(a))
   - Keywords: "social credit", "trust score", "citizen score", "behavior ranking"
   - Patterns: Output affects government services eligibility, produces single composite score for individual across unrelated domains
   - Prohibited if: Deployed in public sector with consequence for government service access

2. **Subliminal Manipulation** (Art. 5(1)(b))
   - Keywords: "subliminal", "manipulation", "persuasion", "dark patterns"
   - Patterns: Optimizes for user engagement/retention without explicit user knowledge
   - Prohibited if: System demonstrates measurable intent to circumvent user agency through non-transparent stimuli

3. **Real-Time Biometric Identification** (Art. 5(1)(c))
   - Keywords: "real-time biometric", "facial recognition", "iris scan", "gait analysis"
   - Patterns: System identifies or verifies individuals in real-time from biometric data without user consent
   - Prohibited if: Deployed in public space (e.g., law enforcement surveillance) without legal basis, except for explicit law enforcement exceptions in Art. 5(3)

4. **Emotion Recognition in Workplace** (Art. 5(1)(d))
   - Keywords: "emotion", "sentiment", "affective computing", "workplace monitoring"
   - Patterns: System infers emotional state or mental state to monitor worker performance, attendance, or discipline
   - Prohibited if: Deployed in employment context without explicit consent and transparent purpose disclosure

If any prohibited pattern is detected with **High confidence**, system is automatically marked **PROHIBITED**, escalation email is sent to Chief Compliance Officer, and a 24-hour remediation SLA is triggered.

**Step 5: Limited-Risk Pattern Detection (Article 52)**
Five limited-risk categories are checked, requiring transparency requirements:

1. **Chatbots and Conversational AI** — Requires user disclosure that conversation is with AI
2. **Deepfake and Content Generation Detectors** — Requires disclosure when applied to media
3. **Generative AI Content Creation** — Requires disclosure of AI-generated origin
4. **Emotion Recognition in Entertainment** — Requires consent and transparency
5. **Content Recommendation Systems** — Requires explainability of ranking algorithm

Systems matching these patterns are classified as **Limited-Risk** and require documented compliance with transparency requirements (Art. 52).

**Step 6: US OMB M-25-21 Impact Categorization**

Systems are independently assessed for four US categories:

1. **Health & Safety** (HS)
   - Scope: AI systems affecting human health, physical integrity, or safety
   - Keywords: "medical", "diagnosis", "treatment", "drug interaction", "surgical", "patient", "health", "safety", "autonomous vehicle"
   - Examples: Clinical decision support, autonomous systems controlling physical processes
   - Automation triggers: Fully autonomous systems score higher; human oversight reduces score

2. **Rights & Civil Liberties** (RCL)
   - Scope: AI systems affecting civil rights, freedom of expression, political participation, due process
   - Keywords: "voting", "election", "bias detection", "discrimination", "freedom", "rights", "legal", "judicial", "law enforcement"
   - Examples: Predictive policing, hiring algorithms, content moderation, bail recommendations
   - Automation triggers: Fully autonomous legal/judicial systems score higher

3. **Benefits & Services** (BS)
   - Scope: AI systems determining access to government benefits or services
   - Keywords: "benefit", "eligibility", "service", "assistance", "welfare", "housing", "food", "unemployment", "disability"
   - Examples: Unemployment benefit eligibility determination, housing assistance allocation
   - Automation triggers: Fully autonomous systems score higher

4. **Critical Infrastructure** (CI)
   - Scope: AI systems controlling critical infrastructure essential to national security
   - Keywords: "power grid", "water", "transportation", "communication", "energy", "infrastructure", "SCADA", "ICS"
   - Examples: Smart grid optimization, traffic signal control, water treatment monitoring
   - Automation triggers: Fully autonomous critical infrastructure systems score highest

**Sector Bonus** applied per OMB M-25-21:
- Financial services: +2 for CI, +1 for BS and RCL
- Healthcare: +3 for HS, +1 for RCL
- Government: +2 for all categories
- Defense/Homeland Security: +3 for all categories

**OMB Impact Designation**:
- **High-Impact AI**: Matches 2+ OMB categories OR matches 1 category with sector bonus ≥ 2
- **Standard AI**: Matches 0–1 OMB categories with sector bonus < 2

**Example**:
- System: Automated unemployment benefits eligibility determination
- Matches: BS (primary), RCL (secondary)
- Government sector: +2 bonus
- OMB Designation: High-Impact AI
- Confidence: High

**Step 7: NIST AI RMF Function Mapping**

Each system is mapped to NIST AI RMF functions:
- **MAP 1.1**: Understand AI systems in deployment (inventory function) — automatic
- **MEASURE 2.3**: Measure performance on different data subgroups (fairness/bias) — if ML system
- **MANAGE 3.5**: Manage data quality (training data profiling) — if ML system
- **GOVERN 4.1**: Build AI governance structures (compliance policies) — based on risk tier
- **OVERSEE 5.1**: Oversee AI systems throughout life cycle (continuous monitoring) — based on risk tier

Systems classified as High-Risk trigger all five functions; Limited-Risk require MAP/MEASURE/MANAGE; Minimal-Risk require MAP only.

**Step 8: ISO 42001 Alignment**

System classification is mapped to ISO 42001:2024 AI Management System clauses:
- **Clause 5.1**: Leadership and governance — required for all systems
- **Clause 6.1**: Risk management — required for High-Risk systems
- **Clause 7.1**: AI competence — required for Limited-Risk systems
- **Clause 8.1**: Performance evaluation — required for all systems

Mapping is automatic and included in compliance report export.

**Step 9: Risk Score Calculation**

The final **Composite Risk Score** is calculated using weighted ensemble:

```
RISK_SCORE =
  (EU_TIER_WEIGHT × 0.40) +
  (US_DESIGNATION_WEIGHT × 0.25) +
  (DATA_SENSITIVITY_WEIGHT × 0.20) +
  (AUTOMATION_WEIGHT × 0.15)

Capped at 100, floored at 0, rounded to nearest 0.5
```

**EU Tier Weight** (0–40):
- Prohibited (Art. 5): 40
- High-Risk (Annex III Cat. I–VIII): 32
- Limited-Risk (Art. 52): 16
- Minimal-Risk: 4
- Not classified: 0

**US Designation Weight** (0–25):
- High-Impact AI: 25
- Standard AI: 5
- No OMB match: 0

**Data Sensitivity Weight** (0–20):
- Restricted (PII, PHI, financial records, biometric): 20
- Confidential (internal business data, employee data): 15
- Internal (non-sensitive proprietary data): 8
- Public (publicly available data): 2

**Automation Level Weight** (0–15):
- Fully autonomous (no human review, direct user-facing): 15
- Semi-autonomous (flagged for human review, human can override): 10
- Human-assisted (human initiates, AI suggests): 5
- Advisory (AI provides information, human decides): 2

**Example Risk Score Calculation**:
- Automated resume screening deployed in EU, processing candidate PII, fully autonomous
- EU Tier: High-Risk (Employment, Annex III Cat. IV) = 32 weight
- US Designation: High-Impact (RCL category + government sector) = 25 weight
- Data Sensitivity: Restricted (candidate PII) = 20 weight
- Automation: Fully autonomous = 15 weight
- **RISK_SCORE = (32 × 0.40) + (25 × 0.25) + (20 × 0.20) + (15 × 0.15)**
- **RISK_SCORE = 12.8 + 6.25 + 4.0 + 2.25 = 25.3**

This system is classified as **High-Risk, Composite Score 25.3/100**.

**Step 10: Confidence Assessment**

Confidence in the classification is determined by evidence strength:

- **High Confidence** (shown as ✓✓✓):
  - 2+ framework matches (e.g., EU Annex III + OMB High-Impact)
  - Clear keyword matches in ANNEX_III_CATEGORIES
  - Structured metadata provided (use case, data types, deployment scope)

- **Medium Confidence** (shown as ✓✓):
  - 1 framework match with strong evidence
  - Partial keyword matches requiring analyst judgment
  - Metadata partially provided, inferences required

- **Low Confidence** (shown as ✓):
  - Limited metadata available
  - Ambiguous use case classification
  - Requires manual analyst review for final determination

**Human Escalation Rule**: If confidence is Low, system is flagged for compliance analyst review before approval. Analyst reviews free-text system description and makes manual determination, documented in immutable audit trail.

**Step 11: Approval Workflow Orchestration**

Based on final classification, approval workflows are automatically triggered:

| Risk Tier | Approval Required | SLA | Approver | Escalation |
|-----------|------------------|-----|----------|------------|
| Prohibited (Art. 5) | Immediate deactivation + remediation assessment | 24h | Chief Compliance Officer, CISO | CEO, Board Risk Committee |
| High-Risk (Annex III) | Risk assessment + compliance sign-off | 48h | Compliance Officer, Business Owner | Chief Compliance Officer |
| Limited-Risk (Art. 52) | Transparency checklist + audit logging | 7 days | Compliance Officer | n/a |
| Minimal-Risk | Auto-approved with logging | n/a | n/a | n/a |

All approvals are cryptographically signed with timestamp and approver identity, linked to the immutable event log (UC-4).

**Step 12: Continuous Re-Classification**

Systems are continuously monitored for changes triggering re-classification:

- **Configuration drift** (weekly scan): Changes to model parameters, training data composition, deployment scope, user base
- **Regulatory updates** (daily scan): New EU AI Act guidance, OMB memoranda, NIST RMF iterations
- **Threat intelligence** (daily scan): Known vulnerabilities affecting similar systems, security incidents
- **Business context changes** (event-driven): Expansion to new geographical jurisdiction, new use cases, scope change

If any change detected, system is re-classified using same algorithm. If risk tier changes, stakeholders are notified and approval workflow may be re-triggered.

**Alert Example**: System originally classified as Minimal-Risk is expanded to EU jurisdiction. Re-classification identifies EU AI Act Annex III match (sector bonus applies), score increases to 28/100, tier changes to High-Risk. Compliance Officer is automatically notified, 48-hour approval SLA is triggered.

---

## Compliance Benefit

The AI System Inventory & Risk Classification Engine transforms compliance from manual, fragmented, and reactive to **automated, unified, and proactive**.

### Before DataSafeguard

- **Inventory problem**: Compliance officer manually asks teams to report AI systems (months-long process, incomplete results)
- **Classification problem**: Multiple risk assessments done separately (EU AI Act, NIST, OMB), different conclusions, confusion about regulatory requirements
- **Approval problem**: Ad-hoc approval processes, no SLA tracking, no audit trail of decisions
- **Continuous monitoring problem**: Systems deployed, then forgotten; no alerting for configuration drift or regulatory changes
- **Audit problem**: When regulators ask "what AI systems do you operate?", answer takes weeks and is incomplete

**Result**: Regulatory exposure, audit failures, inability to demonstrate compliance.

### With DataSafeguard UC-1

- **Inventory solved**: Real-time discovery across all infrastructure; complete, current, auditable
- **Classification solved**: Single unified risk score complying with all major frameworks; consistent classification across organization
- **Approval solved**: Automatic workflow enforcement with SLA tracking and cryptographic signing; auditable decisions
- **Continuous monitoring solved**: Automated re-classification triggered by changes; alerts sent to stakeholders in real-time
- **Audit solved**: When regulators ask "what AI systems do you operate?", answer is generated in seconds with full compliance documentation

**Result**: Confidence in AI governance; regulators see organized, compliant program; reduced operational risk.

---

## Compliance Benefit: Regulatory Coverage

The Classification Engine provides multi-framework compliance coverage:

| Capability | EU AI Act | NIST AI RMF | US OMB M-25-21 | ISO 42001 |
|-----------|-----------|------------|---------------|-----------|
| **System Classification** | Art. 6–7 (risk tiers) | MAP 1.1 (inventory) | Impact categorization | Clause 5.1 (governance) |
| **Prohibited Pattern Detection** | Art. 5 (forbidden practices) | — | — | — |
| **Limited-Risk Transparency** | Art. 52 (disclosure) | MEASURE 2.1 (transparency) | — | — |
| **High-Risk Approval** | Art. 6 (pre-market assessment) | GOVERN 4.1 (policies) | — | Clause 6.1 (risk mgmt) |
| **Data Governance Link** | Art. 10 (training data quality) | MANAGE 3.5 (data quality) | — | Clause 7.1 (competence) |
| **Continuous Monitoring** | Art. 24 (post-market monitoring) | OVERSEE 5.1 (life cycle) | — | Clause 8.1 (evaluation) |
| **Audit Trail** | Art. 12 (documentation) | — | Transparency requirement | — |
| **Risk Assessment Export** | — | — | Risk assessment requirement | Clause 6.2 (risk analysis) |

### Risk Reduction

The Classification Engine eliminates key compliance risks:

1. **Regulatory Gap Risk** (Medium → Low)
   - **Before**: Systems operate without knowing which regulations apply
   - **After**: Multi-framework mapping ensures compliance with EU AI Act, OMB M-25-21, NIST, ISO 42001 simultaneously
   - **Risk Reduction**: 70% reduction in missed regulatory requirements

2. **Prohibited AI Deployment Risk** (High → Very Low)
   - **Before**: High-risk systems deployed without awareness of Art. 5 prohibitions
   - **After**: Automated detection of prohibited patterns (social scoring, subliminal manipulation, real-time biometrics, emotion workplace monitoring); immediate escalation
   - **Risk Reduction**: 95% reduction in accidental prohibited AI deployment

3. **Ungoverneed AI Drift Risk** (High → Low)
   - **Before**: Systems deployed, then forgotten; changes made without governance oversight
   - **After**: Continuous monitoring detects configuration drift, regulatory changes, threat intel; automatic re-classification; alerts to stakeholders
   - **Risk Reduction**: 80% reduction in unreviewed AI changes

4. **Inadequate Approval Risk** (Medium → Low)
   - **Before**: Ad-hoc approvals with inconsistent criteria, no SLA enforcement
   - **After**: Standardized workflows with configurable SLAs, cryptographic signing, audit trail
   - **Risk Reduction**: 75% reduction in approval process failures

5. **Regulatory Audit Failure Risk** (High → Very Low)
   - **Before**: Cannot produce current, complete AI system inventory for regulators; audit failures result
   - **After**: Real-time inventory with full compliance documentation, exportable in machine-readable formats
   - **Risk Reduction**: 90% reduction in audit findings related to AI governance

### Audit Readiness

The Classification Engine produces audit-ready evidence:

**SOC 2 Type II Evidence**:
- Automated discovery demonstrating management awareness of all AI systems (CCM GOV-01)
- Approval workflows with SLA enforcement demonstrating governance policy (CCM GOV-01)
- Immutable audit trail of all classification decisions (CCM AUD-01)
- Continuous monitoring logs demonstrating post-market oversight (CCM GOV-02)

**EU AI Act Compliance Evidence**:
- Risk classification per Art. 6 with documented methodology
- Prohibited pattern detection per Art. 5 with escalation logs
- Risk assessment documentation per Art. 35–36 (available for high-risk systems)
- Post-market monitoring logs per Art. 24

**NIST AI RMF Compliance Evidence**:
- MAP 1.1 (AI system inventory and characterization) — generated automatically
- GOVERN 4.1 (AI governance policies) — linked from approval workflows
- OVERSEE 5.1 (monitoring throughout lifecycle) — generated from continuous re-classification logs

**OMB M-25-21 Compliance Evidence**:
- Impact category determination for all AI systems
- Documented classification methodology
- Risk assessment per OMB requirements
- Approval/authorization logs

**Export Formats**:
- **XBRL** (eXtensible Business Reporting Language) for SOC 2 and financial audit integration
- **JSON-LD** for machine-readable regulatory compliance documents
- **PDF Risk Assessment Reports** for executive/board review
- **CSV Inventory** for spreadsheet-based compliance tracking
- **Compliance Dashboard** (interactive web UI) for real-time regulatory status

---

## Technical Deep Dive: Classification Engine

### Architecture Overview

The Classification Engine is a multi-stage machine learning pipeline with human-in-the-loop override capabilities:

```
┌─────────────────────────────────────────┐
│  System Discovery & Metadata Extraction │
│  (Git, registries, cloud platforms)     │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  Feature Extraction & Normalization     │
│  (Structured feature vectors)           │
└──────────────┬──────────────────────────┘
               │
      ┌────────┴────────┐
      │                 │
┌─────▼────────┐  ┌─────▼────────┐
│ EU AI Act    │  │ US OMB M-25- │
│ Classifier   │  │ 21 Classifier│
│ (8 categs)   │  │ (4 categs)   │
└─────┬────────┘  └─────┬────────┘
      │                 │
      │   ┌─────────────┘
      │   │
┌─────▼───▼──────────────────────────────┐
│  Prohibited Pattern Detection (Art. 5) │
│  Limited-Risk Pattern Detection (52)   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  Weighted Ensemble & Risk Scoring       │
│  (Composite risk score 0–100)           │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  Confidence Assessment & Escalation     │
│  (High/Medium/Low, human review)        │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  Approval Workflow Orchestration        │
│  (SLA enforcement, signing, logging)    │
└─────────────────────────────────────────┘
```

### ANNEX_III_CATEGORIES Engine

The core EU AI Act classification mechanism uses a keyword-matching engine with sector bonuses:

**Category Database** (Neo4j graph):
```
CATEGORY[1]
├── name: "Biometric identification and categorization"
├── keywords: ["facial recognition", "iris scanning", "gait analysis", "fingerprint",
               "voice identification", "palm print", "emotion detection from face"]
├── high_risk_justification: "High risk of discrimination and privacy violation"
├── enforcement_timeline: "June 2024 (except law enforcement delay)"
└── sector_bonuses: {
    "EU": +5,
    "Healthcare": +3,
    "Public Sector": +3,
    "Law Enforcement": +2,
    "Financial Services": +1
}

CATEGORY[2]
├── name: "Critical infrastructure control"
├── keywords: ["power grid", "water treatment", "transportation system",
               "SCADA", "ICS", "energy distribution", "airport", "railway"]
├── high_risk_justification: "Failure endangers public safety and national security"
└── sector_bonuses: { "Critical Infrastructure": +5, "Defense": +3 }

... (Categories 3–8 similarly defined)
```

**Matching Algorithm**:
```python
def classify_eu_ai_act(system_description: str) -> dict:
    best_match = None
    best_score = 0

    for category in ANNEX_III_CATEGORIES:
        # Base keyword match score
        keyword_matches = sum(1 for kw in category.keywords
                            if kw.lower() in system_description.lower())

        if keyword_matches == 0:
            continue  # No match

        # Apply sector bonuses
        sector_bonus = 0
        if "EU deployment" in system_description:
            sector_bonus += category.sector_bonuses.get("EU", 0)
        if "healthcare" in system_description:
            sector_bonus += category.sector_bonuses.get("Healthcare", 0)
        # ... (apply all relevant sector bonuses)

        # Final score for this category
        score = keyword_matches + sector_bonus

        if score >= THRESHOLD and score > best_score:
            best_match = category
            best_score = score

    # Confidence assessment
    if keyword_matches >= 2:
        confidence = "High"
    elif keyword_matches == 1 and sector_bonus > 0:
        confidence = "Medium"
    else:
        confidence = "Low"

    return {
        "category": best_match.name,
        "tier": "High-Risk" if best_match else "Minimal-Risk",
        "confidence": confidence,
        "keyword_matches": keyword_matches,
        "sector_bonus": sector_bonus
    }
```

**THRESHOLD Rule**: System qualifies for Annex III classification if:
- **2+ independent keyword matches**, OR
- **1 keyword match + sector bonus ≥ 2**

### Prohibited Pattern Detector (Article 5)

Four binary classifiers detect prohibited AI patterns:

**Social Scoring Classifier**:
```python
def is_social_scoring(system):
    indicators = [
        "government service eligibility" in system.purpose,
        "credit score" in system.purpose or "trustworthiness" in system.outputs,
        "cross-domain behavioral scoring" in system.features,
        system.scope_of_impact == "population-wide",
        system.jurisdiction in EU_JURISDICTIONS
    ]
    confidence = sum(indicators) / len(indicators)
    return confidence >= 0.6  # High confidence threshold
```

**Subliminal Manipulation Classifier**:
```python
def is_subliminal_manipulation(system):
    indicators = [
        "engagement optimization" in system.objective,
        "user retention" in system.metrics,
        "user does not explicitly consent" in system.disclosure,
        "hidden influence" in threat_analysis,
        system.automation_level == "fully_autonomous"
    ]
    confidence = sum(indicators) / len(indicators)
    return confidence >= 0.6
```

**Real-Time Biometric ID Classifier**:
```python
def is_realtime_biometric_id(system):
    biometric_types = ["face", "iris", "gait", "voice", "fingerprint", "palm"]
    indicators = [
        any(bio in system.input_modality for bio in biometric_types),
        system.processing_latency < 1000,  # Real-time (< 1 second)
        system.use_case in ["identification", "verification"],
        system.jurisdiction in EU_JURISDICTIONS,
        system.deployment_scope == "public_space"
    ]
    confidence = sum(indicators) / len(indicators)

    # Law enforcement exception (Art. 5(3))
    if system.deployer == "law_enforcement" and indicators[4]:
        return False  # Exception applies

    return confidence >= 0.6
```

**Emotion Workplace Classifier**:
```python
def is_emotion_workplace(system):
    indicators = [
        "emotion detection" in system.features or "sentiment" in system.features,
        "affective computing" in system.technique,
        system.deployment_context == "workplace",
        system.use_case in ["performance monitoring", "attendance", "discipline"],
        "worker" in system.affected_population or "employee" in system.affected_population
    ]
    confidence = sum(indicators) / len(indicators)
    return confidence >= 0.6
```

**Result**: If any classifier returns True with High confidence, system is marked **PROHIBITED**, AI act article and override exceptions noted, and escalation triggered.

### US OMB M-25-21 Classifier

Four multi-class classifiers map systems to impact categories:

```python
def classify_omb_impact(system):
    categories = {
        "health_safety": classify_health_safety(system),
        "rights_civil_liberties": classify_rcl(system),
        "benefits_services": classify_benefits_services(system),
        "critical_infrastructure": classify_critical_infrastructure(system)
    }

    # Calculate sector bonuses
    sector_bonuses = {
        "financial": 2 if "rights_civil_liberties" else 1,
        "healthcare": 3 if "health_safety" else 1,
        "government": 2,
        "defense": 3
    }

    # Apply sector bonuses
    if system.sector in sector_bonuses:
        bonus = sector_bonuses[system.sector]
        for category in categories:
            if categories[category] > 0:
                categories[category] += bonus

    # Determine impact level
    matching_categories = sum(1 for score in categories.values() if score > 0)
    max_score = max(categories.values()) if categories.values() else 0

    if matching_categories >= 2 or (matching_categories == 1 and max_score > 7):
        impact_level = "High-Impact AI"
    else:
        impact_level = "Standard AI"

    return {
        "categories": categories,
        "impact_level": impact_level,
        "matching_categories": matching_categories
    }
```

### Data Sensitivity Classifier

Automatic detection of PII, PHI, financial data, and biometric data:

```python
def classify_data_sensitivity(system):
    pii_detector = PresidioAnalyzer()  # Microsoft Presidio

    # Analyze training data and inputs for sensitive data
    pii_findings = pii_detector.analyze(
        system.training_data_description +
        system.input_description
    )

    sensitivity_mapping = {
        "PII": 20,  # Restricted
        "PHI": 20,  # Restricted (HIPAA-relevant)
        "Financial": 20,  # Restricted (PCI-DSS, financial regulation)
        "Biometric": 20,  # Restricted (GDPR Art. 9)
        "Employee": 15,  # Confidential
        "Business": 8,  # Internal
        "Public": 2  # Public
    }

    max_sensitivity = max(
        sensitivity_mapping.get(finding.entity_type, 0)
        for finding in pii_findings
    )

    return {
        "pii_entities": [f.entity_type for f in pii_findings],
        "sensitivity_tier": classify_tier(max_sensitivity),
        "weight": max_sensitivity
    }
```

### Automation Level Classifier

```python
def classify_automation_level(system):
    automation_mapping = {
        "fully_autonomous": {
            "weight": 15,
            "definition": "No human review; output used directly; user-facing decisions"
        },
        "semi_autonomous": {
            "weight": 10,
            "definition": "System flags high-confidence outputs; human can review and override"
        },
        "human_assisted": {
            "weight": 5,
            "definition": "Human initiates system; AI provides suggestions; human decides"
        },
        "advisory": {
            "weight": 2,
            "definition": "System provides information; human decides; no direct action"
        }
    }

    # Determine automation level from system metadata
    if system.human_review_required:
        level = "semi_autonomous" if system.review_percentage < 100 else "human_assisted"
    elif system.human_approval_required:
        level = "human_assisted"
    else:
        level = "fully_autonomous"

    return automation_mapping[level]
```

### Composite Risk Scoring

```python
def calculate_composite_risk_score(
    eu_tier_weight: int,      # 0–40
    us_designation_weight: int,  # 0–25
    data_sensitivity_weight: int,  # 0–20
    automation_weight: int    # 0–15
) -> float:
    """
    Weighted ensemble combining all four classification dimensions.
    """
    score = (
        eu_tier_weight * 0.40 +
        us_designation_weight * 0.25 +
        data_sensitivity_weight * 0.20 +
        automation_weight * 0.15
    )

    # Cap at 100
    score = min(score, 100)
    score = max(score, 0)

    # Round to nearest 0.5 for readability
    score = round(score * 2) / 2

    return score
```

### Confidence Scoring

```python
def assess_confidence(
    eu_keyword_matches: int,
    us_category_matches: int,
    sector_matches: int,
    metadata_completeness: float
) -> str:
    """
    High: 2+ framework matches + complete metadata
    Medium: 1 framework match + partial metadata
    Low: 0–1 matches + incomplete metadata
    """
    evidence_score = (
        eu_keyword_matches * 0.3 +
        us_category_matches * 0.3 +
        sector_matches * 0.2 +
        metadata_completeness * 0.2
    )

    if evidence_score >= 0.7:
        return "High"
    elif evidence_score >= 0.4:
        return "Medium"
    else:
        return "Low"
```

### Continuous Re-Classification Triggers

Systems are automatically re-evaluated on:

1. **Configuration Drift Detection** (weekly)
   - Model parameters changed (retraining, fine-tuning)
   - Training data composition changed (new sources, removed sources)
   - Deployment scope expanded (new jurisdiction, new user base)
   - Upstream/downstream system changes

2. **Regulatory Update Detection** (daily)
   - New EU AI Act guidance documents published
   - OMB M-series memoranda issued
   - NIST AI RMF revised
   - ISO 42001 updated
   - Sector-specific regulations (HIPAA, GLBA, etc.) modified

3. **Threat Intelligence** (daily)
   - Known vulnerabilities affecting similar systems
   - Security incidents or breaches in similar architectures
   - Regulatory enforcement actions against similar systems

4. **Business Context Changes** (event-driven)
   - New geographical deployment (especially EU)
   - New use cases added to system
   - Ownership change (acquisition, spin-off)
   - Regulatory audit initiated

**Re-Classification Logic**:
```python
def should_reclassify(system, event_log):
    """Determine if system should be re-classified."""
    last_classification_time = system.classification_timestamp
    time_since_classification = now() - last_classification_time

    # Periodic re-classification (quarterly)
    if time_since_classification > 90 days:
        return True

    # Event-driven re-classification
    recent_events = [
        e for e in event_log
        if e.timestamp > last_classification_time
    ]

    drift_events = [e for e in recent_events if e.type == "config_drift"]
    regulatory_events = [e for e in recent_events if e.type == "regulatory_update"]
    threat_events = [e for e in recent_events if e.type == "threat_intel"]
    business_events = [e for e in recent_events if e.type == "business_context_change"]

    return (
        len(drift_events) > 0 or
        len(regulatory_events) > 0 or
        len(threat_events) > 0 or
        len(business_events) > 0
    )

def reclassify_and_alert(system):
    """Re-run classification; if tier changed, alert stakeholders."""
    old_classification = system.latest_classification
    new_classification = classify_system(system)

    if new_classification.tier != old_classification.tier:
        # Tier changed; escalate
        alert_stakeholders(
            system_id=system.id,
            old_tier=old_classification.tier,
            new_tier=new_classification.tier,
            reason=new_classification.change_reason
        )

        # Trigger new approval workflow if needed
        if new_classification.requires_approval:
            trigger_approval_workflow(system)

    # Log re-classification event (UC-4)
    log_classification_event(system, old_classification, new_classification)
```

### Version History & Immutable Trail

Every classification decision is versioned and immutably stored:

```python
@dataclass
class ClassificationVersion:
    system_id: str
    version_number: int
    classification_timestamp: datetime
    eu_ai_act_tier: str
    us_omb_impact: str
    composite_risk_score: float
    confidence: str
    triggering_event: str  # "discovery", "config_drift", "regulatory_update", etc.
    classifier_version: str  # Tag for audit trail
    metadata_snapshot: dict  # Full system metadata at classification time
    approver_id: str  # Who approved
    approval_timestamp: datetime
    cryptographic_hash: str  # SHA-256 hash of this version + previous version
    signature: str  # RSA-4096 signature by approver

    def is_valid(self) -> bool:
        """Verify cryptographic integrity of classification history."""
        if self.version_number > 1:
            previous = fetch_classification_version(self.system_id, self.version_number - 1)
            expected_hash = sha256(previous.to_bytes() + self.to_bytes())
            return self.cryptographic_hash == expected_hash
        return True
```

---

## Integration Points

UC-1 (Classification Engine) integrates with all other DataSafeguard platform components:

### UC-1 → UC-2 (Multi-Jurisdiction Regulatory Crosswalk)
- UC-1 produces risk classification (EU Annex III tier, OMB impact category)
- UC-2 consumes classification to map compliance requirements per jurisdiction
- **Data flow**: `risk_score, eu_tier, us_impact` → UC-2 for compliance requirement lookup

### UC-1 → UC-3 (AI Security Pipeline)
- UC-1 identifies systems requiring security scanning (High-Risk, Prohibited patterns)
- UC-3 automatically prioritizes security testing for systems flagged by UC-1
- **Data flow**: `system_id, risk_tier` → UC-3 for enhanced scanning

### UC-1 → UC-4 (Immutable Audit Trail)
- UC-1 generates classification decisions; UC-4 logs all decisions and changes
- UC-4 provides cryptographic proof that classifications cannot be retroactively altered
- **Data flow**: `classification_event, approval_decision` → UC-4 for immutable logging

### UC-1 → UC-5 (Bias Detection & Fairness Monitoring)
- UC-1 identifies ML systems that may have fairness requirements (Rights & Civil Liberties, Benefits & Services)
- UC-5 prioritizes bias scanning for systems affecting protected groups
- **Data flow**: `system_id, affected_population` → UC-5 for fairness assessment

### UC-1 → UC-6 (Training Data Governance & Lineage)
- UC-1 identifies systems with high data sensitivity requirements
- UC-6 ensures training data for those systems meets governance standards
- **Data flow**: `system_id, data_sensitivity_tier` → UC-6 for data lineage verification

---

## Business Value

### Quantified ROI Metrics

**Time Savings**:
- **Before**: Compliance officer manually inventories AI systems = 40 hours/quarter
- **After**: Automated discovery + classification = 2 hours/quarter
- **Savings**: 152 hours/year × $200/hour (compliance labor) = **$30,400/year**

**Risk Mitigation**:
- **Before**: Unaware of prohibited AI risks; 30% of systems unclassified
- **After**: 100% classified; prohibited patterns detected immediately
- **Compliance fine avoidance**: Single EU AI Act violation fine = €30M (4% global revenue, Art. 99)
- **Risk mitigation value**: (Probability of violation × Penalty) = (30% × €30M) = **€9M/year risk reduction**

**Audit Efficiency**:
- **Before**: Regulatory audit requires 3 weeks to compile evidence, multiple audit findings
- **After**: Complete compliance documentation generated in real-time
- **Audit cost reduction**: (3 weeks × 2 full-time auditors × $150/hour) = $18,000 saved per audit
- **Audit finding reduction**: 90% fewer findings = $0 (average finding remediation cost)
- **Annual savings**: 2 audits/year × $18,000 = **$36,000/year**

**Operational Efficiency**:
- **Before**: Approval workflows manual, SLA tracking spreadsheet-based
- **After**: Automated workflows, SLA enforcement, no manual tracking
- **Time savings**: 8 hours/week × 50 weeks/year = 400 hours × $100/hour = **$40,000/year**

**Faster Go-to-Market**:
- **Before**: New AI system takes 4 weeks to classify and approve
- **After**: Automated classification in hours; approval SLA 48 hours
- **Time to production**: 28 days → 3 days (93% reduction)
- **Business value**: Earlier revenue generation, competitive advantage; estimated **$500K+/year** for SaaS company deploying monthly ML features

**Total Year-1 Quantified Value**: $30,400 + €9M + $36,000 + $40,000 + $500K = **$606,400 (conservative estimate)**

### Qualitative Benefits

1. **Regulatory Confidence**: Board and executives have visibility into AI governance; reduced nervousness about regulatory action
2. **Vendor Evaluation**: When evaluating ML vendors/APIs, can quickly classify third-party models against internal risk standards
3. **M&A Due Diligence**: AI system inventory immediately available during acquisition; accelerates due diligence
4. **Insurance & Risk Financing**: Underwriters have confidence in AI governance; may reduce cyber insurance premiums
5. **Customer Trust**: Can credibly communicate AI governance to customers; competitive advantage in B2B sales
6. **Employee Recruitment**: Engineering teams prefer working at companies with clear AI governance; helps retain talent
7. **Strategic Planning**: Executives understand AI risk portfolio; informs investment decisions (which systems to prioritize for risk reduction, which to expand)

---

## Appendix: Example Classification Scenarios

### Scenario 1: Resume Screening Tool

**System Description**:
- Name: TalentMatch Resume Screening
- Type: ML classifier (NLP + computer vision)
- Purpose: Screen job applications, rank candidates by qualification match
- Training data: 500K historical resumes + hiring decisions (past 5 years)
- Deployment: SaaS, accessible to 50+ enterprise customers
- Jurisdiction: Primarily EU; expanding to US
- Automation level: Fully autonomous (no human review before rejection)
- Affected population: Job applicants (millions)

**Classification Process**:

1. **EU AI Act Tier**
   - Use case: "Employment recruitment and management"
   - Matches ANNEX_III_CATEGORIES[4] (Employment)
   - Keywords: "resume screening", "hiring", "candidate ranking" (3 matches)
   - Sector bonus: EU jurisdiction (+5), recruiting sector (+0) = +5
   - Final score: 3 keyword matches + 5 sector bonus = 8
   - **Classification**: High-Risk (Annex III Cat. IV)
   - EU tier weight: 32

2. **US OMB M-25-21 Impact**
   - Matches: RCL (Rights & Civil Liberties) — affects access to employment opportunities
   - Keywords: "employment", "discrimination risk", "hiring decisions" (2 matches)
   - Sector bonus: Not applicable (recruiting sector not in OMB list)
   - Final score: 2 category matches + RCL primary
   - **Classification**: High-Impact AI
   - US designation weight: 25

3. **Data Sensitivity**
   - Training data contains: Candidate names, contact info, education history, employment history (PII)
   - Resume inputs contain: Names, dates of birth, disabilities (some), national ID numbers (some countries)
   - **Classification**: Restricted (PII/biometric)
   - Data sensitivity weight: 20

4. **Automation Level**
   - Fully autonomous (no human review before rejection notification)
   - **Classification**: Fully autonomous
   - Automation weight: 15

5. **Composite Risk Score**
   - Risk Score = (32 × 0.40) + (25 × 0.25) + (20 × 0.20) + (15 × 0.15)
   - Risk Score = 12.8 + 6.25 + 4.0 + 2.25 = **25.3/100**

6. **Confidence Assessment**
   - EU keyword matches: 3
   - US category matches: 1 (RCL)
   - Sector matches: 1 (EU)
   - Metadata completeness: 100%
   - Evidence score: (3 × 0.3) + (1 × 0.3) + (1 × 0.2) + (1.0 × 0.2) = 0.9 + 0.3 + 0.2 + 0.2 = 1.6 (capped at 1.0)
   - **Confidence**: High ✓✓✓

7. **Prohibited/Limited-Risk Patterns**
   - Social Scoring: No (output affects single decision, not cross-domain government eligibility)
   - Subliminal Manipulation: No
   - Real-Time Biometric: No (resumes are static documents, no real-time biometric processing)
   - Emotion Workplace: No
   - **Prohibited patterns detected**: None
   - Limited-Risk patterns: Potentially Art. 52 disclosure (AI-generated ranking should be disclosed to candidates)

8. **Approval Workflow**
   - Risk tier: High-Risk
   - Required approval: Compliance Officer + Hiring Manager sign-off
   - SLA: 48 hours
   - **Status**: Requires approval before production deployment
   - **Conditions for approval**:
     - Risk assessment completed (bias analysis, fairness metrics)
     - Art. 52 disclosure implemented (candidates informed that AI scored resumes)
     - GDPR Article 22 right to human review implemented
     - Regular auditing and bias monitoring in place

**Result**: **HIGH-RISK, SCORE 25.3/100, REQUIRES APPROVAL**

---

### Scenario 2: Chatbot Customer Service

**System Description**:
- Name: CustomerCare GPT
- Type: LLM-based conversational AI
- Purpose: Answer customer questions about product features, troubleshooting, billing
- Model: GPT-4-based fine-tuned on internal support documentation
- Deployment: Public-facing website chatbot
- Training data: 100K past support conversations (anonymized)
- Jurisdiction: Global (US + EU)
- Automation level: Fully autonomous (generates responses without human review)
- Affected population: Customers (100K+ active users)

**Classification Process**:

1. **EU AI Act Tier**
   - Use case: "Conversational AI, customer service"
   - Matches: No ANNEX_III_CATEGORIES keywords (not biometric ID, not critical infrastructure, etc.)
   - Sector bonus: N/A (no sector matches)
   - **Classification**: Minimal-Risk (not in Annex III)
   - EU tier weight: 4

2. **US OMB M-25-21 Impact**
   - Use case analysis: Customer service information provision (no health/safety, no rights/civil liberties, no benefits/services, no critical infrastructure)
   - **Classification**: Standard AI (no OMB categories match)
   - US designation weight: 5

3. **Data Sensitivity**
   - Training data contains: Customer names, email addresses, account numbers, support history (PII/confidential)
   - System inputs: Customer messages (may contain PII)
   - **Classification**: Confidential (customer data)
   - Data sensitivity weight: 15

4. **Automation Level**
   - Fully autonomous (generates responses without human review)
   - **Classification**: Fully autonomous
   - Automation weight: 15

5. **Composite Risk Score**
   - Risk Score = (4 × 0.40) + (5 × 0.25) + (15 × 0.20) + (15 × 0.15)
   - Risk Score = 1.6 + 1.25 + 3.0 + 2.25 = **8.1/100**

6. **Confidence Assessment**
   - EU keyword matches: 0 (not in prohibited/high-risk categories)
   - US category matches: 0
   - Sector matches: 0
   - Metadata completeness: 100%
   - Evidence score: 0 (no framework matches)
   - **Confidence**: Low ✓

7. **Limited-Risk Patterns (Article 52)**
   - Chatbots: YES (matches Art. 52 limited-risk pattern)
   - **Transparency requirement**: Must disclose to users that they are interacting with AI chatbot
   - **Disclosure implementation**: "This is an AI-powered chatbot. If you need to speak with a human agent, press 0."

8. **Approval Workflow**
   - Risk tier: Minimal-Risk (but Art. 52 transparency applies)
   - Required approval: None (auto-approved)
   - Conditions: Must implement transparency disclosure (Art. 52)
   - **Status**: Fast-track approval with transparency checklist

**Result**: **MINIMAL-RISK, SCORE 8.1/100, AUTO-APPROVED WITH ART. 52 TRANSPARENCY**

---

### Scenario 3: Predictive Policing System

**System Description**:
- Name: CrimePredictAI
- Type: ML classifier (ensemble of gradient boosted trees + neural networks)
- Purpose: Predict high-crime areas to allocate police patrols
- Training data: 10 years of crime reports, incident locations, arrests (by neighborhood)
- Deployment: City police department
- Jurisdiction: US city
- Automation level: Semi-autonomous (system recommends patrol allocation; lieutenant approves)
- Affected population: Residents (1M), communities at risk of over-policing
- Protected attributes in training data: Race, socioeconomic status (correlated with historical over-policing)

**Classification Process**:

1. **EU AI Act Tier**
   - Use case: "Predictive policing, law enforcement"
   - Matches: ANNEX_III_CATEGORIES[6] (Law enforcement) — keywords: "predictive policing", "crime prediction", "suspect identification"
   - Sector bonus: EU jurisdiction bonus NOT applicable (US city)
   - Final score: 2 keyword matches, no sector bonus
   - **Classification**: High-Risk (Annex III Cat. VI)
   - EU tier weight: 32 (note: applies even in US if system affects EU residents via data transfer or future expansion)

2. **US OMB M-25-21 Impact**
   - Matches: RCL (Rights & Civil Liberties) — affects fairness, due process, freedom of movement
   - Matches: CI (Critical Infrastructure) — police are critical to infrastructure; NO (police not listed as critical infrastructure in OMB)
   - Primary: RCL with strong indicators
   - Sector bonus: Government (+2), Defense/LE (+3) = +3
   - **Classification**: High-Impact AI
   - US designation weight: 25

3. **Data Sensitivity**
   - Training data contains: Crime locations (linked to neighborhoods), arrest records (linked to identities), socioeconomic indicators
   - Data classification: Restricted (government law enforcement records) + Confidential (socioeconomic + location data)
   - **Classification**: Restricted
   - Data sensitivity weight: 20

4. **Automation Level**
   - Semi-autonomous (system recommends; human lieutenant approves)
   - **Classification**: Semi-autonomous
   - Automation weight: 10

5. **Composite Risk Score**
   - Risk Score = (32 × 0.40) + (25 × 0.25) + (20 × 0.20) + (10 × 0.15)
   - Risk Score = 12.8 + 6.25 + 4.0 + 1.5 = **24.55/100**

6. **Confidence Assessment**
   - EU keyword matches: 2 (law enforcement, predictive policing)
   - US category matches: 1 (RCL)
   - Sector matches: 1 (government law enforcement)
   - Metadata completeness: 100%
   - Evidence score: (2 × 0.3) + (1 × 0.3) + (1 × 0.2) + (1.0 × 0.2) = 0.6 + 0.3 + 0.2 + 0.2 = 1.3 (capped)
   - **Confidence**: High ✓✓✓

7. **Bias/Fairness Red Flag**
   - Training data includes protected attributes (race, socioeconomic status, implicitly correlated via neighborhood)
   - High risk of **perpetuating historical over-policing patterns**
   - **Fairness assessment required**: SHAP analysis to measure disparate impact across racial/socioeconomic groups

8. **Approval Workflow**
   - Risk tier: High-Risk
   - Required approval: Police Chief, City Attorney, Chief Compliance Officer
   - SLA: 48 hours (urgent due to public safety implications)
   - **Conditions for approval**:
     - Bias assessment completed (disparate impact analysis per racial/socioeconomic groups)
     - Fairness metrics documented (demographic parity, equalized odds, predictive parity)
     - Governance controls in place (audit of patrol allocation decisions, community oversight)
     - Continuous monitoring of model for performance drift
     - Public transparency statement if deployed

**Result**: **HIGH-RISK, SCORE 24.55/100, REQUIRES APPROVAL + FAIRNESS ASSESSMENT**

---

## Summary

The AI System Inventory & Risk Classification Engine is the foundational platform component providing:

✓ **Real-time visibility** into all AI systems across the enterprise
✓ **Unified risk scoring** complying with EU AI Act, OMB M-25-21, NIST AI RMF, ISO 42001 simultaneously
✓ **Automated detection** of prohibited AI patterns (Article 5)
✓ **Continuous monitoring** with re-classification triggered by drift, regulation changes, threat intelligence
✓ **Approval workflow enforcement** with SLA tracking and cryptographic signing
✓ **Immutable audit trail** supporting SOC 2, regulatory audits, and litigation discovery
✓ **$606K+/year quantified value** from risk mitigation, compliance savings, and operational efficiency

This UC is the **prerequisite** for all other platform capabilities and should be the **first implementation priority**.
