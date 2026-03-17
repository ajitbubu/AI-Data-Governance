# UC-5: Bias Detection & Fairness Monitoring Engine

## Executive Summary

The Bias Detection & Fairness Monitoring Engine is the platform's AI equity layer, automatically detecting and quantifying bias in ML models across six key fairness dimensions: demographic parity, equalized odds, predictive parity, calibration, individual fairness, and intersectional bias. This UC ensures that AI systems treat all user groups fairly regardless of protected characteristics (race, gender, age, disability, national origin), meeting both regulatory requirements (EU AI Act Article 10, OMB M-25-21 Rights & Civil Liberties) and ethical standards.

Every organization deploying AI faces fairness risk: models trained on historical data perpetuate historical discrimination; algorithms optimized for accuracy often amplify bias against minority groups; and disparate impact (unequal outcomes despite equal treatment) creates legal liability. Undetected bias in hiring, lending, criminal justice, or benefits determination systems can result in $billions in liability, class-action lawsuits, and regulatory penalties (e.g., EEOC enforcement actions worth 10–100x typical settlements).

The Fairness Engine solves this via automated pre-deployment and runtime bias scanning using explainability libraries (SHAP, LIME) to identify which features drive disparate outcomes, with built-in remediation suggestions. Protected attribute monitoring ensures that even if models are trained without explicit protected attributes, proxies for those attributes are detected.

This UC benefits Chief Compliance Officers ensuring non-discrimination in AI; General Counsels managing liability exposure; Product teams building responsible AI; and Data Scientists deploying models with confidence in their fairness.

---

## What This Use Case Does

The Fairness Engine performs four continuous operations:

### Pre-Deployment Bias Scanning

Before any model is deployed to production, comprehensive bias analysis is performed:

**Step 1: Protected Attribute Detection**

System analyzes training data to identify columns containing or proxying for protected attributes:

```python
def detect_protected_attributes(training_data, feature_names):
    """
    Identify features that are or proxy for protected attributes.
    """
    protected_attributes = {
        "race": {"columns": ["race", "ethnicity", "country_of_origin"],
                 "proxies": ["zip_code", "neighborhood", "surname"]},
        "gender": {"columns": ["gender", "sex"],
                  "proxies": ["first_name", "pronouns", "title"]},
        "age": {"columns": ["age", "date_of_birth"],
               "proxies": ["graduation_year", "start_date"]},
        "disability": {"columns": ["disability_status"],
                      "proxies": ["medical_history", "medication_list"]},
        "national_origin": {"columns": ["country", "citizenship"],
                           "proxies": ["language", "accent", "surname"]}
    }

    detected = []

    # 1. Direct protected attribute detection
    for feature in feature_names:
        for attr_type, attr_config in protected_attributes.items():
            if feature.lower() in [col.lower() for col in attr_config["columns"]]:
                detected.append({
                    "attribute": attr_type,
                    "detection_method": "direct",
                    "feature": feature,
                    "confidence": "High"
                })

    # 2. Proxy attribute detection (statistical analysis)
    for feature in feature_names:
        for attr_type, attr_config in protected_attributes.items():
            # Check if feature is proxy (correlation with actual attribute or patterns indicating proxy)
            if is_proxy_for(feature, training_data, attr_type):
                detected.append({
                    "attribute": attr_type,
                    "detection_method": "proxy",
                    "feature": feature,
                    "confidence": "Medium",
                    "proxy_reason": f"Strong correlation with {attr_type}"
                })

    return detected
```

**Step 2: Fairness Metric Calculation**

Six fairness metrics calculated for each protected attribute:

1. **Demographic Parity** (SPD: Statistical Parity Difference)
   - Definition: Proportion of positive outcomes equal across protected groups
   - Formula: |P(Ŷ=1 | A=0) - P(Ŷ=1 | A=1)|
   - Threshold: <0.1 (within 10% of each other)
   - Example: Resume screener approves 60% of male candidates, 50% of female candidates → SPD = 0.10 (borderline)

2. **Equalized Odds**
   - Definition: False Positive Rate and True Positive Rate equal across groups
   - Formula: |TPR_0 - TPR_1| + |FPR_0 - FPR_1|
   - Threshold: <0.1
   - Example: Model correctly identifies 90% of qualified male candidates but only 75% of qualified female candidates → violation

