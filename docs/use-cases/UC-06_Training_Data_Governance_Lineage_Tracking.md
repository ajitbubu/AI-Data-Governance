# UC-6: Training Data Governance & Lineage Tracking

## Executive Summary

The Training Data Governance & Lineage Tracking system is the platform's data provenance layer, capturing complete ownership, licensing, PII, and consent metadata for every dataset used in AI model training. This UC builds a Neo4j-based knowledge graph mapping dataset → model → deployment dependencies, enabling rapid impact analysis when regulations change, data subjects request erasure (GDPR Article 17), or license compliance is questioned.

Every organization training AI systems faces data governance gaps: training datasets sourced from multiple origins with unclear licensing; PII presence unknown or unreviewed; consent status ambiguous; and data quality undocumented. This creates legal and operational risk: GDPR fines for missing data inventory, copyright disputes when training on unlicensed data, and inability to respond to data subject deletion requests within the mandatory 30-day window.

The Data Governance Engine solves this via automated dataset registration (metadata extraction, license detection, PII scanning) plus lineage graphing showing how datasets flow through data processing pipelines into models and ultimately to deployments. When a regulator asks "is this training data GDPR-compliant?" the system produces a detailed compliance report in minutes.

This UC benefits Data Officers managing GDPR/CCPA compliance; General Counsels evaluating licensing risk; Chief Data Officers ensuring data quality; and Compliance Officers proving due diligence on third-party datasets.

---

## What This Use Case Does

The Data Governance Engine performs four continuous operations:

### Dataset Registration & Metadata Extraction

Every dataset used for training is registered with comprehensive metadata:

```python
class DatasetRegistration:
    def __init__(self, dataset_id, dataset_name):
        self.dataset_id = dataset_id
        self.dataset_name = dataset_name
        self.metadata = {
            # Identification
            "source": None,           # S3 bucket, API, vendor, internal DB
            "source_system": None,    # SAP, Salesforce, Snowflake, Hugging Face, etc.
            "collection_date": None,  # When data was collected
            "registration_date": now(),

            # Data Composition
            "record_count": None,     # Total rows/records
            "feature_count": None,    # Total columns/features
            "feature_types": None,    # Numeric, categorical, text, image, etc.
            "data_types": None,       # CSV, JSON, Parquet, HDF5, TFRecord

            # PII & Sensitive Data
            "pii_detected": False,    # Any PII present?
            "pii_entities": [],       # Types detected: names, emails, SSN, etc.
            "pii_columns": [],        # Specific columns containing PII
            "phi_detected": False,    # Health information?
            "sensitive_data_types": [],  # Financial, government IDs, biometric, etc.

            # Consent & Licensing
            "consent_status": None,   # Explicit, Opt-In, Opt-Out, Assumed, Unknown
            "consent_basis": None,    # GDPR Article 6 basis: contract, legal obligation, vital interest, public task, legitimate interest
            "license": None,          # Dataset license: MIT, Apache 2.0, CC-BY, Commercial, etc.
            "license_url": None,      # Link to license terms
            "copyright_holder": None, # Entity owning copyright
            "licensing_verified": False,
            "licensing_verified_by": None,
            "licensing_verified_date": None,

            # Data Quality
            "quality_score": None,    # 0-100 score based on completeness, accuracy, consistency
            "missing_data_pct": None, # % of missing values
            "duplicate_pct": None,    # % of exact duplicates
            "outlier_pct": None,      # % of statistical outliers
            "freshness": None,        # Days since last update

            # Governance
            "data_owner": None,       # Person responsible
            "retention_policy": None, # How long data retained
            "retention_deadline": None,
            "approved": False,        # Data approved for training?
            "approved_by": None,
            "approved_date": None,
            "restrictions": []        # Usage restrictions
        }
```

**Automatic Metadata Extraction**:

```python
def extract_dataset_metadata(dataset_path, sample_size=10000):
    """
    Automatically extract metadata from dataset.
    """
    # 1. Load dataset sample
    df = load_data_sample(dataset_path, sample_size)

    # 2. Extract structure
    metadata = {
        "record_count": len(df),
        "feature_count": len(df.columns),
        "feature_types": {col: str(df[col].dtype) for col in df.columns},
        "data_types": infer_data_format(dataset_path)
    }

    # 3. Detect PII using Microsoft Presidio
    from presidio_analyzer import AnalyzerEngine
    analyzer = AnalyzerEngine()

    pii_entities = {}
    for column in df.columns:
        column_text = df[column].astype(str).str.cat(sep=" ")
        findings = analyzer.analyze(column_text)
        if findings:
            pii_entities[column] = [f.entity_type for f in findings]

    metadata["pii_detected"] = len(pii_entities) > 0
    metadata["pii_entities"] = list(set([entity for entities in pii_entities.values() for entity in entities]))
    metadata["pii_columns"] = list(pii_entities.keys())

    # 4. Detect sensitive data (financial, government IDs)
    sensitive_patterns = {
        "credit_card": r"^\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}$",
        "ssn": r"^\d{3}-\d{2}-\d{4}$",
        "iban": r"^[A-Z]{2}\d{2}[A-Z0-9]+$"
    }

    sensitive_data_detected = {}
    for col in df.columns:
        for sensitive_type, pattern in sensitive_patterns.items():
            matches = df[col].astype(str).str.match(pattern).sum()
            if matches > 0:
                sensitive_data_detected[col] = sensitive_type

    metadata["sensitive_data_types"] = list(set(sensitive_data_detected.values()))

    # 5. Calculate data quality metrics
    metadata["missing_data_pct"] = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
    metadata["duplicate_pct"] = (len(df) - len(df.drop_duplicates())) / len(df) * 100

    return metadata
```

