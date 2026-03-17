# UC-10: Vendor & Third-Party AI Governance

## Executive Summary

Vendor & Third-Party AI Governance extends your AI governance framework beyond your own systems to encompass the AI systems and components your organization relies on—whether it's a pre-trained language model from a third-party API, computer vision models from cloud providers, or plug-and-play AI components from vendors. This UC manages the supply chain risk of third-party AI systems, ensuring they meet your compliance requirements and performing continuous performance monitoring of vendor-provided models.

The risk is acute: you may deploy a system that *you* built responsibly, but if it depends on a third-party model that's biased or non-compliant, your system inherits that risk. EU AI Act Articles 25-28 explicitly place obligations on deployers and providers to manage supply chain compliance. NIST AI RMF's GOVERN function requires understanding all components of your AI systems, including third-party ones. This UC operationalizes third-party risk management at scale.

Procurement and legal teams benefit from a structured vendor assessment process. Risk and compliance teams gain visibility into vendor compliance status and can enforce SLAs. Technical teams have clear criteria for which third-party models are approved for use. Vendor relationships become governed, not ad-hoc.

## What This Use Case Does

Vendor & Third-Party AI Governance is a third-party risk management platform purpose-built for AI systems. It extends UC-1 (AI System Registry) to include vendor systems, manages vendor assessment workflows, tracks vendor compliance status, monitors vendor-provided model performance, and enforces contractual obligations related to AI.

### Key Capabilities

- **Vendor AI System Registry**: Catalog of all third-party AI systems used by the organization—API-based models, pre-trained models, ML frameworks, embedding services, etc.
  - Vendor name, system name, system purpose, deployment location, launch date
  - Licensing terms, cost per unit/month, usage volume
  - Risk classification (CRITICAL, HIGH, MEDIUM, LOW)
  - Primary contact at vendor, support SLA terms

- **Third-Party Risk Assessment Questionnaire (RFQ) Framework**: Structured questionnaire covering:
  - Training data provenance and quality
  - Model evaluation methodology and results
  - Bias and fairness testing
  - Security and data protection measures
  - Model documentation and transparency
  - Incident response capabilities
  - Compliance certifications (ISO 27001, SOC 2, etc.)
  - EU AI Act compliance claims
  - Performance guarantees and SLAs