3. **Predictive Parity**
   - Definition: Precision equal across protected groups (positive prediction value same for all groups)
   - Formula: |P(Y=1 | Ŷ=1, A=0) - P(Y=1 | Ŷ=1, A=1)|
   - Threshold: <0.1
   - Example: When model predicts "approve", 80% of male candidates are actually qualified, 70% of female candidates → violation

4. **Calibration**
   - Definition: Predicted probability reflects actual outcome probability for each group
   - Formula: |Predicted P(Y=1 | Group A=0) - Actual P(Y=1 | Group A=0)| (repeat for A=1)
   - Threshold: <0.05
   - Example: Model predicts 50% approval for female candidates; actual 45% approval → calibration error 5% (borderline)

5. **Individual Fairness**
   - Definition: Similar individuals treated similarly regardless of protected attribute
   - Formula: Euclidean distance between similar individuals' predictions; check if protected attribute drives difference
   - Threshold: <5% prediction difference attributable to protected attribute
   - Example: Two identical job applicants (same skills, experience) differing only in race; if predictions differ >5% → violation

6. **Intersectional Bias**
   - Definition: Fairness across multiple protected attributes combined (not just individual attributes)
   - Formula: Metric calculated for combinations (e.g., gender × race, age × disability)
   - Threshold: <0.1 per combination
   - Example: Model may be fair to women overall, but unfair to Black women (intersectional violation)

**Calculation Code**:
```python
def calculate_fairness_metrics(predictions, actual_labels, protected_attrs):
    """
    Calculate all six fairness metrics.
    """
    metrics = {
        "demographic_parity": calculate_spd(predictions, actual_labels, protected_attrs),
        "equalized_odds": calculate_equalized_odds(predictions, actual_labels, protected_attrs),
        "predictive_parity": calculate_predictive_parity(predictions, actual_labels, protected_attrs),
        "calibration": calculate_calibration(predictions, actual_labels, protected_attrs),
        "individual_fairness": calculate_individual_fairness(predictions, protected_attrs),
        "intersectional": calculate_intersectional_bias(predictions, actual_labels, protected_attrs)
    }

    # Mark violations
    violations = []
    for metric_name, metric_value in metrics.items():
        if metric_value > FAIRNESS_THRESHOLD:
            violations.append({
                "metric": metric_name,
                "value": metric_value,
                "threshold": FAIRNESS_THRESHOLD,
                "violated": metric_value > FAIRNESS_THRESHOLD
            })

    return {
        "metrics": metrics,
        "violations": violations,
        "overall_fairness_score": calculate_overall_score(metrics)
    }
```

**Step 3: Feature Attribution Analysis**

Explainability libraries (SHAP, LIME) used to identify which features drive disparate outcomes:

```python
def attribute_disparate_impact(model, X_test, y_test, protected_attr_values):
    """
    Use SHAP to determine which features drive disparate impact.
    """
    # 1. Calculate SHAP values (importance of each feature for each prediction)
    explainer = shap.TreeExplainer(model) if tree_model else shap.KernelExplainer(model.predict, X_test.sample(100))
    shap_values = explainer.shap_values(X_test)

    # 2. Compare SHAP values between protected groups
    group_0_indices = np.where(protected_attr_values == 0)[0]
    group_1_indices = np.where(protected_attr_values == 1)[0]

    feature_contributions = {}
    for feature_idx, feature_name in enumerate(X_test.columns):
        # Average SHAP value contribution per group
        group_0_contribution = np.mean(np.abs(shap_values[group_0_indices, feature_idx]))
        group_1_contribution = np.mean(np.abs(shap_values[group_1_indices, feature_idx]))

        # Difference in feature contribution
        contribution_diff = abs(group_0_contribution - group_1_contribution)

        feature_contributions[feature_name] = {
            "group_0_avg_contribution": group_0_contribution,
            "group_1_avg_contribution": group_1_contribution,
            "difference": contribution_diff
        }

    # 3. Identify top features driving disparate impact
    sorted_features = sorted(
        feature_contributions.items(),
        key=lambda x: x[1]["difference"],
        reverse=True
    )

    return {
        "disparate_impact_features": sorted_features[:10],  # Top 10 features
        "primary_driver": sorted_features[0][0] if sorted_features else None
    }
```