**PII Handling**:
- If PII detected: dataset marked as "Restricted" (requires explicit governance review)
- Requires documented legitimate basis (GDPR Article 6) for processing
- Requires data protection impact assessment (DPIA)
- May trigger automatic masking before training (if policy dictates)

**License Detection**:

```python
def detect_dataset_license(dataset_source):
    """
    Automatically detect dataset license from common sources.
    """
    licenses = {}

    # Check Hugging Face
    if "huggingface.co" in dataset_source:
        license_type = fetch_huggingface_license(dataset_source)
        licenses["source"] = "Hugging Face"
        licenses["license"] = license_type

    # Check GitHub
    elif "github.com" in dataset_source:
        license_type = fetch_github_license(dataset_source)
        licenses["source"] = "GitHub"
        licenses["license"] = license_type

    # Check Kaggle
    elif "kaggle.com" in dataset_source:
        license_type = fetch_kaggle_license(dataset_source)
        licenses["source"] = "Kaggle"
        licenses["license"] = license_type

    # Check UCI ML Repository
    elif "archive.ics.uci.edu" in dataset_source:
        licenses["source"] = "UCI ML"
        licenses["license"] = "CC0 (Public Domain)"  # UCI datasets typically public domain

    # For custom/internal datasets
    else:
        licenses["source"] = "Internal"
        licenses["license"] = None  # Must be manually specified
        licenses["action_required"] = "License must be specified by data owner"

    return licenses
```

**Approval Workflow**:

```
Dataset Registration Workflow:

Step 1: Metadata extracted
├─ Record count: 100,000
├─ PII detected: Names, emails, dates of birth
├─ License: Unknown
├─ Quality score: 85%
└─ Status: PENDING REVIEW

Step 2: Automated checks
├─ PII present → Requires GDPR Article 6 basis ✓ (consent documented)
├─ License unknown → Requires legal review ✗ (MISSING)
└─ Quality score 85% → Acceptable (threshold: 80%)

Step 3: Approval required
├─ Chief Data Officer (PII dataset)
├─ General Counsel (licensing verification)
└─ Action required: Confirm license terms or obtain from data owner

Step 4: Post-approval
├─ Dataset approved for training
├─ Lineage tracking begins
└─ Status: APPROVED
```

### Data Lineage Tracking (Neo4j Graph)

Complete lineage graph capturing dataset → model → deployment dependencies:

```
Neo4j Graph Structure:

(Dataset {
  id: "dataset_001",
  name: "500K Resumes 2018-2023",
  pii_present: true,
  license: "MIT"
})
  │
  ├─ PROCESSED_BY → (Pipeline {id: "pipeline_001", name: "Resume Cleaner v1"})
  │                   │
  │                   └─ OUTPUTS → (Dataset {id: "dataset_002", name: "Cleaned Resumes"})
  │                                  │
  │                                  ├─ USED_FOR_TRAINING → (Model {id: "model_001", name: "ResumeMatcher v2"})
  │                                  │                        │
  │                                  │                        ├─ EVALUATED_ON → (Dataset {id: "dataset_003", name: "Test Set"})
  │                                  │                        │
  │                                  │                        └─ DEPLOYED_TO → (Deployment {
  │                                  │                                           id: "deploy_001",
  │                                  │                                           name: "TalentMatch SaaS",
  │                                  │                                           jurisdiction: ["EU", "US"],
  │                                  │                                           users: 10000
  │                                  │                                         })
  │
  └─ DELETED_BY_SUBJECT → (DeletionRequest {
                             subject_id: "john.doe@example.com",
                             request_date: "2024-03-01",
                             deadline: "2024-03-31",
                             status: "PENDING"
                           })
```

**Lineage Query Examples**:

```cypher
// Query 1: All datasets used to train a specific model
MATCH (dataset:Dataset) -[:USED_FOR_TRAINING]-> (model:Model {name: "Resume Screener v2"})
RETURN dataset.name, dataset.pii_present, dataset.license

// Query 2: All deployments affected by a dataset (for impact analysis)
MATCH (dataset:Dataset {id: "dataset_001"})
      -[:USED_FOR_TRAINING]-> (model:Model)
      -[:DEPLOYED_TO]-> (deployment:Deployment)
RETURN deployment.name, deployment.jurisdiction, deployment.users

// Query 3: All models/deployments affected by deletion request
MATCH (deletionRequest:DeletionRequest {subject_id: "john.doe@example.com"})
      <-[:DELETED_BY_SUBJECT]- (dataset:Dataset)
      -[:USED_FOR_TRAINING]-> (model:Model)
      -[:DEPLOYED_TO]-> (deployment:Deployment)
RETURN model.name, deployment.name, model.retraining_required

// Query 4: Data provenance (complete chain from original source to deployment)
MATCH (originalDataset:Dataset {id: "dataset_001"})
      -[:PROCESSED_BY]-> (pipe:Pipeline)
      -[:OUTPUTS]-> (cleanedDataset:Dataset)
      -[:USED_FOR_TRAINING]-> (model:Model)
      -[:DEPLOYED_TO]-> (deployment:Deployment)
RETURN [originalDataset, pipe, cleanedDataset, model, deployment]
```

### GDPR Article 17 Right-to-Erasure Impact Analysis

Automated analysis of impact when data subjects request deletion:

**Workflow**:

```python
def analyze_deletion_request(subject_id, dataset_ids_containing_subject):
    """
    Analyze impact of deletion request (GDPR Article 17).
    """
    # 1. Find all datasets affected
    affected_datasets = query_graph(
        f"MATCH (d:Dataset) WHERE d.id IN {dataset_ids_containing_subject} RETURN d"
    )

    # 2. Find all models trained on affected datasets
    affected_models = query_graph(
        f"MATCH (d:Dataset) -[:USED_FOR_TRAINING]-> (m:Model) WHERE d.id IN {dataset_ids_containing_subject} RETURN m"
    )

    # 3. Find all deployments using affected models
    affected_deployments = query_graph(
        f"MATCH (m:Model) -[:DEPLOYED_TO]-> (dep:Deployment) WHERE m.id IN {[m.id for m in affected_models]} RETURN dep"
    )

    # 4. Determine remediation required
    remediation = {
        "datasets_to_delete": len(affected_datasets),
        "models_to_retrain": len(affected_models),
        "deployments_affected": len(affected_deployments),
        "users_notified": sum([d.users for d in affected_deployments]),
        "compliance_deadline": subject_deletion_request_date + 30 days,
        "recommended_action": "Retrain all affected models without subject's data"
    }

    return remediation
```

**Example Impact Report**:

```
=== GDPR ARTICLE 17 DELETION REQUEST IMPACT ANALYSIS ===
Subject ID: john.doe@example.com
Request Date: 2024-03-01
Compliance Deadline: 2024-03-31 (30 days)

=== AFFECTED DATASETS ===
Count: 3 datasets

1. Resume Dataset (500K records)
   ├─ Subject in dataset: YES (1 record)
   ├─ PII of subject retained: Name, email, phone, salary history
   └─ Deletion complexity: Low (single record removal)

2. Test Set (10K records)
   ├─ Subject in dataset: YES (1 record)
   ├─ Deletion complexity: Low

3. Validation Set (5K records)
   ├─ Subject in dataset: NO
   └─ No deletion required

=== AFFECTED MODELS ===
Count: 2 models

1. ResumeMatcher v2
   ├─ Trained on: Resume Dataset + Test Set
   ├─ Training date: 2024-01-15
   ├─ Retrain required: YES (subject's data was in training set)
   ├─ Estimated retrain time: 2 weeks
   └─ Retrain deadline: 2024-03-31

2. ResumeMatcher v1 (legacy)
   ├─ Trained on: Resume Dataset (old version, no Test Set)
   ├─ Retrain required: NO (superseded by v2; decommissioned 2024-02-01)
   └─ No action required

=== AFFECTED DEPLOYMENTS ===
Count: 1 deployment affected

1. TalentMatch SaaS
   ├─ Model version: ResumeMatcher v2 (AFFECTED)
   ├─ Regions deployed: EU, US
   ├─ Active users: 10,000
   ├─ Predictions made with subject's data in training: ~2,000 candidates compared against subject's profile
   └─ Notification required: YES (10,000 users impacted)

=== COMPLIANCE ACTIONS REQUIRED ===

IMMEDIATE (within 3 days):
1. Delete subject's record from Resume Dataset
2. Delete subject's record from Test Set
3. Notify TalentMatch SaaS product team (model retraining needed)

SHORT-TERM (within 2 weeks):
1. Retrain ResumeMatcher v2 model WITHOUT subject's data
2. Run fairness analysis (ensure retraining didn't introduce bias)
3. Deploy retrained model to production
4. Validate model performance vs. previous version

FINAL (within 30 days):
1. Verify deletion completed across all systems
2. Document deletion in audit trail (UC-4)
3. Respond to data subject with deletion confirmation

=== RISK ASSESSMENT ===
Compliance Risk: LOW
└─ Reason: Clear lineage enables rapid remediation within 30-day deadline

Cost Impact: MEDIUM
├─ Model retraining: $5K (engineering time)
├─ Validation and testing: $3K
└─ Total: $8K

=== RECOMMENDATION ===
APPROVE deletion request and proceed with remediation plan above.
Deadline is achievable with current team resources.
```