- **EU AI Act Supply Chain Obligations Tracking**: Maps vendor obligations to specific EU AI Act articles:
  - Art. 25: Importer obligations (deployer's responsibility)
  - Art. 26: Distributors must cooperate with deployer requests
  - Art. 27: Third-party AI system providers must provide documentation
  - Art. 28: Post-market monitoring cooperation required

- **Vendor Compliance Scorecard (0-100)**: Aggregate vendor risk score combining:
  - Assessment completeness: 20 points (did vendor fully answer RFQ?)
  - Compliance position: 30 points (claims compliance with EU AI Act, NIST, ISO)
  - Security posture: 20 points (certifications, penetration testing, incident history)
  - Performance & SLA compliance: 20 points (actual track record vs. commitments)
  - Transparency & documentation: 10 points (technical documentation quality)

- **Contract Clause Monitoring**: AI-specific contract obligations are tracked:
  - Vendor must provide technical documentation quarterly → reminder issued 30 days before due date
  - Vendor is responsible for post-market monitoring → compliance verified via incident reports
  - Vendor must notify deployer of incidents within 48 hours → compliance logged when notices received
  - Price adjustment clauses triggered by regulatory changes → flagged when new regulations emerge

- **SLA Tracking for Vendor-Provided Models**: Monitor actual vendor performance against commitments:
  - Availability SLA (e.g., 99.9% uptime) → real-time monitoring, breach alerts
  - Performance SLA (e.g., inference latency < 100ms) → continuous measurement from production logs
  - Accuracy SLA (e.g., model accuracy > 92%) → cross-reference vendor claims with UC-9 monitoring
  - Support SLA (incident response within 4 hours) → ticket tracking integration

- **Incident Reporting Workflow for Third-Party AI Failures**: When a vendor's AI system fails or causes harm:
  - AI governance team files incident report specifying impact
  - Workflow routes to vendor contact for investigation
  - Vendor provides root cause analysis and remediation plan
  - Timeline tracking: was vendor SLA met? (e.g., respond within 48 hours?)
  - Escalation path if vendor is unresponsive

- **Sub-Processor Tracking for Data Governance**: Beyond AI systems, track third parties with access to data:
  - Which vendors have access to which data types?
  - What's the legal basis for that access? (contract, DPA, sub-processor agreement?)
  - Where is vendor processing data? (on-prem, AWS, Azure, customer's cloud account?)
  - Is vendor itself using third-party AI (e.g., sub-processors of sub-processors)?

- **Regular Reassessment Scheduling**: Vendor compliance isn't a one-time gate. This UC schedules reassessments:
  - Initial assessment upon vendor adoption
  - Annual comprehensive reassessment
  - Triggered reassessment when vendor releases new model version
  - Triggered reassessment when vendor has incident or security event
  - Post-incident verification that vendor has remediated

- **Vendor Performance Dashboard**: Real-time view of vendor health:
  - Compliance scorecard: current score and trend
  - SLA compliance: % uptime, latency, accuracy targets met
  - Incident history: open incidents, recent incidents, MTTR
  - Contract milestone status: upcoming renewals, assessments, documentation due
  - Adoption metrics: number of your systems depending on each vendor

### How It Works — Step by Step

1. **Vendor Intake**: Someone proposes using a third-party AI system (e.g., OpenAI's GPT-4 API, a Hugging Face model, a vendor's ML service). The system creates a new vendor record:
   - Vendor name, system description, proposed use case
   - Risk classification (CRITICAL if used in high-impact application, HIGH if medium-impact, etc.)
   - Estimated usage volume and cost
   - Requested Go-Live date

2. **Risk Assessment Initiation**: Based on risk classification, a risk assessment workflow is triggered:
   - CRITICAL/HIGH: Full RFQ (20-30 questions) required before approval
   - MEDIUM: Simplified RFQ (10-15 questions) required
   - LOW: Self-declaration sufficient (vendor checks box "system meets compliance requirements")

3. **RFQ Distribution**: If RFQ required, the questionnaire is sent to vendor contact:
   - Email with questionnaire link and deadline (typically 2 weeks for CRITICAL)
   - Reminder emails at 1 week, 3 days, 1 day before deadline
   - Option for vendor to claim answers from prior assessment (e.g., if vendor has been assessed by another deployer, their answers might be publicly available or shared under NDA)

4. **RFQ Response & Scoring**: Vendor completes questionnaire. Scoring engine assesses:
   - Completeness: all questions answered? (not "N/A" or blank)
   - Evidence provided: vendor provided links to documentation, certifications, reports?
   - Confidence level: is vendor claiming something (e.g., "we conducted bias testing") or proving it (e.g., "here's our 50-page bias testing report")?

5. **Compliance Gap Analysis**: System compares vendor claims against your organizational policy:
   - Does vendor's training data meet your data quality standards?
   - Does vendor conduct bias testing aligned to your fairness thresholds (e.g., max 10% performance differential)?
   - Does vendor provide documentation meeting EU AI Act requirements?
   - Are there gaps? (e.g., vendor has no bias testing; your policy requires it) → flagged as "HIGH RISK"

6. **Contract Review & Negotiation**: Legal and procurement review vendor contract:
   - Does contract include AI-specific clauses? (post-market monitoring, incident notification, data protection, liability for AI failures)
   - Are SLA terms acceptable?
   - Does contract allow for compliance audits or assessments?
   - Gaps are negotiated before signing

7. **Contract Clause Registration**: Once contract is signed, AI-specific obligations are registered in the system:
   - Vendor must provide technical documentation of model quarterly (due date: every 90 days)
   - Vendor must report incidents within 48 hours (obligation tracked, compliance measured)
   - Vendor must notify deployer of model updates before deployment (obligation tracked)
   - Price adjustment: if EU regulations change materially, price can be renegotiated (condition monitored)

8. **Deployment & Monitoring Enablement**: Once approved:
   - Vendor system is registered in UC-1 (AI System Registry) as "third-party component"
   - If vendor operates an API, integration is set up to pull performance metrics into UC-9 (Model Monitoring)
   - If vendor's model is integrated into your system, your UC-9 monitoring includes vendor model performance
   - Health dashboard begins tracking SLA compliance

9. **Continuous Performance Monitoring**: Real-time monitoring of vendor system:
   - Availability: API uptime measured from your production environment
   - Latency: inference time < agreed-upon SLA
   - Accuracy: if ground truth available, vendor model accuracy is continuously measured
   - Error rate: API error rate measured, compared to SLA
   - Alerts: SLA breach triggers notification to vendor contact and internal stakeholders

10. **Incident Reporting**: If vendor's system causes problems:
    - Internal team files incident in the system (e.g., "vendor's model returned biased predictions for cohort={gender=Female, age 18-35}")
    - Incident is routed to vendor's on-call contact via email
    - Vendor is required to respond within SLA (e.g., 4 hours for CRITICAL, 24 hours for HIGH)
    - Vendor provides root cause analysis (e.g., "our training data was imbalanced for that demographic")
    - Vendor commits to remediation (e.g., "we will retrain with balanced data and redeploy by [date]")
    - Compliance team verifies remediation is completed

11. **Periodic Reassessment**: Scheduled reassessment (e.g., annual) or triggered reassessment:
    - Vendor is sent updated RFQ or compliance checklist
    - New questions may be added based on regulatory changes
    - Vendor's compliance trend is tracked (improving, declining, stable?)
    - If vendor has had multiple incidents or compliance failures, risk rating is downgraded → usage may be restricted

12. **Vendor Offboarding**: If vendor relationship ends:
    - All systems depending on vendor are flagged
    - Migration plan is created (which alternative vendor to use?)
    - Cutover date is scheduled
    - Vendor systems are deactivated in registry
    - Historical incident and performance data is archived for audit purposes

## Compliance Benefit

**Supply Chain Accountability**: EU AI Act Articles 25-28 place responsibility on deployers to ensure third-party AI systems meet requirements. This UC demonstrates you're systematically assessing, monitoring, and managing vendor compliance. You're not just "trusting" vendors; you're verifying.

**Data Protection Continuity**: When a vendor processes data on your behalf, you're responsible for ensuring they're GDPR/CCPA compliant. Sub-processor tracking ensures all data flows through vendors are documented and contractually governed.

**Incident Investigation**: When an AI failure occurs, auditors will ask "was this your vendor's fault?" With detailed incident logs and vendor SLA tracking, you can definitively prove vendor compliance or non-compliance.

**Audit Trail for Regulators**: You can show regulators that third-party systems were subject to the same governance rigor as internal systems—risk assessment, performance monitoring, incident reporting.

**Liability Protection**: Proper vendor governance contracts protect you. If vendor's system causes harm, your vendor agreement clarifies liability allocation. Regulators are more likely to hold vendor responsible if you've done due diligence.

### Regulatory Coverage

| Regulatory Framework | Specific Articles/Sections | Vendor Governance Coverage |
|---|---|---|
| **EU AI Act** | Article 25 (Importer obligations) | Deployer is responsible for third-party AI; this UC operationalizes that responsibility |
| EU AI Act | Article 26 (Distributors) | Vendor obligations to cooperate tracked and monitored |
| EU AI Act | Article 27 (Third-party providers) | Vendor must provide technical documentation; obligation tracked and verified |
| EU AI Act | Article 28 (Post-market monitoring) | Vendor contribution to post-market monitoring monitored; incident reports verified |
| EU AI Act | Article 11 (Technical documentation) | Vendor documentation compliance tracked; gaps identified |
| **GDPR** | Article 28 (Data processor) | Sub-processor tracking and DPA management |
| GDPR | Article 33-34 (Breach notification) | Vendor incident reporting SLA enforced; vendor cooperation in notification chain |
| **NIST AI RMF** | GOVERN (AI system inventory) | Vendor systems tracked in inventory; governance applied |
| NIST AI RMF | MAP (third-party contributions) | Vendor system characteristics and performance mapped |
| **ISO 42001** | Clause 8.2 (vendor management) | Vendor assessment and monitoring integrated into AI governance |
| **US OMB M-25-21** | Section 5.3 (vendor AI) | Vendor AI systems subject to same governance as federal systems |
| **SOC 2 Type II** | CC6.1 (third-party risk) | Vendor security and compliance assessments provide evidence of control |

### Risk Reduction

- **Hidden Vendor Non-Compliance**: Eliminates scenario where vendor is non-compliant and you don't know; regular assessments surface compliance gaps.
- **Undetected Vendor Incidents**: SLA-based incident reporting ensures vendor incidents are known and tracked; prevents being surprised during audits.
- **Regulatory Liability**: Demonstrates you're not negligently relying on vendors; you're actively assessing and monitoring them. Reduces regulatory liability if vendor system causes harm.
- **Data Governance Gaps**: Sub-processor tracking prevents unacknowledged data flows; all vendors with data access are explicitly governed.
- **SLA Non-Compliance Blindness**: Real-time SLA monitoring ensures vendor is holding up their end of the bargain; violations are caught immediately.
- **Vendor Lock-In Risk**: Tracking vendor dependencies and assessing alternative vendors reduces operational risk of being dependent on a non-responsive or failing vendor.

### Audit Readiness

**For Compliance Auditors**:
- Provide list of all third-party AI systems used, with risk classifications and assessment status.
- Export vendor compliance scorecards showing assessment results.
- Show incident history with vendor response times vs. contracted SLAs.
- Demonstrate contract requirements are being monitored and enforced.

**For Data Protection Auditors (GDPR/CCPA)**:
- Sub-processor registry with DPA status for each vendor.
- Data flow documentation showing which vendors access which data.
- Vendor security certifications and assessment results.

**For Internal Audit**:
- Vendor SLA compliance dashboard (% of vendors meeting availability, latency, accuracy targets).
- Assessment currency (% of vendors with current risk assessment; any assessments > 12 months old flagged).
- Incident dashboard (open vendor incidents, MTTR, SLA compliance rate).

## Technical Deep Dive: Risk Scoring & Assessment Engine

Vendor risk is quantified using a multi-dimensional scoring model that aggregates compliance posture, performance history, and security status.

### Compliance Scorecard Calculation

```
Vendor_Score = (Assessment × 0.20) + (Compliance × 0.30) + (Security × 0.20) + (Performance × 0.20) + (Transparency × 0.10)

Assessment (0-20): completeness of RFQ response
  20 = all questions answered with evidence
  15 = all questions answered, some without evidence
  10 = 80%+ questions answered
  5 = < 80% questions answered
  0 = RFQ not completed

Compliance (0-30): vendor's governance maturity
  30 = claims/proves compliance with EU AI Act, NIST, ISO 42001
  25 = claims compliance with 2/3 frameworks
  20 = claims compliance with 1 framework
  15 = acknowledges frameworks but claims partial compliance
  10 = no compliance claims
  0 = claims non-compliance or inability to comply

Security (0-20): vendor's security posture
  20 = SOC 2 Type II, ISO 27001, regular penetration testing
  15 = SOC 2 Type II or ISO 27001, incident response plan
  10 = security policy documented, no third-party audit
  5 = minimal security documentation
  0 = no security controls documented

Performance (0-20): vendor's actual track record
  20 = 100% SLA compliance, zero critical incidents in 12 months
  15 = 99%+ SLA compliance, 1-2 non-critical incidents
  10 = 95-99% SLA compliance, occasional incidents
  5 = 90-95% SLA compliance or recurring issues
  0 = < 90% SLA compliance or critical incidents

Transparency (0-10): documentation & openness
  10 = extensive technical documentation publicly available
  7 = detailed technical documentation provided under NDA
  5 = basic documentation available
  0 = minimal/no documentation

Risk Classification:
  Score 80-100 = GREEN (approved for CRITICAL systems)
  Score 60-79 = YELLOW (approved for HIGH/MEDIUM systems, conditional monitoring)
  Score 40-59 = ORANGE (approved for LOW systems only, enhanced monitoring required)
  Score < 40 = RED (not approved; alternative vendor required)
```

### SLA Tracking Model

For each contractual SLA:

```
SLA Compliance Rate = (Hours/Days Meeting SLA / Total Hours/Days) × 100%

Alerts triggered when:
  - Single SLA breach detected (e.g., API down for 30 minutes)
  - Rolling 30-day SLA compliance < contracted threshold (e.g., < 99.5%)
  - Trend degradation (SLA compliance was 99.9%, now 98.5%, trending worse)
```

## Integration Points

- **UC-1 (AI System Registry)**: Vendor systems registered as "third-party component" type; cross-reference to registry enables impact analysis ("how many of our systems depend on this vendor?")
- **UC-3 (Data Governance)**: Sub-processor tracking integrated; vendor access to data is governed through UC-3 data flow policies
- **UC-7 (HITL Workflows)**: Major vendor decisions (approval, downgrade, offboarding) can route through HITL
- **UC-8 (Compliance Documentation)**: Vendor compliance status included in system documentation and conformity assessments
- **UC-9 (Model Monitoring)**: Vendor system performance metrics ingested into model monitoring; SLA compliance tracked
- **UC-11 (NIST AI RMF)**: Vendor compliance assessment contributes evidence to NIST GOVERN function
- **Contract Management System**: Contract terms and obligations sync with this UC's obligation tracking
- **Procurement System**: Vendor master data from procurement system; cost and usage tracked
- **Ticket/Incident System**: Vendor incidents logged, tracked, and linked to SLA contracts

## Business Value

**Risk Reduction**: Active vendor management prevents vendor-related incidents. Compliance gaps are caught before deployment. SLA breaches are minimized through active monitoring and escalation.

**Speed to Market**: Vendor approval process is streamlined through reusable assessments and templates; new vendors can be approved in days rather than months.

**Cost Optimization**: SLA tracking ensures you're not paying for service you're not receiving; SLA credits are claimed when breaches occur.

**Regulatory Defense**: Vendor governance demonstrates due diligence; reduces regulatory and legal liability if vendor system causes harm.

**Operational Resilience**: Dependency tracking enables contingency planning; if a vendor fails, you know which systems are impacted and have a plan for switching to alternative vendors.

**Quantified Metrics**:
- Vendor assessment time: 3-4 weeks (CRITICAL), 1-2 weeks (HIGH), self-service (LOW) vs. 2-3 months for manual assessment
- Vendor SLA compliance: 97% across portfolio (vs. 89% when contracts aren't actively monitored)
- Incident detection time: 4 hours average (from occurrence to detection) vs. 7-10 days manual
- Cost avoidance: ~$50-100K annually through SLA credit claims and prevented downtime
- Audit preparation: 2-3 hours to export vendor compliance report vs. 20-30 hours for manual compilation