**Step 4: Bias Remediation Recommendations**

For each detected bias, system recommends remediation actions:

```python
def recommend_remediation(bias_finding):
    """
    Recommend remediation for detected bias.
    """
    remediation_strategies = {
        "demographic_parity_violation": [
            {
                "strategy": "rebalance_training_data",
                "description": "Oversample underrepresented group in training data",
                "effort": "Medium",
                "effectiveness": "High"
            },
            {
                "strategy": "apply_fairness_constraints",
                "description": "Add fairness regularization term to model loss function",
                "effort": "Low",
                "effectiveness": "Medium"
            },
            {
                "strategy": "change_decision_threshold",
                "description": "Adjust decision threshold per protected group to equalize approval rates",
                "effort": "Low",
                "effectiveness": "High"
            }
        ],
        "equalized_odds_violation": [
            {
                "strategy": "remove_disparate_impact_features",
                "description": "Remove features identified as driving disparate impact",
                "effort": "Medium",
                "effectiveness": "High",
                "caution": "May reduce model accuracy"
            },
            {
                "strategy": "apply_fairness_constraints",
                "description": "Constrain equalized odds during model training",
                "effort": "Medium",
                "effectiveness": "High"
            }
        ],
        # ... more strategies for other bias types ...
    }

    bias_type = identify_bias_type(bias_finding)
    return remediation_strategies.get(bias_type, [])
```

### Runtime Fairness Monitoring

After deployment, continuous monitoring detects if model fairness degrades:

**Monitoring Metrics** (tracked per day):
- Demographic parity: approval/rejection rates by protected group
- Equalized odds: true positive rate and false positive rate by group
- Calibration: predicted vs. actual outcome rates by group
- Individual fairness: prediction variance for similar individuals

**Alert Triggers**:
- If any fairness metric violates threshold for 3+ consecutive days → escalate to Data Science team
- If fairness metric degrades >10% from baseline → escalate
- If disparate impact increases in any protected group → escalate

**Dashboard Visualization**:
```
Fairness Monitoring Dashboard — Resume Screening Tool

Current Metrics:
├─ Demographic Parity: 0.08 ✓ (threshold: 0.10)
├─ Equalized Odds: 0.06 ✓
├─ Predictive Parity: 0.09 ✓
├─ Calibration: 0.03 ✓
└─ Intersectional Bias:
   ├─ Gender × Race: 0.08 ✓
   ├─ Gender × Age: 0.12 ✗ VIOLATION
   └─ Race × Age: 0.09 ✓

Approval Rates by Protected Group:
├─ Male: 65%
├─ Female: 58% (7% difference, -6% vs baseline)
├─ White: 68%
├─ Black: 55% (13% difference, -8% vs baseline) ✗ CONCERNING
└─ Asian: 64%

Primary Disparate Impact Driver: "experience_years_weighted_by_education_level"
├─ Feature weight for male candidates: 0.45
├─ Feature weight for female candidates: 0.32
├─ Difference: 0.13 (significant)

Recommended Remediations:
1. [Rebalance training data] — Oversample minority groups
2. [Apply fairness constraints] — Add fairness term to loss function
3. [Remove disparate impact features] — Drop experience_years_weighted feature
```

### Protected Attribute Monitoring

Even if training data doesn't explicitly contain protected attributes, system detects proxies:

```python
def detect_proxy_attributes(predictions, features):
    """
    Detect if model outcomes correlate with proxies for protected attributes.
    """
    known_proxies = {
        "race": ["zip_code", "neighborhood", "surname", "high_school"],
        "gender": ["first_name", "title", "salary_history"],
        "age": ["graduation_year", "job_start_date", "retirement_contribution"],
        "disability": ["health_insurance_type", "medical_expense_ratio", "parking_permit"]
    }

    correlations = {}
    for protected_attr, proxy_features in known_proxies.items():
        for proxy_feature in proxy_features:
            if proxy_feature in features.columns:
                correlation = calculate_correlation(predictions, features[proxy_feature])
                if abs(correlation) > 0.3:  # Strong correlation threshold
                    correlations[proxy_feature] = {
                        "proxy_for": protected_attr,
                        "correlation_strength": correlation,
                        "alert": "Model outcomes correlate with proxy for protected attribute"
                    }

    return correlations
```