### Copyright & Licensing Compliance for Generative AI

Special handling for generative AI training data (text, images) where copyright is critical:

```python
def verify_generative_ai_training_compliance(dataset_info):
    """
    Verify copyright and licensing compliance for generative AI training data.
    """
    compliance_checks = {}

    # 1. Verify license allows AI training
    allowed_for_ai_training = [
        "CC0 (Public Domain)",
        "CC-BY",
        "CC-BY-SA",
        "MIT",
        "Apache 2.0",
        "GPL",
        "Custom (Verified)
    ]

    if dataset_info["license"] not in allowed_for_ai_training:
        compliance_checks["license_issue"] = {
            "status": "VIOLATION",
            "reason": f"License {dataset_info['license']} does not permit AI training",
            "action_required": "Obtain license modification or alternate dataset"
        }

    # 2. Verify no copyright restrictions
    copyright_issues = []
    for data_sample in dataset_info["samples"]:
        copyright_status = check_copyright_status(data_sample)
        if copyright_status == "copyrighted":
            copyright_issues.append(data_sample)

    if copyright_issues:
        compliance_checks["copyright_issue"] = {
            "status": "VIOLATION",
            "reason": f"{len(copyright_issues)} copyrighted works detected",
            "action_required": "Remove copyrighted works before training"
        }

    # 3. Verify attribution requirements met
    if "CC-BY" in dataset_info["license"]:
        compliance_checks["attribution"] = {
            "status": "REQUIRED",
            "action_required": "Include attribution in model documentation"
        }

    # 4. Verify no personal data without consent
    if dataset_info["pii_present"] and dataset_info["consent_status"] != "Explicit":
        compliance_checks["pii_issue"] = {
            "status": "VIOLATION",
            "reason": "PII present without explicit consent",
            "action_required": "Remove PII or obtain explicit consent"
        }

    return compliance_checks
```

### Training Data Version Control & Reproducibility

All training data versions tracked to enable model reproducibility:

```
Training Data Version Control

Model: ResumeMatcher v2
Training Date: 2024-01-15
Training Data Version Commit: data-v2.1

Components:
├─ Resume Dataset
│  └─ Version: dataset_001_v2.1
│     ├─ Commit: abc123def456
│     ├─ Record count: 500,000
│     ├─ Timestamp: 2024-01-14T18:00:00Z
│     └─ Checksum: SHA256(abc123...)
├─ Feature Engineering Pipeline
│  └─ Version: pipeline_001_v1.3
│     ├─ Commit: ghi789jkl012
│     ├─ Processing steps: 12
│     └─ Timestamp: 2024-01-14T19:00:00Z
└─ Test Set
   └─ Version: test_set_v1.2
      ├─ Commit: mno345pqr678
      ├─ Record count: 10,000
      └─ Timestamp: 2024-01-14T20:00:00Z

Reproducibility: FULL
- Exact same data versions can be reconstructed from Git commit abc123def456
- Model retraining from these exact data versions would produce identical results
```

---

## Key Capabilities

- **Dataset registration with automatic metadata extraction** (record count, feature types, quality scores)
- **PII/PHI detection** (using Microsoft Presidio; flagged for governance review)
- **License detection & verification** (automatic detection from Hugging Face, GitHub, Kaggle)
- **Consent tracking** (GDPR Article 6 basis documented per dataset)
- **Data quality scoring** (0-100 based on completeness, accuracy, consistency)
- **Data lineage graphing** (Neo4j: dataset → pipeline → model → deployment)
- **GDPR Article 17 impact analysis** (automated calculation of deletion request consequences)
- **Copyright compliance for generative AI** (special handling for text/image data)
- **Training data version control** (Git-based version history; reproducibility enabled)
- **Proxy attribute detection** (PII may be inferred even if not explicitly present)
- **Data retention policy enforcement** (TTL management; automatic deletion when retention expires)
- **Audit-ready data provenance** (complete chain from source through training to deployment)
- **EU AI Act Article 10 compliance** (data quality, bias mitigation, documentation)

---

## How It Works — Step by Step

### Dataset Registration Workflow

**Step 1: Dataset Discovery**

System periodically scans data sources for new datasets:

```python
def discover_datasets():
    """
    Scan data sources for new datasets.
    """
    discovered = []

    # S3 buckets
    for bucket in CONFIGURED_S3_BUCKETS:
        objects = list_s3_objects(bucket)
        for obj in objects:
            if obj.last_modified > last_scan_time:
                discovered.append({
                    "source": f"s3://{bucket}/{obj.key}",
                    "type": infer_format(obj.key),
                    "size": obj.size,
                    "last_modified": obj.last_modified
                })

    # Databases
    for db_connection in CONFIGURED_DATABASES:
        tables = list_tables(db_connection)
        for table in tables:
            if table.last_modified > last_scan_time:
                discovered.append({
                    "source": f"{db_connection.name}.{table.name}",
                    "type": "SQL",
                    "record_count": query_record_count(db_connection, table),
                    "last_modified": table.last_modified
                })

    # Hugging Face
    for user in HUGGINGFACE_USERS:
        datasets = fetch_huggingface_datasets(user)
        for dataset in datasets:
            if dataset.updated_at > last_scan_time:
                discovered.append({
                    "source": f"huggingface://{user}/{dataset.name}",
                    "type": "Dataset Card",
                    "size": dataset.size,
                    "last_modified": dataset.updated_at
                })

    return discovered
```

**Step 2: Metadata Extraction**

For each discovered dataset, metadata automatically extracted:

```
S3://ml-datasets/resume-data/2024-01/resumes.parquet

Extraction Results:
├─ Format: Parquet
├─ Record count: 500,000
├─ Feature count: 47
├─ Size: 2.3 GB
├─ Data types:
│  ├─ 15 numeric (id, salary, years_experience)
│  ├─ 25 categorical (education, industry, job_title)
│  └─ 7 text (resume_text, cover_letter)
├─ Quality metrics:
│  ├─ Completeness: 98.5% (1.5% missing values)
│  ├─ Uniqueness: 99.8% (0.2% exact duplicates)
│  ├─ Validity: 97.2% (data types match schema)
│  └─ Overall score: 95% (EXCELLENT)
├─ Sensitive data detected:
│  ├─ PII: YES
│  │  ├─ Names: 500,000 (every record)
│  │  ├─ Emails: 487,000
│  │  ├─ Phone numbers: 412,000
│  │  └─ Dates of birth: 500,000
│  ├─ Sensitive data: YES
│  │  ├─ Salary information: 500,000 (sensitive financial data)
│  │  └─ Previous employer: 500,000
│  └─ Classification: RESTRICTED (requires approval)
└─ Status: PENDING REVIEW
```

**Step 3: License Detection**

```
License Detection:

For: huggingface.co/datasets/user/resume-data

Fetch Hugging Face Dataset Card:
├─ License field: "CC-BY"
├─ License URL: https://creativecommons.org/licenses/by/4.0/
├─ Terms:
│  ├─ Usage: Allowed (including commercial AI training)
│  ├─ Modification: Allowed
│  ├─ Distribution: Allowed
│  ├─ Attribution: REQUIRED
│  └─ Sublicensing: Allowed
├─ Compliance: VERIFIED ✓
└─ Status: APPROVED for AI training
```

**Step 4: Approval Workflow**

Datasets with PII, licensing questions, or quality concerns routed to approval:

```
Dataset Registration Approval Workflow:

Dataset: resume-data
Classification: RESTRICTED (PII present, needs approval)

Approvers Required:
├─ Chief Data Officer (PII oversight)
├─ General Counsel (license verification)
└─ Data Governance Committee (usage approval)

Approval Status:

☐ Chief Data Officer
  └─ Review needed: PII assessment
     ├─ PII fields: Names, emails, salaries, dates of birth
     ├─ Consent basis: Internal recruitment (Article 6(1)(b): Employment contract)
     └─ Approval: [Pending review]

☐ General Counsel
  └─ Review needed: License compliance
     ├─ License: CC-BY-4.0 (allows AI training)
     ├─ Attribution: Required in model documentation
     └─ Approval: [Pending review]

☐ Data Governance Committee
  └─ Review needed: Overall usage approval
     ├─ Quality score: 95% (EXCELLENT)
     ├─ Data retention policy: 7 years (matches GDPR)
     └─ Approval: [Pending review]

Once all 3 approvals granted:
├─ Dataset approved for training
├─ Lineage tracking enabled
└─ Status: APPROVED
```

### Lineage Impact Analysis Workflow

**Query: How is this dataset used?**

```python
def analyze_dataset_impact(dataset_id):
    """
    Show all models and deployments using a dataset.
    """
    # Query lineage graph
    models = query_graph(f"""
        MATCH (d:Dataset {{id: '{dataset_id}'}})
              -[:USED_FOR_TRAINING]-> (m:Model)
        RETURN m.id, m.name, m.training_date, m.production_status
    """)

    deployments = query_graph(f"""
        MATCH (d:Dataset {{id: '{dataset_id}'}})
              -[:USED_FOR_TRAINING]-> (m:Model)
              -[:DEPLOYED_TO]-> (dep:Deployment)
        RETURN dep.id, dep.name, dep.jurisdiction, dep.users, dep.status
    """)

    impact_report = {
        "dataset": dataset_id,
        "models_trained": models,
        "deployments_using_models": deployments,
        "total_users_affected": sum([d.users for d in deployments]),
        "jurisdictions_affected": list(set([j for d in deployments for j in d.jurisdiction]))
    }

    return impact_report
```

