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
**Purpose:** Controls how problems are grouped and filtered

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
**Purpose:** Routes problems to external systems and users based on alerting profiles

**Role in Alert Flow:**
- The final delivery stage of the alert flow
- Binds notification channels to specific alerting profiles (not direct problem filtering)
- Routes problems to email, webhooks, integrations, and external systems
- Controls notification payload, recipients, and delivery options
- Enables alert state tracking (open/closed problem notifications)

**Key Characteristics:**
- **Profile-based routing:** Each notification rule is explicitly tied to an alerting profile via `alertingProfile` field
- **Type-based configuration:** Different notification types (EMAIL, WEBHOOK, etc.) have type-specific settings
- **Template system:** Uses placeholders like `{State}`, `{ProblemID}`, `{ImpactedEntity}`, `{ProblemDetailsHTML}` for dynamic content
- **State notifications:** Can notify on problem creation and/or closure with `notifyClosedProblems` flag
- **Custom payloads:** Webhooks support custom JSON/XML payloads with template variables
- **Certificate handling:** Can accept/reject untrusted SSL certificates for webhook destinations

**Real-World Structure from Downloaded Settings:**

**Email Notification Example:**
```json
{
  "objectId": "vu9U3hXa3q0AAAABAB1idWlsdGluOnByb2JsZW0ubm90aWZpY2F0aW9ucwAGdGVuYW50...",
  "value": {
    "enabled": true,
    "type": "EMAIL",
    "displayName": "example email",
    "emailNotification": {
      "recipients": ["bob@example.com"],
      "ccRecipients": [],
      "bccRecipients": [],
      "subject": "{State} Problem {ProblemID}: {ImpactedEntity}",
      "notifyClosedProblems": true,
      "body": "{ProblemDetailsHTML}"
    },
    "alertingProfile": "vu9U3hXa3q0AAAABABhidWlsdGluOmFsZXJ0aW5nLnByb2ZpbGU..."
  }
}
```

**Webhook Notification Example:**
```json
{
  "objectId": "vu9U3hXa3q0AAAABAB1idWlsdGluOnByb2JsZW0ubm90aWZpY2F0aW9ucwAGdGVuYW50...",
  "value": {
    "enabled": true,
    "type": "WEBHOOK",
    "displayName": "example webhook",
    "webHookNotification": {
      "url": "https://example.com",
      "acceptAnyCertificate": false,
      "notifyEventMergesEnabled": false,
      "notifyClosedProblems": true,
      "headers": [],
      "payload": "{\n\"State\":\"{State}\",\n\"ProblemID\":\"{ProblemID}\",\n\"ProblemTitle\":\"{ProblemTitle}\"\n}"
    },
    "alertingProfile": "vu9U3hXa3q0AAAABABhidWlsdGluOmFsZXJ0aW5nLnByb2ZpbGU..."
  }
}
```

**Key Structural Insights:**
- Each notification object is a **complete, self-contained notification rule** (not a reusable template)
- The `alertingProfile` field creates a **direct 1:1 binding** to an alerting profile
- Multiple notification objects can reference the same alerting profile for multi-channel delivery
- The notification inherits problem scope and filtering from its linked alerting profile
- Template variables are substituted when problems match the linked alerting profile's criteria

---

## The Complete Alert Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    PROBLEM DETECTION LAYER                      │
│         builtin:anomaly-detection.metric-events                 │
│  (Metric Thresholds → Anomalies → Initial Problem Creation)     │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ Problem with tags/severity
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ALERT MANAGEMENT LAYER                        │
│              builtin:alerting.profile                           │
│      (Filter by severity/tags → Consolidate → Ready)            │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ Problem passes alerting profile filter
                     ▼
    ┌────────────────┴────────────────┐
    │                                 │
    ▼                                 ▼
┌─────────────────────┐       ┌─────────────────────┐
│  EMAIL NOTIFICATION │       │ WEBHOOK NOTIFICATION│
│ (Bound to Alert     │       │ (Bound to Alert     │
│  Profile via ID)    │       │  Profile via ID)    │
└─────────────────────┘       └─────────────────────┘
    │                                 │
    │ Renders template                │ Sends JSON payload
    │ with problem data               │ with problem data
    │                                 │
    ▼                                 ▼
  EMAIL DELIVERY           EXTERNAL SYSTEM INTEGRATION
  (bob@example.com)        (https://example.com)
```

**Key Relationship:** Each `builtin:problem.notifications` object explicitly references a specific `builtin:alerting.profile` through the `alertingProfile` field. Problems only reach that notification channel if they pass the linked alerting profile's filters.

---

## How They Work Together

### Example Scenario: High CPU Usage Alert

1. **Detection (anomaly-detection.metric-events)**
   - Rule monitors host CPU usage
   - Detects that CPU has exceeded baseline by 4 deviations for 5 consecutive minutes
   - Creates a CRITICAL problem with tags: `environment:production`, `type:performance`

2. **Filtering (alerting.profile)**
   - "Team Linz" alerting profile's rule matches: severity=AVAILABILITY and tagFilter includes AppTeam
   - Determines if this problem should trigger notifications linked to this profile
   - Forwards to all notification objects that reference this alerting profile

3. **Notification (problem.notifications)**
   - Email notification object references the "Team Linz" alerting profile
   - Problem matches, so email is sent to bob@example.com with template variables substituted
   - Webhook notification object also references the "Team Linz" alerting profile  
   - Custom JSON payload is POSTed to https://example.com with problem details
   - Both notifications inherit the alerting profile's filtering logic

---

## Key Relationships & Dependencies

### Anomaly Detection → Alerting Profile
- **Dependency:** Alerting profiles work ONLY on problems created by anomaly detection rules
- **Interaction:** The severity and tags from anomaly detection are used by alerting profiles to filter and group
- **Example:** If anomaly detection doesn't create a problem, the alerting profile never triggers

### Alerting Profile → Problem Notifications (Explicit Binding)
- **Dependency:** Each problem notification object contains an `alertingProfile` field with the ID of its associated alerting profile
- **Interaction:** Problem notifications only fire on problems that BOTH:
  1. Pass through the linked alerting profile's filters (severity, tags, delays)
  2. Match the notification's specific type/configuration
- **One-to-Many Pattern:** One alerting profile can be referenced by multiple notification objects (email, webhook, etc.)
- **Example:** 
  - Alerting profile "Team Linz" has AVAILABILITY severity rule with AppTeam tag filter
  - Email notification "Team Linz Email" references this profile
  - Webhook notification "Team Linz Webhook" also references this profile
  - Both notifications fire only when problems match the profile's rules

### All Three Together
- **Complete lifecycle:** Anomaly Detection (WHEN) → Alerting Profile (WHAT/HOW_MUCH) → Notifications (WHERE/TO_WHOM)
- **Explicit routing:** Notifications don't auto-discover problems; they're explicitly bound to profiles
- **Tag-based routing:** Tags from detection → used by alerting profiles for filtering → inherited by notifications
- **Multi-channel support:** Multiple notifications can be bound to same profile for multi-channel delivery without rule duplication

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
- Each `.json` file is one complete notification rule/integration (EMAIL, WEBHOOK, etc.)
- Contains the `alertingProfile` field showing which profile this notification is bound to
- Template variables are rendered when problems from that profile are received
- Multiple notification files can reference the same alerting profile for multi-channel delivery
- Example structure includes email recipients, webhook URLs, custom JSON payloads, and delivery options

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