### Intersectional Bias Detection

Bias detection extended to combinations of protected attributes:

```python
def calculate_intersectional_bias(predictions, actual_labels, protected_attrs_dict):
    """
    Calculate fairness metrics for combinations of protected attributes.
    """
    # Identify all protected attributes
    attr_names = list(protected_attrs_dict.keys())  # ['race', 'gender', 'age']

    intersectional_metrics = {}

    # For each pair of attributes
    for i in range(len(attr_names)):
        for j in range(i+1, len(attr_names)):
            attr1, attr2 = attr_names[i], attr_names[j]
            values1 = protected_attrs_dict[attr1]
            values2 = protected_attrs_dict[attr2]

            # Calculate fairness metric for each combination
            for val1 in set(values1):
                for val2 in set(values2):
                    mask = (values1 == val1) & (values2 == val2)
                    if np.sum(mask) > 30:  # Minimum 30 samples for statistical significance
                        group_predictions = predictions[mask]
                        group_labels = actual_labels[mask]

                        # Calculate metrics for this subgroup
                        spd = calculate_spd_for_group(group_predictions, group_labels)
                        intersectional_metrics[f"{attr1}={val1}, {attr2}={val2}"] = spd

    return intersectional_metrics
```

---

## Key Capabilities

- **Pre-deployment bias scanning** (6 fairness metrics: demographic parity, equalized odds, predictive parity, calibration, individual fairness, intersectional)
- **Protected attribute detection** (direct and proxy attributes)
- **Feature attribution analysis** (SHAP/LIME: which features drive disparate impact)
- **Bias remediation recommendations** (automated suggestions for fairness improvement)
- **Runtime fairness monitoring** (continuous tracking of fairness metrics post-deployment)
- **Alert escalation** (fairness violations trigger alerts to Data Science team)
- **Intersectional bias detection** (fairness across combinations of protected attributes)
- **Proxy attribute monitoring** (detects if outcomes correlate with proxies for protected attributes even if direct attributes removed)
- **Fairness dashboard** (visualization of metrics, violations, drivers, recommendations)
- **GDPR Article 22 support** (right to human review for significant decisions)
- **Integration with UC-6** (training data bias analysis)
- **EU AI Act Article 10 compliance** (data quality and bias requirements)
- **NIST AI RMF MAP 2.3 compliance** (bias/fairness mapping and measurement)

---

## How It Works — Step by Step

### Pre-Deployment Analysis Workflow

**Phase 1: Data Preparation**

Training and test data loaded; protected attributes identified:

```python
def prepare_bias_analysis(model, train_data, test_data, protected_attr_columns):
    """
    Prepare for bias analysis.
    """
    # 1. Identify protected attributes
    protected_attrs_detected = detect_protected_attributes(
        train_data,
        protected_attr_columns
    )

    # 2. Generate predictions
    train_predictions = model.predict(train_data)
    test_predictions = model.predict(test_data)

    # 3. Extract labels
    train_labels = train_data['target']
    test_labels = test_data['target']

    return {
        "model": model,
        "train_predictions": train_predictions,
        "test_predictions": test_predictions,
        "train_labels": train_labels,
        "test_labels": test_labels,
        "protected_attrs": protected_attrs_detected
    }
```

**Phase 2: Fairness Metric Calculation**

All six fairness metrics calculated on test data:

```python
def run_bias_analysis(prepared_data):
    """
    Execute full bias analysis.
    """
    predictions = prepared_data["test_predictions"]
    labels = prepared_data["test_labels"]
    protected_attrs = prepared_data["protected_attrs"]

    fairness_report = {
        "model": prepared_data["model"].name,
        "timestamp": now(),
        "protected_attributes_detected": protected_attrs,
        "fairness_metrics": {},
        "violations": [],
        "feature_attribution": {},
        "remediation_recommendations": []
    }

    # Calculate metrics for each protected attribute
    for protected_attr in protected_attrs:
        attr_name = protected_attr["attribute"]
        attr_values = prepared_data[f"{attr_name}_values"]

        metrics = calculate_fairness_metrics(
            predictions,
            labels,
            {attr_name: attr_values}
        )

        fairness_report["fairness_metrics"][attr_name] = metrics["metrics"]

        # Track violations
        if metrics["violations"]:
            fairness_report["violations"].extend(metrics["violations"])

        # Analyze feature attribution
        feature_attribution = attribute_disparate_impact(
            prepared_data["model"],
            prepared_data["test_data"],
            labels,
            attr_values
        )
        fairness_report["feature_attribution"][attr_name] = feature_attribution

        # Recommend remediations
        for violation in metrics["violations"]:
            recommendations = recommend_remediation(violation)
            fairness_report["remediation_recommendations"].extend(recommendations)

    # Intersectional bias analysis
    fairness_report["intersectional_bias"] = calculate_intersectional_bias(
        predictions,
        labels,
        {pa["attribute"]: prepared_data[f"{pa['attribute']}_values"] for pa in protected_attrs}
    )

    return fairness_report
```