**Example Impact Report**:
```
Dataset: resume-data (500K records)

Models Trained:
├─ ResumeMatcher v2 (training date: 2024-01-15)
│  └─ Status: PRODUCTION
├─ ResumeMatcher v1 (training date: 2023-10-01)
│  └─ Status: ARCHIVED (replaced by v2)
└─ Resume-Bias-Detector (training date: 2024-02-20)
   └─ Status: PRODUCTION

Deployments Using Models:
├─ TalentMatch SaaS (using ResumeMatcher v2)
│  ├─ Users: 10,000
│  └─ Jurisdictions: EU, US
├─ Internal Recruiting Tool (using ResumeMatcher v2 + Resume-Bias-Detector)
│  ├─ Users: 500
│  └─ Jurisdictions: Global
└─ Resume API (using ResumeMatcher v1) [LEGACY]
   ├─ Users: 2,000
   └─ Jurisdictions: North America

Total Users Affected: 12,500
Jurisdictions: EU, US, Global
```

### GDPR Article 17 Deletion Request Workflow

**Step 1: Request Received**

Data subject John Doe requests deletion of his data:

```
Request Details:
├─ Subject ID: john.doe@example.com
├─ Request Date: 2024-03-01
├─ Request Method: Email to privacy@acme.com
├─ Deadline: 2024-03-31 (30-day GDPR deadline)
└─ Status: PROCESSING
```

**Step 2: Impact Analysis**

System analyzes all datasets, models, deployments affected:

```python
def process_deletion_request(subject_id, request_date):
    """
    Process GDPR Article 17 deletion request.
    """
    # 1. Find all datasets containing subject
    affected_datasets = query_graph(f"""
        MATCH (d:Dataset)
        WHERE any(record in d.records WHERE record.subject_id = '{subject_id}')
        RETURN d.id, d.name
    """)

    # 2. Find all models trained on affected datasets
    affected_models = query_graph(f"""
        MATCH (d:Dataset) -[:USED_FOR_TRAINING]-> (m:Model)
        WHERE d.id IN {[d.id for d in affected_datasets]}
        RETURN m.id, m.name, m.status
    """)

    # 3. Find all deployments
    affected_deployments = query_graph(f"""
        MATCH (m:Model) -[:DEPLOYED_TO]-> (dep:Deployment)
        WHERE m.id IN {[m.id for m in affected_models]}
        RETURN dep.id, dep.name, dep.users, dep.jurisdiction
    """)

    # 4. Create deletion plan
    plan = {
        "datasets_to_clean": affected_datasets,
        "models_to_retrain": [m for m in affected_models if m.status == "PRODUCTION"],
        "deployments_affected": affected_deployments,
        "deadline": request_date + timedelta(days=30),
        "steps": [
            "1. Delete subject's records from all affected datasets",
            "2. Retrain all production models (retrain_without_subject=True)",
            "3. Validate retrained models (fairness, performance)",
            "4. Deploy retrained models to production",
            "5. Verify deletion across all systems",
            "6. Respond to data subject with deletion confirmation"
        ]
    }

    return plan
```

**Step 3: Remediation Execution**

```
Deletion Request Remediation Plan

Subject: john.doe@example.com
Deadline: 2024-03-31 (29 days remaining)

=== DATASETS TO DELETE FROM ===

1. resume-data (S3://ml-datasets/resume-data/)
   ├─ Records to delete: 1 (out of 500,000)
   ├─ Deletion method: Filter WHERE subject_id != 'john.doe@example.com'
   ├─ Expected time: <1 hour
   └─ Verification: Checksum before/after

2. resume-test-set (S3://ml-datasets/test-sets/)
   ├─ Records to delete: 1 (out of 10,000)
   ├─ Expected time: <30 min
   └─ Status: READY

=== MODELS TO RETRAIN ===

1. ResumeMatcher v2 (PRODUCTION)
   ├─ Training data affected: YES (subject was in training set)
   ├─ Retrain effort: 2 weeks (model training + validation)
   ├─ Retrain command: `train_model(model_id='v2', exclude_subject='john.doe@example.com')`
   └─ Deadline: 2024-03-17

2. Resume-Bias-Detector (PRODUCTION)
   ├─ Training data affected: YES
   ├─ Retrain effort: 1 week
   └─ Deadline: 2024-03-24

3. ResumeMatcher v1 (ARCHIVED, no action required)

=== DEPLOYMENTS AFFECTED ===

1. TalentMatch SaaS
   ├─ Current model: ResumeMatcher v2 (will be retrained)
   ├─ Deployment date for retrained model: 2024-03-24
   ├─ User impact: 10,000 users will have retrained model
   └─ Notification: Product team notified, deployment window scheduled

2. Internal Recruiting Tool
   ├─ Current models: ResumeMatcher v2 + Resume-Bias-Detector (both retrained)
   ├─ Deployment date: 2024-03-24
   └─ User impact: 500 internal users

=== VERIFICATION CHECKLIST ===

[ ] Delete subject's records from resume-data
[ ] Delete subject's records from resume-test-set
[ ] Verify deletions via checksum comparison
[ ] Retrain ResumeMatcher v2 (exclude john.doe@example.com)
[ ] Run fairness analysis on retrained v2 (ensure no bias introduced)
[ ] Validate retrained v2 performance vs. previous version
[ ] Retrain Resume-Bias-Detector
[ ] Run fairness analysis on retrained detector
[ ] Deploy retrained models to production (ResumeMatcher v2 + Bias Detector)
[ ] Update lineage graph (new model versions linked to cleaned datasets)
[ ] Verify deletion in audit trail (UC-4)
[ ] Send deletion confirmation to john.doe@example.com
[ ] Complete by: 2024-03-31

=== TIMELINE ===

2024-03-01: Request received
2024-03-02: Data deletion (1 day)
2024-03-03: Start retraining (1st model)
2024-03-17: Retraining complete (v2)
2024-03-18: Start retraining (2nd model)
2024-03-24: Retraining complete, deployment ready
2024-03-24: Deploy retrained models
2024-03-25: Verification complete
2024-03-31: Confirm to data subject (deadline)

Compliance: ON TRACK ✓
```

