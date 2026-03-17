# UC-12: General-Purpose AI (GPAI) Model Compliance Dashboard

## Executive Summary

The General-Purpose AI (GPAI) Model Compliance Dashboard addresses a critical new regulatory reality: EU AI Act Articles 53 and 55 introduce a novel classification—"general-purpose AI" models—with specific compliance obligations for providers. Large language models like GPT-4, Claude, Llama, and open-source foundation models fall under this definition. If your organization builds, fine-tunes, or operates GPAI models, you have distinct legal obligations beyond standard high-risk AI system governance.

GPAI introduces new compliance challenges: you must identify systemic risks in your model, provide transparency about training data and copyright, implement model evaluation procedures, and maintain capability records showing the model's performance across diverse tasks. This UC operationalizes GPAI-specific governance, ensuring that foundation models deployed within or provided by your organization are compliant with EU AI Act Articles 53-55 and equivalent global regulations.

Chief Technology Officers, Legal teams, and Regulatory Affairs teams benefit most directly: GPAI compliance is separate from high-risk system compliance and requires different evidence, different risk assessments, and different disclosure obligations. This UC creates clarity: "these are our GPAI models, here's our compliance evidence, here's the transparency information we're providing to downstream deployers."

## What This Use Case Does

The GPAI Model Compliance Dashboard is a specialized governance system for foundation models and general-purpose AI systems. It extends the AI System Registry (UC-1) with GPAI-specific attributes, compliance workflows, and transparency reporting designed to meet EU AI Act Articles 53-55 and anticipated global GPAI regulations.

### Key Capabilities

- **EU AI Act Art. 53/55 GPAI Compliance Tracking**:
  - Registry of all GPAI models operated or provided by the organization
  - For each model: compliance status against Art. 53 (GPAI transparency) and Art. 55 (systemic risk) requirements
  - Documentation of which models fall under GPAI definition (trained on large amounts of data, performs variety of tasks) vs. standard high-risk systems
  - Version tracking: GPAI models often have multiple versions (v1.0, v1.5, v2.0); each version tracked separately

- **GPAI Model Registry with Capability Assessments**:
  - Model name, version, release date, training data summary, parameter count
  - Capability assessment: what can this model do well? (e.g., "strong at text generation, weaker at numerical reasoning")
  - Limitation documentation: where does model struggle? (e.g., "may produce hallucinations when knowledge is insufficient")
  - Appropriate use cases: what is this model designed for? (e.g., "general-purpose text understanding; not suitable for medical diagnosis without human review")
  - Inappropriate use cases: what should users avoid? (e.g., "do not use for autonomous weapons targeting without human override")

- **Systemic Risk Identification for GPAI with Systemic Risk Flag (Art. 55)**:
  - EU AI Act Art. 55 defines "systemic risk" as risk of significant harm at societal scale
  - Dashboard tracks:
    - Is this GPAI model deployed at massive scale (millions of users)?
    - Could it be misused for illegal purposes (disinformation, fraud, illegal content generation)?
    - Could it amplify bias or discrimination at scale?
    - Could it threaten cybersecurity, critical infrastructure, or democratic processes?
  - Models flagged as systemic risk (e.g., billion-parameter language models deployed to billions of users) have enhanced compliance obligations:
    - Compute threshold monitoring: GPAI with 10^25 FLOP of compute (EU guidance) requires systemic risk flagging
    - Enhanced testing for misuse potential
    - Incident reporting to EU authorities
    - Ongoing systemic risk monitoring and mitigation

- **Technical Documentation Requirements (Annex XI)**:
  - EU AI Act Annex XI specifies what GPAI technical documentation must contain:
    - Model architecture and training methodology
    - Training data: sources, quality metrics, filtering applied
    - Evaluation methodology: how was model tested? On what benchmarks?
    - Performance across tasks: capability profile
    - Limitations and failure modes documented
    - Safety testing: adversarial robustness, jailbreak resistance, etc.
    - Deployment considerations: how should deployers use this model safely?
  - This UC generates or imports required documentation for each GPAI model version

- **Copyright Compliance and Training Data Transparency**:
  - EU AI Act Art. 53 requires disclosure of training data, including copyright-protected works
  - This UC tracks:
    - Training data sources: datasets used (e.g., CommonCrawl, Books, etc.)
    - Copyright compliance: how were copyrighted works handled?
      - Were creators notified and consent obtained? (EU: creators have a right to know if works used)
      - Are opt-out mechanisms provided for content creators?
      - Is the model trained on copyrighted material without consent? (legally gray but increasingly regulated)
    - Transparency reporting: publicly disclosed information about training data
    - Creator compensation (if applicable): mechanism for creator benefit-sharing

