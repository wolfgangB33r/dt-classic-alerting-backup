# Dynatrace Classic Alert Notification Flow - Settings Schemas Guide

## Overview

The three settings schemas work together to create a complete alerting and notification workflow in Dynatrace. They form the foundation of how problems are detected, grouped, and communicated to users and external systems.

## The Three Settings Schemas

### 1. **builtin:anomaly-detection.metric-events**
**Purpose:** Defines the conditions that trigger problem detection

**Role in Alert Flow:**
- Detects anomalies in metrics (values exceeding baselines, static thresholds, etc.)
- Creates initial problems when anomalies are identified
- The starting point of the alert notification pipeline
- Controls sensitivity and severity of problem creation

**Key Characteristics:**
- Condition-based: "Alert when metric X exceeds baseline by Y%"
- Event-driven: Automatically triggered when metric conditions are met
- Severity levels: Can categorize detected issues by severity
- Scope: Can target specific entities, applications, or hosts

**Example Configuration Structure:**
```json
{
  "objectId": "anomaly-detection-rule-id",
  "value": {
    "name": "High CPU Usage Detection",
    "enabled": true,
    "metricKey": "builtin:host.cpu.usage",
    "alertConditions": [{
      "baselineType": "BASELINE_BASED",
      "deviations": 3,
      "occurrences": 5
    }],
    "severityLevel": "CRITICAL"
  }
}
```

---

### 2. **builtin:alerting.profile**
**Purpose:** Controls how problems are grouped, consolidated, and filtered

**Role in Alert Flow:**
- Acts as a reusable filter and processor BETWEEN problem detection and notification
- Groups related problems together for notification sending
- Controls severity handling and escalation logic

**Key Characteristics:**
- Post-detection filtering: Works on already-detected problems
- Time-based rules: Uses time windows for grouping and deduplication
- Severity escalation: Can escalate based on problem patterns

**Example Configuration Structure:**
```json
{
  "objectId": "alerting-profile-id",
  "value": {
    "displayName": "Production Alert Profile",
    "rules": [{
      "severityLevel": "CRITICAL",
      "tagFilter": {
        "include": ["environment:production"],
        "exclude": []
      },
      "delayInMinutes": 5,
      "eventCountAggregation": {
        "eventCountAggregation": "AGGREGATE_BY_SOURCE",
        "eventCountAggregationType": "ALL_PROBLEMS",
        "triggerOnCount": 1
      }
    }],
    "enabled": true
  }
}
```

---

### 3. **builtin:problem.notifications**
**Purpose:** Defines HOW and WHERE problems are notified

**Role in Alert Flow:**
- The final destination stage of the alert flow
- Routes problems to notification channels (email, Slack, PagerDuty, webhooks, etc.)
- Determines who gets notified based on problem characteristics
- Handles notification escalation and repeat notifications
- Integrates with external systems

**Key Characteristics:**
- Channel-based: Routes to email, SMS, webhooks, integrations, etc.
- Recipient determination: Can use tags, entity types, or custom routing
- Escalation paths: Can escalate through multiple channels/recipients
- Event type filtering: Can trigger on problem creation, resolution, or both

**Example Configuration Structure:**
```json
{
  "objectId": "notification-rule-id",
  "value": {
    "displayName": "Production Incident Notification",
    "enabled": true,
    "rules": [{
      "type": "PROBLEM",
      "enabled": true,
      "filter": {
        "customFilter": {
          "filterOperator": "AND",
          "filters": [{
            "filterOperator": "OR",
            "nestedFilters": [{
              "key": "SEVERITY",
              "stringValue": "CRITICAL"
            }]
          }]
        }
      },
      "notificationTargets": [{
        "type": "SLACK",
        "slackNotificationConfig": {
          "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
          "channel": "#incidents"
        }
      }]
    }],
    "eventTypeFilter": ["CREATED", "RESOLVED"]
  }
}
```

---