**Phase 3: Bias Report Generation**

Comprehensive report generated and presented to stakeholders:

```
=== AI FAIRNESS ANALYSIS REPORT ===
Model: Resume Screening Tool
Analysis Date: 2024-12-15
Test Set Size: 10,000 records

=== EXECUTIVE SUMMARY ===
Fairness Status: ⚠ VIOLATIONS DETECTED

The model demonstrates fair treatment across most protected groups, but violates equalized odds for Black candidates. Recommended action: apply fairness constraints during retraining.

=== DEMOGRAPHIC PARITY (Statistical Parity Difference) ===
Metric Definition: Approval rates equal across protected groups
Threshold: <0.10 (within 10%)

Results:
Gender:
├─ Male approval rate: 65%
├─ Female approval rate: 58%
├─ SPD: 0.07 ✓ (PASS)

Race:
├─ White approval rate: 68%
├─ Black approval rate: 55%
├─ SPD: 0.13 ✗ (VIOLATION)
├─ Asian approval rate: 64%
├─ Hispanic approval rate: 61%

Age:
├─ <30 approval rate: 52%
├─ 30-40 approval rate: 68%
├─ >40 approval rate: 60%
├─ SPD: 0.16 ✗ (VIOLATION)

=== EQUALIZED ODDS (FPR & TPR Parity) ===
Metric Definition: False Positive Rate and True Positive Rate equal across protected groups
Threshold: <0.10

Results:
Gender:
├─ Male TPR: 0.92, Female TPR: 0.88
├─ Difference: 0.04 ✓ (PASS)

Race:
├─ White TPR: 0.94, Black TPR: 0.78
├─ Difference: 0.16 ✗ (VIOLATION)
├─ Asian TPR: 0.91

=== FEATURE ATTRIBUTION (SHAP Analysis) ===
Primary disparate impact drivers (by group):

For Black candidates (group with lower outcomes):
1. "years_of_experience_weighted" (importance: -0.15)
   └─ Description: This feature disproportionately penalizes Black candidates
2. "elite_school_bonus" (importance: -0.08)
   └─ Description: Overweights elite school attendance (which correlates with race)
3. "employment_gaps" (importance: -0.07)
   └─ Description: Penalizes employment gaps (which may reflect systemic barriers)

=== INTERSECTIONAL BIAS ===
Fairness across combinations of protected attributes:

Black Female candidates:
├─ Approval rate: 45%
├─ vs. White Male: 72%
├─ Disparate impact: 27% (SEVERE)

Black Male candidates:
├─ Approval rate: 62%
├─ vs. White Male: 72%
├─ Disparate impact: 10% (acceptable)

White Female candidates:
├─ Approval rate: 61%
├─ vs. White Male: 72%
├─ Disparate impact: 11% (acceptable)

=== RECOMMENDED REMEDIATIONS ===
Priority 1 (Most Effective):
1. Remove "years_of_experience_weighted" feature
   └─ Estimated fairness improvement: SPD from 0.13 to 0.06
   └─ Accuracy impact: -2% (acceptable)
   └─ Effort: Low

2. Apply fairness constraints during retraining
   └─ Use Fairlearn library with equalized_odds_ratio=0.95
   └─ Estimated fairness improvement: SPD from 0.13 to 0.07
   └─ Accuracy impact: -1% (acceptable)

Priority 2:
3. Rebalance training data
   └─ Oversample Black candidates in training set
   └─ Target: match demographic distribution of candidate pool
   └─ Effort: Medium

=== APPROVAL DEADLINE ===
This model cannot be deployed to production without remediation.
Fairness violations must be addressed before approval.

Approval Status: BLOCKED until violations remediated

=== NEXT STEPS ===
1. Data Science team: Implement Priority 1 remediations
2. Re-run bias analysis on retrained model
3. Submit for fairness review once violations resolved
4. Deploy with continuous fairness monitoring
```