- **Downstream Deployer Notification System**:
  - GPAI providers must inform downstream users (deployers using the model in applications) about:
    - Model capabilities and limitations
    - Known risks and mitigation strategies
    - Appropriate use cases and prohibited uses
    - Performance data: capability benchmarks, evaluation results
  - This UC generates and tracks:
    - Deployer documentation: automatically generated user guide for downstream deployers
    - Incident reporting: if downstream deployer reports harmful incident involving GPAI model, notification system alerts GPAI provider
    - Update notifications: when GPAI model is updated, downstream deployers are notified of changes/improvements

- **Compute Threshold Monitoring (10^25 FLOP)**:
  - EU guidance indicates GPAI models trained with > 10^25 FLOP (floating-point operations) are presumed to pose systemic risk
  - This UC tracks training compute for each model:
    - If compute threshold exceeded → model automatically flagged for systemic risk obligations
    - Enhanced testing, monitoring, and incident reporting required
    - Dashboard alerts when any GPAI model approaches or exceeds threshold

- **Model Evaluation Benchmarks Tracking**:
  - Industry-standard benchmarks for GPAI capability assessment:
    - Natural language understanding: MMLU, HellaSwag, LAMBADA
    - Reasoning: ARC, BoolQ, MultiRC
    - Domain-specific: MedQA (medical), LegalBench (legal), etc.
  - This UC tracks:
    - Which benchmarks used to evaluate each GPAI model
    - Benchmark scores: model's performance on each benchmark
    - Benchmark evolution: tracking if performance improves/degrades across model versions
    - Competitive analysis: how does our GPAI perform vs. industry benchmarks and competing models?

- **Incident Reporting Pipeline for GPAI-Specific Issues**:
  - Unlike high-risk systems, GPAI incidents have specific regulatory implications:
    - Disinformation: GPAI model used to generate false information at scale
    - Illegal content: GPAI generates illegal content (CSAM, weapons design, etc.)
    - Jailbreaks: vulnerability discovered allowing misuse or harmful outputs
    - Systemic harm: evidence of bias, discrimination, or other societal-scale harm
  - Incident workflow:
    - Internal incident report filed (what happened, impact, root cause)
    - Assessment: is this a systemic risk incident? (requires regulatory reporting)
    - Mitigation: what's being done to fix? (e.g., release model update, disable feature, add safeguards)
    - Regulatory reporting: incidents involving systemic risk are reported to authorities (EU: reported to relevant authorities; may trigger formal investigation)
    - Transparency: decisions about whether/how to disclose to users

- **Transparency Obligations for GPAI Providers**:
  - GPAI providers must publicly disclose:
    - Model name and version
    - Intended use and appropriate use cases
    - Key performance characteristics
    - Known limitations and risks
    - Minimum hardware requirements for deployment
    - Training data summary (sources, amount, quality filtering)
    - Mitigation measures for identified risks
  - This UC maintains:
    - Public model card (auto-generated or manually authored) meeting Annex XI requirements
    - Transparency portal: public-facing documentation and benchmark results
    - Changelog: version history with improvements/changes documented
    - Risk disclosure: publicly documented risks, limitations, and mitigation strategies

### How It Works — Step by Step

1. **Model Registration**: When a GPAI model is developed or acquired, it's registered in UC-12:
   - Model name, version, release date
   - Organization's role: provider (we built/fine-tuned it), deployer (we're using a third-party model), or both
   - Model type: language model, multimodal model, code generation, etc.
   - Estimated deployment scale: number of users expected, deployment geography

2. **GPAI Classification**: System determines if model meets GPAI definition:
   - Is model trained on large amount of data? (multiple TBs, diverse domains)
   - Does model perform variety of tasks? (tested on multiple benchmarks, general-purpose capability)
   - Has model been released or is it intended for deployment? (not a research prototype)
   - Classification: GPAI Yes/No
   - If GPAI, then Articles 53-55 obligations apply