---

## Compliance Benefit

The Training Data Governance Engine enables compliance with critical data regulation:

### Before DataSafeguard

- **No data inventory**: Don't know what datasets exist or what data they contain
- **PII unknown**: Train on data with PII without realizing it; GDPR exposure
- **License ambiguous**: Use third-party data without verifying license compliance; copyright disputes
- **Deletion impossible**: Data subject requests deletion; can't find data within 30 days; GDPR fine
- **No lineage**: When security incident occurs, can't rapidly determine which models/deployments affected

**Result**: GDPR fines, copyright disputes, regulatory audit failures, slow incident response.

### With DataSafeguard UC-6

- **Complete data inventory**: All datasets registered with metadata
- **PII identified**: Automatic detection; flagged for governance review
- **License verified**: Automatic license detection + legal verification
- **Rapid deletion**: Lineage graph enables impact analysis in minutes; remediation plan generated automatically
- **Incident response**: Lineage graph enables rapid impact analysis (which models use this data? which deployments affected?)

**Result**: Full GDPR/copyright compliance; rapid deletion responses; effective incident response.

---

## Regulatory Coverage

| Control | GDPR | HIPAA | CCPA | EU AI Act | Copyright Law |
|---------|------|-------|------|-----------|--------------|
| **Data Inventory** | Art. 30 (ROPA) | 45 CFR § 164.308 | CA Privacy Law | Art. 10 (documentation) | — |
| **PII Detection** | Art. 4(1) | § 164.304 (PHI) | § 1798.100 | Art. 4 (personal data) | — |
| **Consent Tracking** | Art. 6, Art. 7 | 45 CFR § 164.308 | § 1798.100 | — | Creative license terms |
| **License Verification** | — | — | — | — | 17 USC § 101 (copyright) |
| **Deletion Impact** | Art. 17 (right to erasure) | 45 CFR § 164.312 | § 1798.105 | — | — |
| **Data Lineage** | Art. 32 (accountability) | 45 CFR § 164.308 (tracking) | — | Art. 10 (data quality) | — |
| **Retention Policy** | Art. 5(1)(e) | 45 CFR § 164.312 | — | — | — |

---

## Technical Deep Dive

### Neo4j Lineage Query Engine

```cypher
// Graph schema
CREATE INDEX idx_dataset_id ON (Dataset(id));
CREATE INDEX idx_model_id ON (Model(id));
CREATE INDEX idx_deployment_id ON (Deployment(id));

// Create relationships
CREATE CONSTRAINT unique_dataset_id ON (d:Dataset) ASSERT d.id IS UNIQUE;
CREATE CONSTRAINT unique_model_id ON (m:Model) ASSERT m.id IS UNIQUE;
CREATE CONSTRAINT unique_deployment_id ON (d:Deployment) ASSERT d.id IS UNIQUE;

// Query: All datasets -> models -> deployments (complete lineage)
MATCH (d:Dataset) -[r1:USED_FOR_TRAINING]-> (m:Model) -[r2:DEPLOYED_TO]-> (dep:Deployment)
RETURN d.name, m.name, dep.name
ORDER BY d.id, m.id, dep.id;

// Query: Models affected by deletion request
MATCH (d:Dataset) -[:DELETED_BY_SUBJECT {subject_id: 'john.doe@example.com'}]-> (deletionRequest:DeletionRequest)
      -[:IMPACTS]-> (m:Model)
RETURN m.name, m.status, m.retraining_required;
```

### Data Quality Scoring Algorithm

