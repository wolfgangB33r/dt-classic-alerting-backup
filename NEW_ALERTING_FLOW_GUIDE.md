# How to migrate from Classic Alerting Flow towards DQL-based Alerts and Simple Workflows

## Overview

Two new concepts work together to create a complete alerting and notification workflow in Dynatrace. They form the foundation of how problems are detected, and communicated to users and external systems.
Those two concepts are: 
* DQL based anomaly detectors (builtin:davis.anomaly-detectors), as replacement for Metric events (builtin:anomaly-detection.metric-events)
* Dynatrace simple workflows, as a replacement for problem filtering (builtin:alerting.profile) and problem notifications (builtin:problem.notifications)

## The DQL-based Alerting Config (Anomaly Detectors)

### 1. **builtin:davis.anomaly-detectors**
**Purpose:** Defines the conditions that trigger problem detection

**Role in Alert Flow:**
- Detects anomalies in DQL-queried timeseries data (values exceeding baselines, static thresholds, etc.)
- Creates initial problems when anomalies are identified
- The starting point of the alert notification pipeline
- Controls sensitivity and severity of problem creation

**Key Characteristics:**
- Condition-based: "Alert when timeseries value X exceeds baseline by Y%"
- Event-driven: Automatically triggered when metric conditions are met
- Severity levels: Can categorize detected issues by severity
- Scope: Can target specific entities, applications, or hosts

**Example Configuration Structure:**
```json

```

---