3. **Systemic Risk Assessment**: For GPAI models, assess systemic risk:
   - Scale: How many users will have access?
     - < 1M users: not systemic
     - 1-100M users: potentially systemic
     - > 100M users: presumed systemic
   - Misuse potential: Could this model be misused for illegal activities?
     - Disinformation at scale: model could generate convincing false information
     - Illegal content: model could generate illegal content (weapons, drugs, CSAM, etc.)
     - Fraud: model could impersonate individuals or generate fraudulent documents
     - Score: LOW, MEDIUM, HIGH
   - Bias/discrimination risk: Could model perpetuate systemic bias?
     - Demographic parity gaps in performance (e.g., 92% accuracy for one demographic, 78% for another)
     - Hiring bias, lending bias, criminal justice bias
     - Score: LOW, MEDIUM, HIGH
   - Critical infrastructure/democratic risk: Could model harm critical systems or democratic processes?
     - Autonomous weapons, cyberattacks, election interference
     - Score: LOW, MEDIUM, HIGH
   - Compute threshold: Was model trained with > 10^25 FLOP?
     - If yes: flagged as presumed systemic risk

4. **Systemic Risk Determination**:
   - If scale = HIGH, OR misuse potential = HIGH, OR bias risk = HIGH, OR compute > 10^25 FLOP:
     - Model flagged: "Systemic Risk = TRUE"
     - Enhanced obligations activated (see step 7)
   - Otherwise: "Systemic Risk = FALSE"; standard GPAI obligations apply

5. **Capability Assessment and Documentation**:
   - Capability profile created: what can model do well?
     - Benchmark scores documented (MMLU: 92%, ARC: 88%, etc.)
     - Natural language understanding: YES, strong
     - Code generation: YES, strong
     - Medical knowledge: YES, moderate (not suitable for clinical diagnosis)
     - Legal knowledge: PARTIAL (general legal concepts but not authoritative)
   - Limitation documentation: where does model struggle?
     - Numerical reasoning: weak
     - Long-context understanding (> 100K tokens): degraded performance
     - Real-time information: training data cutoff means no knowledge of current events
     - Hallucinations: may produce plausible-sounding but false information
   - Appropriate use cases documented:
     - "Suitable for general-purpose text understanding, summarization, Q&A"
     - "NOT suitable for autonomous decision-making in high-stakes domains (hiring, lending, criminal justice) without human review"
     - "NOT suitable for medical, legal, or financial advice without expert verification"
   - Annex XI documentation auto-generated or manually authored

6. **Training Data & Copyright Compliance**:
   - Training data sources documented:
     - CommonCrawl: 60% of training
     - Books (copyrighted and public domain): 20%
     - Academic papers: 10%
     - Proprietary data: 10%
   - Copyright handling:
     - Mechanism 1: All copyrighted works removed during data cleaning → "Model trained on copyright-free data only"
     - Mechanism 2: Copyrighted works included but creators can opt-out → "Creators can request data removal from future versions"
     - Mechanism 3: Copyrighted works included without consent → documented as potential liability (increasingly problematic legally)
   - Transparency disclosure: public disclosure of training data summary
   - Creator compensation (if applicable): mechanism tracked (e.g., creator benefit fund, licensing fees paid)

7. **Enhanced Obligations for Systemic Risk Models**:
   - Systemic risk monitoring: ongoing evaluation for systemic harm
     - Quarterly evaluation on abuse/misuse benchmarks
     - Adversarial robustness testing: can model be jailbroken?
     - Societal impact assessment: has model been misused? (red team, user feedback)
   - Incident reporting: systemic risk incidents reported to authorities
     - Evidence of large-scale disinformation using model → report to relevant authorities
     - Criminal use of model detected → law enforcement notification
     - Significant bias discovered → regulatory notification
   - Remediation: rapid model updates or feature disablement if systemic harm identified
   - Transparency: public disclosure of systemic risks and mitigation measures

8. **Model Evaluation and Benchmarking**:
   - Benchmark suite defined: MMLU, ARC, LAMBADA, HellaSwag, domain-specific benchmarks
   - Model evaluated on full benchmark suite:
     - Scores recorded: MMLU 92%, ARC 88%, LAMBADA 95%, HellaSwag 84%
     - Benchmark results publicly disclosed in model card
   - Comparative analysis: how does model compare to:
     - Previous version: "v2.0 shows +3 points on MMLU vs. v1.5"
     - Competitive models: "Model X scores 92% on MMLU, Industry average 88%"
   - Trend analysis: performance improvement trajectory tracked across versions