**Phase 4: Approval Blocking**

If fairness violations detected, model blocked from deployment:

```python
def check_fairness_approval(fairness_report):
    """
    Determine if model can be approved for deployment.
    """
    violations = fairness_report["violations"]
    critical_violations = [v for v in violations if v["severity"] == "Critical"]

    if critical_violations:
        return ApprovalDecision(
            approved=False,
            reason="Critical fairness violations detected",
            violations=critical_violations,
            required_remediations=fairness_report["remediation_recommendations"]
        )

    # If no critical violations, can proceed to deployment
    return ApprovalDecision(approved=True)
```

### Runtime Monitoring Workflow

**Phase 1: Baseline Establishment**

After deployment, initial fairness metrics recorded as baseline:

```
Baseline Established (2024-01-15):
├─ Demographic Parity: 0.08
├─ Equalized Odds: 0.06
├─ Predictive Parity: 0.09
├─ Calibration: 0.03
└─ Intersectional Bias (Race×Gender): 0.10
```

**Phase 2: Daily Monitoring**

Each day, fairness metrics recalculated on new predictions:

```python
def monitor_fairness_daily(model_id, date):
    """
    Calculate fairness metrics for predictions made on a given date.
    """
    # Query predictions and actual outcomes from that date
    predictions = db.query("""
        SELECT * FROM predictions
        WHERE model_id = %s AND prediction_date = %s
    """, model_id, date)

    # Get actual outcomes (if available by that date)
    actual_outcomes = db.query("""
        SELECT prediction_id, actual_outcome
        FROM actual_outcomes
        WHERE prediction_date >= %s AND prediction_date <= %s
    """, date, date + 7 days)  # May take up to 7 days to get actual outcomes

    # Calculate fairness metrics for this date
    daily_metrics = calculate_fairness_metrics(
        predictions["prediction_value"],
        actual_outcomes["actual_outcome"],
        predictions["protected_attributes"]
    )

    # Compare to baseline
    violations = []
    for metric_name, metric_value in daily_metrics.items():
        baseline_value = FAIRNESS_BASELINE[metric_name]
        if metric_value > baseline_value + 0.05:  # 5% threshold
            violations.append({
                "metric": metric_name,
                "date": date,
                "value": metric_value,
                "baseline": baseline_value,
                "change": metric_value - baseline_value
            })

    # Alert if violations detected
    if violations:
        alert_data_science_team(
            model_id=model_id,
            date=date,
            violations=violations
        )

    return daily_metrics
```

**Phase 3: Alert Escalation**

If fairness degrades, escalation workflow triggered:

```
Day 1: Fairness metric violation detected
├─ Alert sent to Data Science team (low severity)
└─ No action required; monitoring continues

Day 2: Violation continues
├─ Alert sent to Data Science team (medium severity)
└─ Recommended action: investigate root cause

Day 3: Violation continues for 3rd consecutive day
├─ Alert sent to Chief Data Officer (high severity)
├─ Model may be paused pending investigation
└─ Required action: root cause analysis by EOD

Investigation Results:
├─ Root cause: Training data has shifted (new hiring practice favors certain demographics)
├─ Recommended action: Retrain model on current data
├─ Timeline: Retraining + bias analysis = 1 week
└─ Interim: Model continues with human-in-loop review of high-risk decisions
```

---

## Compliance Benefit

The Fairness Engine ensures compliance with critical non-discrimination requirements:

### Before DataSafeguard

- **Undetected bias**: Models deployed with disparate impact; discovered via EEOC complaint
- **No fairness metrics**: Can't quantify bias; hard to defend in legal action
- **Feature opacity**: Don't know which model features drive discrimination
- **No remediation strategy**: When bias discovered, no systematic approach to fixing it
- **Intersectional blindness**: Monitor fairness for individual attributes but miss intersectional bias (e.g., bias against Black women specifically)

**Result**: Discrimination lawsuits, EEOC enforcement, regulatory penalties, reputational damage.