## The Complete Alert Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    PROBLEM DETECTION LAYER                      │
│         builtin:anomaly-detection.metric-events                 │
│  (Metric Thresholds → Anomalies → Initial Problem Creation)    │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ Problem Detected
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ALERT MANAGEMENT LAYER                        │
│              builtin:alerting.profile                           │
│  (Grouping → Deduplication → Filtering → Consolidation)        │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ Alert Ready for Notification
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                  NOTIFICATION DELIVERY LAYER                    │
│            builtin:problem.notifications                        │
│  (Routing → Integration → Escalation → User/System Delivery)   │
└──────────────────────────────────────────────────────────────────┘
```

---

## How They Work Together

### Example Scenario: High CPU Usage Alert

1. **Detection (anomaly-detection.metric-events)**
   - Rule monitors host CPU usage
   - Detects that CPU has exceeded baseline by 4 deviations for 5 consecutive minutes
   - Creates a CRITICAL problem with tags: `environment:production`, `type:performance`

2. **Management (alerting.profile)**
   - Alert profile's rule matches: severity=CRITICAL and tag filter includes production
   - Looks for similar problems in the last 5 minutes (delay window)
   - Finds 3 related CPU alerts from the same host
   - Consolidates them into ONE alert to reduce noise
   - Forwards consolidated alert for notification

3. **Notification (problem.notifications)**
   - Notification rule filters: "Send CRITICAL problems with tag 'type:performance' to Slack"
   - Additionally, escalates to PagerDuty if problem persists > 15 minutes
   - Sends initial notification to #incidents Slack channel
   - If resolved, sends a "Resolved" message to the same channel

---

## Key Relationships & Dependencies

### Anomaly Detection → Alerting Profile
- **Dependency:** Alerting profiles work ONLY on problems created by anomaly detection rules
- **Interaction:** The severity and tags from anomaly detection are used by alerting profiles to filter and group
- **Example:** If anomaly detection doesn't create a problem, the alerting profile never triggers

### Alerting Profile → Problem Notifications
- **Dependency:** Problem notifications only fire on problems processed by alerting profiles
- **Interaction:** Alerting profile rules determine which problems are "ready" for notification
- **Example:** If alerting profile filters out a problem, no notification is sent

### All Three Together
- **Complete lifecycle:** Anomaly Detection (WHEN) → Alerting Profile (WHAT/HOW_MUCH) → Notifications (WHERE/TO_WHOM)
- **Filtering layers:** Each layer can suppress/enhance based on different criteria
- **Tag-based routing:** Tags from detection flow through profiles to notifications for intelligent routing

---

## Configuration Best Practices

### 1. **Anomaly Detection Rules**
- Create specific rules for each critical metric
- Use baselines for normal variation, static thresholds for absolute limits
- Tag problems with relevant metadata (environment, component type, severity)
- Avoid overly sensitive rules that create noise

### 2. **Alerting Profiles**
- Group similar problems to reduce alert fatigue (e.g., "Group all network errors from same service")
- Use time windows to consolidate transient issues (5-15 minute windows typical)
- Implement severity-based differentiation (CRITICAL gets escalated immediately)
- Use tag-based rules to handle different environments differently

### 3. **Problem Notifications**
- Route different severity levels to appropriate channels
- Implement escalation: Start with Slack, escalate to PagerDuty if unacknowledged
- Tag-based routing to send notifications to relevant teams
- Avoid duplicate notifications across channels for same problem

---

## Understanding Downloaded Settings Files

When you run `download_settings.py`, each schema will produce folders containing JSON files:

### Anomaly Detection Files
- Multiple `.json` files, each representing one anomaly detection rule
- Contains metric keys, thresholds, baseline configurations, and severity levels

### Alerting Profile Files
- Typically fewer files than anomaly detection
- Each file represents a complete alerting profile with multiple rules
- Contains grouping logic, time windows, and severity filters

### Notification Files
- Multiple `.json` files for different notification configurations
- Each file represents one notification rule or integration configuration
- Contains channel information, escalation paths, and filters

---

## Common Issues & Troubleshooting

| Issue | Likely Cause | Check These Settings |
|-------|--------------|----------------------|
| Too many alerts (alert fatigue) | Anomaly detection too sensitive OR alerting profile not grouping | Adjust baseline deviations; increase alerting profile time windows |
| Alerts not firing | Detection enabled but alerting profile filtering them out | Check alerting profile filter criteria and severity levels |
| Some teams not receiving alerts | Notification rule filters too restrictive | Review tag-based filtering in notification rules |
| Duplicate notifications | Multiple notification rules for same problem | Consolidate or make notification filters more specific |
| Delayed alerts | Alerting profile delay window too long | Reduce delayInMinutes setting |

---

## References

- **Dynatrace Anomaly Detection:** https://docs.dynatrace.com/docs/setup-and-configuration/setup-on-premises/configuration/anomaly-detection
- **Alerting Profiles:** https://docs.dynatrace.com/docs/setup-and-configuration/setup-on-premises/configuration/alerting-profiles
- **Problem Notifications:** https://docs.dynatrace.com/docs/setup-and-configuration/setup-on-premises/configuration/problem-notifications

---

**Created:** January 31, 2026  
**Purpose:** Guide for understanding Dynatrace classic alert flow settings schemas