9. **Downstream Deployer Communication**:
   - Model Card generated (Google format or custom variant):
     - Model overview: name, version, intended use
     - Capabilities and limitations: what model is good/bad at
     - Training data: sources, size, quality
     - Performance: benchmark scores, demographic breakdown
     - Recommendations for use: appropriate use cases, required disclaimers
     - Contact information: support, incident reporting
   - User guide for downstream deployers: implementation guidance
   - Incident reporting channel: downstream users can report incidents, which are escalated to GPAI provider

10. **Incident Response & Reporting**:
    - Systemic risk incident reported (e.g., model used to generate election disinformation)
    - Assessment: is this truly a systemic incident? (affected millions, potential for major harm?)
    - If yes: report to regulatory authorities (EU: relevant authorities per Art. 55)
    - Mitigation plan: what's being done? (model update, feature disable, additional safeguards)
    - Transparency decision: will this be publicly disclosed? (depends on jurisdiction and severity)
    - Follow-up: long-term monitoring to prevent recurrence

11. **Continuous Monitoring**:
    - Quarterly systemic risk assessment: is risk level changing?
    - Model performance: are benchmark scores stable? (declining performance may indicate drift or new vulnerability)
    - Incident tracking: are there patterns in reported incidents?
    - Regulatory landscape: are new GPAI regulations emerging? (compliance obligations may evolve)

## Compliance Benefit

**Regulatory Compliance for GPAI Providers**: If your organization provides GPAI models (even internally to other departments), EU AI Act Articles 53-55 compliance is mandatory for EU users. This UC ensures documentation, risk assessment, and transparency obligations are met.

**Systemic Risk Management**: Systemic risk is a new regulatory concept; this UC operationalizes systematic identification and mitigation of systemic harms from GPAI models.

**Legal Defense**: Documentation of training data, copyright compliance, and systemic risk assessment provides legal defense against copyright infringement claims and regulatory enforcement.

**Transparency Accountability**: Public disclosure of model capabilities, limitations, and risks demonstrates good-faith transparency, which courts and regulators view favorably.

**Incident Accountability**: Complete incident history, systemic risk assessments, and remediation records demonstrate you're taking systemic harm seriously, not ignoring problems.

### Regulatory Coverage

| Regulatory Framework | Specific Articles/Sections | GPAI Dashboard Coverage |
|---|---|---|
| **EU AI Act** | Article 53 (GPAI transparency requirements) | Transparency obligations tracking; model card generation; disclosure documentation |
| EU AI Act | Article 54 (GPAI assessment) | Capability assessment, benchmark testing, limitation documentation |
| EU AI Act | Article 55 (systemic risk for GPAI) | Systemic risk identification, enhanced obligations for high-risk GPAI, compute monitoring |
| EU AI Act | Annex XI (GPAI technical documentation) | Auto-generates required technical documentation |
| **EU AI Act** | Article 60 (GPAI incident reporting) | Systemic risk incident reporting pipeline to authorities |
| **GDPR** | Articles 13-14 (transparency) | Training data transparency aligns with GDPR transparency obligations |
| **Copyright Directives** | EU Copyright Directive Article 17 | Training data copyright compliance and transparency tracked |
| **ISO 42001** | Clause 8.1 (planning for GPAI) | GPAI capability and risk assessment integrated into ISO governance |
| **NIST AI RMF** | MEASURE (GPAI evaluation) | Benchmark testing and performance documentation contribute to MEASURE function |
| **US FTC Guidelines** | AI Transparency & Accountability | GPAI transparency disclosures align with FTC AI guidance on deceptive practices |

### Risk Reduction

- **Regulatory Enforcement Risk**: GPAI non-compliance with Articles 53-55 can result in fines up to 6% of revenue. Compliance UC eliminates this risk.
- **Copyright Liability**: Training GPAI on copyrighted data without proper handling creates litigation risk. This UC tracks copyright compliance and documents safeguards.
- **Systemic Harm Blindness**: Without systemic risk assessment, GPAI providers don't know if their models pose societal-scale risks. Monitoring and incident reporting catch systemic harms before they scale.
- **Transparency Violations**: Failing to disclose model limitations, training data, or risks violates Articles 53-54. This UC ensures disclosures are complete and accurate.
- **Incident Response Delays**: Without a formal incident pipeline, systemic incidents go unreported. Incident workflow ensures regulatory reporting happens on schedule.

### Audit Readiness

**For EU Regulators (DMA, BEREC, relevant authorities)**:
- Provide GPAI compliance report showing:
  - Models classified as GPAI or non-GPAI with justification
  - Systemic risk assessments for all GPAI models
  - Compute threshold documentation (10^25 FLOP tracking)
  - Technical documentation (Annex XI)
  - Incident reporting history for systemic risk incidents
  - Transparency disclosures (model cards, training data documentation)