### With DataSafeguard UC-5

- **Pre-deployment bias detection**: Disparate impact identified before production; remediated before harm
- **Six fairness metrics**: Quantify fairness across multiple dimensions
- **Feature attribution**: Know exactly which features drive discrimination
- **Automated remediation**: Specific recommendations for fairness improvement
- **Intersectional monitoring**: Catch bias against subgroups (e.g., Black women, disabled Latinos)

**Result**: Non-discriminatory AI systems; confidence in fairness; regulatory compliance; reduced liability.

---

## Regulatory Coverage

| Control | GDPR | FCRA | ECOA | Title VII | OMB M-25-21 | EU AI Act | NIST AI RMF |
|---------|------|------|------|-----------|------------|-----------|------------|
| **Pre-Deployment Bias Scanning** | Art. 25 (fairness) | — | Reg. B (adverse action) | Disparate impact | RCL requirement | Art. 10 (quality), Art. 35 (testing) | MAP 2.3 (bias mapping) |
| **Demographic Parity Tracking** | — | — | ECOA analysis | Statistical parity | Disparate impact analysis | — | MEASURE 2.3 (fairness) |
| **Equalized Odds Monitoring** | — | — | ECOA analysis | Equal opportunity | Equal outcomes | — | MEASURE 2.3 |
| **Feature Attribution** | Art. 22 (explanation) | — | Reg. B (explanation) | OFCCP (job validation) | Explainability | Art. 14 (transparency) | MAP 1.3 (transparency) |
| **Intersectional Bias Detection** | Art. 25 (fairness) | — | ECOA §1002.104 (intersectional) | Title VII (intersectional) | — | — | — |
| **Protected Attribute Monitoring** | Art. 9 (sensitive data) | — | Reg. B (protected class) | Title VII (protected class) | — | — | — |
| **Remediation Tracking** | — | — | Reg. B (remediation) | OFCCP (corrective action) | — | — | — |

---

## Technical Deep Dive

### Fairness Metrics Algorithms

**Demographic Parity (SPD: Statistical Parity Difference)**:
```python
def calculate_spd(predictions, labels, protected_attr_values):
    """
    Calculate Statistical Parity Difference (SPD).
    SPD = |P(Ŷ=1 | A=0) - P(Ŷ=1 | A=1)|
    """
    group_0_positive_rate = np.mean(predictions[protected_attr_values == 0] == 1)
    group_1_positive_rate = np.mean(predictions[protected_attr_values == 1] == 1)
    spd = abs(group_0_positive_rate - group_1_positive_rate)
    return spd
```

**Equalized Odds**:
```python
def calculate_equalized_odds(predictions, labels, protected_attr_values):
    """
    Calculate difference in TPR and FPR between groups.
    EO = |TPR_0 - TPR_1| + |FPR_0 - FPR_1|
    """
    group_0_mask = protected_attr_values == 0
    group_1_mask = protected_attr_values == 1

    # True Positive Rate
    tpr_0 = np.sum((predictions[group_0_mask] == 1) & (labels[group_0_mask] == 1)) / np.sum(labels[group_0_mask] == 1)
    tpr_1 = np.sum((predictions[group_1_mask] == 1) & (labels[group_1_mask] == 1)) / np.sum(labels[group_1_mask] == 1)

    # False Positive Rate
    fpr_0 = np.sum((predictions[group_0_mask] == 1) & (labels[group_0_mask] == 0)) / np.sum(labels[group_0_mask] == 0)
    fpr_1 = np.sum((predictions[group_1_mask] == 1) & (labels[group_1_mask] == 0)) / np.sum(labels[group_1_mask] == 0)

    eo = abs(tpr_0 - tpr_1) + abs(fpr_0 - fpr_1)
    return eo
```

### SHAP-Based Feature Attribution