```python
def calculate_data_quality_score(dataset_df):
    """
    Calculate 0-100 quality score for dataset.
    """
    scores = {}

    # 1. Completeness: % of non-null values
    completeness = 1 - (dataset_df.isnull().sum().sum() / (len(dataset_df) * len(dataset_df.columns)))
    scores["completeness"] = completeness * 100

    # 2. Uniqueness: % of unique records (1 - duplicate_rate)
    uniqueness = 1 - ((len(dataset_df) - len(dataset_df.drop_duplicates())) / len(dataset_df))
    scores["uniqueness"] = uniqueness * 100

    # 3. Validity: % of values matching expected data types
    validity_scores = []
    for col in dataset_df.columns:
        try:
            expected_dtype = infer_expected_dtype(col)
            valid_values = (dataset_df[col].dtype == expected_dtype).sum()
            validity_scores.append(valid_values / len(dataset_df))
        except:
            validity_scores.append(0.5)  # Unknown data type, partial credit
    scores["validity"] = (sum(validity_scores) / len(validity_scores)) * 100

    # 4. Consistency: Statistical checks for outliers and anomalies
    outlier_pct = 0
    for numeric_col in dataset_df.select_dtypes(include=[np.number]).columns:
        Q1 = dataset_df[numeric_col].quantile(0.25)
        Q3 = dataset_df[numeric_col].quantile(0.75)
        IQR = Q3 - Q1
        outliers = ((dataset_df[numeric_col] < Q1 - 1.5 * IQR) | (dataset_df[numeric_col] > Q3 + 1.5 * IQR)).sum()
        outlier_pct += outliers / len(dataset_df)

    consistency = (1 - (outlier_pct / len(dataset_df.select_dtypes(include=[np.number]).columns))) * 100
    scores["consistency"] = consistency

    # 5. Weighted average
    weights = {
        "completeness": 0.3,
        "uniqueness": 0.2,
        "validity": 0.3,
        "consistency": 0.2
    }

    overall_score = sum(scores[metric] * weights[metric] for metric in weights.keys())
    return {
        "overall_score": overall_score,
        "dimension_scores": scores
    }
```

---

## Integration Points

UC-6 integrates with other platform components:

### UC-1 → UC-6
- UC-1 identifies systems using training data
- UC-6 provides lineage showing which datasets train those systems
- **Data flow**: `system_id, model_used` → UC-6 for lineage query

### UC-5 → UC-6
- UC-5 analyzes training data for bias
- UC-6 tracks bias analysis results with training data metadata
- **Data flow**: `training_dataset, bias_analysis_results` ↔ UC-5/UC-6

### UC-4 → UC-6
- UC-6 logs all dataset registration, deletion, and lineage changes
- **Data flow**: `data_lineage_event, deletion_event` → UC-4

---

## Business Value

### Quantified ROI Metrics

**GDPR Fine Avoidance**:
- **Before**: GDPR violation (unclear data inventory, no deletion capability) = €20M (4% revenue) fine
- **After**: Organized data governance; rapid deletion response = fine avoided
- **Annual risk reduction**: (1% probability of violation × €20M penalty) = **€200K/year**

**Deletion Request SLA Compliance**:
- **Before**: Data subject requests deletion; manual search takes 2–3 weeks = GDPR violation
- **After**: Lineage graph enables 24-hour deletion plan = full compliance
- **Fines avoided**: 1 GDPR violation = €50K–1M per incident; avoid 1 violation per year = **€500K/year**

**Copyright Compliance**:
- **Before**: Use data with unclear licensing; copyright dispute = $100K–5M settlement
- **After**: License verification before training = dispute prevented
- **Annual risk reduction**: (2% probability × $2.5M average cost) = **$50K/year**

**Model Retraining Efficiency**:
- **Before**: Unplanned data deletion or licensing issue discovered; retrain in crisis mode = $50K+ cost
- **After**: Lineage graph enables planned retraining; no crisis = savings
- **Per incident**: $30K saved × 2–3 incidents/year = **$60K–90K/year**

**Total Year-1 Quantified Value**: $200K + $500K + $50K + $75K = **$825K minimum**

### Qualitative Benefits

1. **Regulatory Confidence**: Regulators see organized data governance; reduced audit risk
2. **Data Subject Trust**: Can respond to deletion requests within 24 hours; demonstrates commitment to privacy
3. **Incident Response Speed**: Lineage graph enables rapid impact analysis; faster incident resolution
4. **Model Reproducibility**: Exact data versions tracked; models can be reproduced for audits

---

## Summary

The Training Data Governance & Lineage Tracking system delivers:

✓ **Automated dataset registration** with metadata extraction (record count, quality score, PII detection)
✓ **PII/PHI detection and tagging** (using Microsoft Presidio)
✓ **License detection and verification** (automatic from Hugging Face, GitHub, Kaggle)
✓ **Data lineage graphing** (Neo4j: dataset → model → deployment)
✓ **GDPR Article 17 impact analysis** (automated deletion request impact planning)
✓ **Copyright compliance for generative AI** (special handling for training data licensing)
✓ **Training data version control** (Git-based; reproducibility enabled)
✓ **$825K+/year quantified value** from GDPR fine avoidance and deletion compliance

This UC **follows UC-1–UC-5** and is the **sixth implementation priority**.