**For Copyright/IP Litigation**:
- Document training data sources and copyright handling mechanism
- Show due diligence: how were copyrighted works handled? Removed? Opt-out provided?
- Demonstrate transparency: disclosures made to users about training data

**For Board/Investor Risk Reporting**:
- GPAI portfolio dashboard: which models pose systemic risk, which are compliant
- Regulatory exposure: potential fines for non-compliance ($10-100M range)
- Incident history: systemic incidents reported and remediated
- Outlook: compliance status improving, stable, or declining

## Technical Deep Dive: Systemic Risk Scoring Engine

Systemic risk is quantified using a multi-dimensional framework aggregating scale, misuse potential, bias risk, and critical infrastructure risk.

### Systemic Risk Calculation

```
Systemic_Risk_Score = (Scale × 0.30) + (Misuse_Potential × 0.30) +
                      (Bias_Risk × 0.20) + (Infrastructure_Risk × 0.20)

Scale (0-100):
  User base < 1M: 20 points
  User base 1-10M: 40 points
  User base 10-100M: 70 points
  User base > 100M: 100 points

Misuse_Potential (0-100):
  Model design makes misuse unlikely: 10 points
  Model could be misused but safeguards prevent abuse: 40 points
  Model can generate illegal content despite safeguards: 70 points
  Model enables large-scale illegal activity (disinformation, weapons, fraud): 100 points

Bias_Risk (0-100):
  No identified demographic disparities: 10 points
  < 5% performance gap across demographics: 30 points
  5-15% performance gap: 60 points
  > 15% performance gap or documented harmful bias: 100 points

Infrastructure_Risk (0-100):
  Model poses no risk to critical systems: 10 points
  Model could be used for cyberattacks (requires expertise): 40 points
  Model enables autonomous weapons or critical infrastructure attacks: 100 points

Systemic_Risk_Threshold: 60+
  Score 60-79: MODERATE systemic risk (enhanced monitoring required)
  Score 80-100: HIGH systemic risk (enhanced testing, incident reporting, remediation required)
  Compute > 10^25 FLOP: presumed HIGH systemic risk regardless of score
```

## Integration Points

- **UC-1 (AI System Registry)**: GPAI models registered in main registry with GPAI-specific attributes; systemic risk flag feeds back to UC-1 risk classification.
- **UC-5 (Fairness & Bias Assessment)**: Bias metrics for GPAI models inform Bias_Risk component of systemic risk score.
- **UC-8 (Compliance Documentation)**: Technical documentation (Annex XI) and model cards auto-generated for GPAI models.
- **UC-9 (Model Monitoring)**: GPAI model performance monitored for degradation; benchmark scores tracked.
- **UC-11 (NIST AI RMF)**: GPAI capability assessment and evaluation contribute to NIST MEASURE function evidence.
- **Public Model Registry** (HuggingFace, Model Hub): GPAI models can be published with compliance metadata for transparency.
- **Incident Management System**: Systemic risk incidents logged and escalated; workflow integrates with incident tracking.

## Business Value

**Regulatory Confidence**: GPAI compliance with Articles 53-55 provides certainty that organization's GPAI models are legally defensible. Avoids regulatory enforcement and fines.

**IP Protection**: Copyright compliance documentation and transparency reduce litigation risk from content creators claiming copyright infringement.

**Competitive Advantage**: GPAI models with documented safety, fairness, and transparency can be marketed to risk-averse customers ("fully EU AI Act compliant").

**Incident Resilience**: Systemic risk monitoring and incident reporting reduce probability that GPAI model is misused at scale without detection. Minimizes reputational damage.

**Stakeholder Confidence**: Transparent disclosure of model capabilities, limitations, and risks builds trust with downstream deployers and end users.

**Quantified Metrics**:
- GPAI compliance time: < 2 weeks per model (vs. 3-4 months for manual assessment)
- Systemic risk identification: 100% of high-scale GPAI models assessed (vs. 40% without systematic process)
- Incident detection time: 1-2 weeks (from incident occurrence to regulatory report) vs. 2-3 months without formal pipeline
- Benchmark evaluation: 8 hours per model (vs. 40 hours for manual benchmark testing)
- Copyright compliance documentation: 4-6 hours per model (vs. 20-30 hours for legal review)
- Regulatory fine risk: reduced from $10-100M (non-compliance) to ~$0 (proven compliance)