```python
def explain_disparate_impact_with_shap(model, X_train, X_test, protected_attr_idx):
    """
    Use SHAP to explain which features drive disparate impact.
    """
    # Train SHAP explainer
    explainer = shap.TreeExplainer(model) if is_tree_based(model) else shap.KernelExplainer(
        model.predict,
        X_train.sample(100)
    )

    # Calculate SHAP values for test set
    shap_values = explainer.shap_values(X_test)

    # Separate by protected attribute value
    protected_values = X_test.iloc[:, protected_attr_idx]
    group_0_indices = np.where(protected_values == 0)[0]
    group_1_indices = np.where(protected_values == 1)[0]

    # Compare average absolute SHAP values per feature per group
    feature_importance_group_0 = np.mean(np.abs(shap_values[group_0_indices]), axis=0)
    feature_importance_group_1 = np.mean(np.abs(shap_values[group_1_indices]), axis=0)

    # Calculate disparate importance
    disparate_importance = feature_importance_group_1 - feature_importance_group_0

    # Sort by disparate importance
    sorted_features = np.argsort(np.abs(disparate_importance))[::-1]

    result = []
    for feature_idx in sorted_features[:10]:  # Top 10
        result.append({
            "feature": X_test.columns[feature_idx],
            "importance_group_0": feature_importance_group_0[feature_idx],
            "importance_group_1": feature_importance_group_1[feature_idx],
            "disparate_importance": disparate_importance[feature_idx]
        })

    return result
```

---

## Integration Points

UC-5 integrates with other platform components:

### UC-1 → UC-5
- UC-1 classifies systems (risk tier)
- UC-5 prioritizes bias analysis for high-risk systems
- **Data flow**: `system_id, risk_tier` → UC-5 for prioritization

### UC-6 → UC-5
- UC-6 provides training data lineage and composition
- UC-5 analyzes training data for bias patterns
- **Data flow**: `training_data_metadata, protected_attrs_present` → UC-5

### UC-4 → UC-5
- UC-5 logs all bias analyses and remediation actions
- **Data flow**: `bias_analysis_event, remediation_action` → UC-4

---

## Business Value

### Quantified ROI Metrics

**Legal Liability Avoidance**:
- **Before**: Undetected bias results in discrimination lawsuit = $5M–50M settlement
- **After**: Pre-deployment bias detection prevents lawsuit
- **Annual risk reduction**: (5% probability of lawsuit × $25M average cost) = **$1.25M/year**

**EEOC Enforcement Avoidance**:
- **Before**: EEOC investigation and settlement = $100K–5M
- **After**: No disparate impact discovered by EEOC
- **Annual risk reduction**: (2% probability × $2M average cost) = **$40K/year**

**Retraining Efficiency**:
- **Before**: Bias discovered post-deployment; manual debugging and retraining = 4–6 weeks
- **After**: Bias detected pre-deployment; automated remediation recommendations = 1–2 weeks
- **Time savings**: 2–4 weeks × 2 full-time engineers × $200/hour = **$32K–64K per incident**
- **Incidents prevented per year**: 2–3 = **$64K–192K/year**

**Model Deployment Velocity**:
- **Before**: Fairness review process manual; 2–3 weeks to approve model for production
- **After**: Automated fairness analysis in 1 day
- **Time savings**: 10 days × 1 engineer × $200/hour = **$16K per model deployment**
- **Models deployed per year**: 24 = **$384K/year**

**Total Year-1 Quantified Value**: $1.25M + $40K + $128K + $384K = **$1.802M minimum**

### Qualitative Benefits

1. **Regulatory Confidence**: EEOC and civil rights agencies see fair AI practices; reduced enforcement risk
2. **Customer Trust**: Can credibly communicate commitment to fairness; competitive advantage in regulated industries
3. **Employee Recruitment**: Data Science talent prefers companies with fairness values; better recruitment outcomes
4. **Brand Protection**: Avoid discrimination scandal; protecting brand value

---

## Summary

The Bias Detection & Fairness Monitoring Engine delivers:

✓ **Pre-deployment bias scanning** (6 fairness metrics across protected groups)
✓ **Protected attribute detection** (direct and proxy attributes)
✓ **Feature attribution analysis** (SHAP/LIME: root causes of disparate impact)
✓ **Automated remediation recommendations** (specific improvement strategies)
✓ **Runtime fairness monitoring** (continuous tracking post-deployment)
✓ **Intersectional bias detection** (fairness across attribute combinations)
✓ **Proxy attribute monitoring** (detect correlation with protected attributes even when removed)
✓ **$1.802M+/year quantified value** from legal liability avoidance and retraining efficiency

This UC **follows UC-1, UC-2, UC-3** and is the **fifth implementation priority**.
