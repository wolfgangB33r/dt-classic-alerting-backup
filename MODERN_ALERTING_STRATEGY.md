# Dynatrace Modern Alerting Strategy - DQL Detectors & Workflows

## Overview

The new alerting strategy replaces the classic three-layer approach with a more flexible, code-first architecture:
- **DQL-based anomaly detectors** for problem detection with custom logic
- **Dynatrace Workflows** for orchestrating notifications and remediation actions
- **Direct trigger filtering** in workflows eliminating need for separate alerting profiles
- **Native integrations** for email, JIRA, Slack, PagerDuty, and 100+ other systems

This approach provides better control, flexibility, and maintainability compared to classic alerting.

---

## Architecture Overview

### Classic Alerting (Three-Layer Approach)
```
Metric Anomaly Detection
        ↓
Alerting Profile (Group & Filter)
        ↓
Problem Notifications (Route to Channel)
```

### Modern Alerting (Two-Layer Approach)
```
DQL Anomaly Detector (Detection + Custom Logic)
        ↓
Dynatrace Workflow (Filter + Multi-Action Orchestration)
        ├── Send Email
        ├── Create JIRA Ticket
        ├── Post to Slack
        ├── Trigger Remediation
        └── Run Custom Scripts
```

---

## Key Components

### 1. DQL-Based Anomaly Detectors

**Purpose:** Define detection logic using Dynatrace Query Language (DQL)

**Advantages over Classic:**
- Query complex conditions across metrics, logs, and traces
- Combine multiple data sources in one detector
- Use custom thresholds and algorithms
- Apply functions like aggregations, comparisons, and calculations
- Version control and code review friendly (plain text queries)

**Example DQL Detector:**
```dql
fetch builtin:host.cpu.usage
| filter in(host.name, "web-prod-*")
| fields host.name, cpu_usage = value
| stats avg(cpu_usage) as avg_cpu by host.name
| filter avg_cpu > 85
```

**Configuration Structure:**
```json
{
  "displayName": "High CPU on Production Hosts",
  "dqlQuery": "fetch builtin:host.cpu.usage | filter in(host.name, \"web-prod-*\") | stats avg(value) as avg_cpu | filter avg_cpu > 85",
  "severityLevel": "critical",
  "evaluationFrequency": "5m",
  "enabled": true
}
```

**Severity Levels:** `informational`, `warning`, `critical`

---

### 2. Dynatrace Workflows

**Purpose:** Orchestrate multi-step actions triggered by problems

**Trigger Types:**
- **Problem trigger:** Fires when problems are created, updated, or resolved
- **Schedule trigger:** Runs at fixed intervals
- **Webhook trigger:** Receives external events

**Workflow Structure:**
```yaml
Trigger: Problem created with filter
├─ Condition: Filter problems by severity/tags/entity type
├─ Action 1: Send Email with dynamic content
├─ Action 2: Create JIRA Ticket
├─ Action 3: Post to Slack
├─ Action 4: Trigger Remediation Script
└─ Action N: Custom integration
```

**Problem Filter in Workflow Trigger:**
```json
{
  "displayName": "Production Incident Response",
  "trigger": {
    "type": "problem",
    "filters": {
      "eventType": "CREATED",
      "severityLevel": "CRITICAL",
      "problemType": "AVAILABILITY",
      "tags": {
        "environment": ["production"],
        "team": ["platform"]
      },
      "affectedEntities": {
        "types": ["SERVICE", "APPLICATION"]
      }
    }
  },
  "tasks": [
    {
      "type": "send_email",
      "recipients": ["team@example.com"],
      "subject": "🚨 {ProblemTitle}",
      "body": "Problem ID: {ProblemID}\nSeverity: {Severity}\nAffected: {AffectedEntities}"
    },
    {
      "type": "create_jira_ticket",
      "project": "OPS",
      "issueType": "Incident",
      "summary": "{ProblemTitle}",
      "description": "{ProblemDetails}",
      "priority": "High"
    },
    {
      "type": "post_slack",
      "channel": "#incidents",
      "message": "Critical incident detected: {ProblemTitle}"
    }
  ]
}
```

**Available Actions:**
- Email notifications
- JIRA ticket creation
- Slack/Teams/Discord messages
- PagerDuty incidents
- ServiceNow incidents
- Webhook calls
- Script execution
- Custom HTTP requests
- Database updates
- And 100+ native integrations

---

## Migration Guide: Classic → Modern Alerting

### Step 1: Analyze Current Configuration

**Export classic alerting setup:**
```bash
# Download current configs using download_settings.py
python download_settings.py
```

**Review the three layers:**
1. `downloaded_settings/builtin_anomaly-detection.metric-events/` - Detection rules
2. `downloaded_settings/builtin_alerting.profile/` - Grouping/filtering rules
3. `downloaded_settings/builtin_problem.notifications/` - Notification channels

---

### Step 2: Map Classic to Modern Components

#### Classic Layer 1: Anomaly Detection Rules
**→ Becomes:** DQL-based Detector

**Mapping:**
| Classic | Modern | Example |
|---------|--------|---------|
| Metric + Threshold | DQL Query | `fetch builtin:host.cpu.usage \| filter value > 85` |
| Baseline deviation | DQL stats + filter | `\| stats avg(value) as baseline \| filter value > baseline * 1.5` |
| Severity level | severityLevel field | `"severityLevel": "critical"` |
| Enabled/disabled | enabled field | `"enabled": true` |

**Example Transformation:**

Classic (metric-based):
```json
{
  "name": "High CPU Detection",
  "metricKey": "builtin:host.cpu.usage",
  "alertConditions": [{
    "baselineType": "BASELINE_BASED",
    "deviations": 3
  }],
  "severityLevel": "CRITICAL"
}
```

Modern (DQL-based):
```json
{
  "displayName": "High CPU Detection",
  "dqlQuery": "fetch builtin:host.cpu.usage | stats avg(value) as cpu_avg | filter cpu_avg > 85",
  "severityLevel": "critical",
  "evaluationFrequency": "5m"
}
```

---

#### Classic Layer 2: Alerting Profiles
**→ Becomes:** Workflow Problem Trigger Filter

**Mapping:**
| Classic | Modern | Location |
|---------|--------|----------|
| Severity rule | severityLevel filter | `trigger.filters.severityLevel` |
| Tag filter | tags filter | `trigger.filters.tags` |
| Delay in minutes | (removed - direct delivery) | N/A |
| Event consolidation | (removed - simpler model) | N/A |

**Example Transformation:**

Classic (profile-based grouping):
```json
{
  "displayName": "Team Linz",
  "severityRules": [{
    "severityLevel": "AVAILABILITY",
    "delayInMinutes": 5,
    "tagFilter": ["AppTeam"]
  }]
}
```

Modern (workflow trigger filter):
```json
{
  "displayName": "Team Linz Workflow",
  "trigger": {
    "type": "problem",
    "filters": {
      "severityLevel": "AVAILABILITY",
      "tags": {
        "team": ["linz"]
      },
      "eventType": "CREATED"
    }
  }
}
```

---

#### Classic Layer 3: Problem Notifications
**→ Becomes:** Workflow Actions

**Mapping:**
| Classic | Modern | Example |
|---------|--------|---------|
| Email recipients | send_email action | `{"type": "send_email", "recipients": []}` |
| Email subject/body | Template variables | `{ProblemTitle}`, `{ProblemID}` |
| Webhook URL | http_request action | `{"type": "http_request", "url": "..."}` |
| Custom payload | body/payload field | Custom JSON/text |

**Example Transformation:**

Classic (email notification):
```json
{
  "type": "EMAIL",
  "displayName": "Team Email Notification",
  "emailNotification": {
    "recipients": ["team@example.com"],
    "subject": "{State} Problem {ProblemID}: {ImpactedEntity}",
    "body": "{ProblemDetailsHTML}"
  },
  "alertingProfile": "..."
}
```

Modern (workflow email action):
```json
{
  "displayName": "Team Incident Response",
  "trigger": { /* ... */ },
  "tasks": [{
    "type": "send_email",
    "recipients": ["team@example.com"],
    "subject": "🚨 {ProblemTitle}",
    "body": "Problem: {ProblemID}\nEntity: {ImpactedEntity}\nDetails: {ProblemDetails}"
  }]
}
```

---

### Step 3: Create New DQL Detectors

For each anomaly detection rule in your classic setup:

1. **Extract the metric key** (e.g., `builtin:host.cpu.usage`)
2. **Identify the threshold** (e.g., baseline + 3 deviations or static value)
3. **Convert to DQL query:**

```dql
fetch builtin:host.cpu.usage
| filter in(dt.entity.host, array("HOST-123", "HOST-456"))  // optional: filter specific entities
| stats avg(value) as metric_value
| filter metric_value > threshold_value
```

4. **Set severity** based on original rule severity
5. **Create detector** in Dynatrace Settings → Anomaly Detection → DQL Detectors

---

### Step 4: Create Workflows to Replace Alerting Profiles + Notifications

For each combination of (Alerting Profile + Notification):

1. **Create new workflow** in Dynatrace Settings → Workflows
2. **Add problem trigger** with filters from alerting profile
3. **Add actions** from all notifications bound to that profile

**Example Complete Migration:**

Classic Setup:
- Detector: "High Memory Usage"
- Profile: "Production" (tag filter: env=prod)
- Notifications: 
  - Email to ops@company.com
  - Webhook to incident system

Modern Setup:
- DQL Detector: "High Memory Usage"
- Workflow: "Production Memory Alert"
  - Trigger filter: `tags.environment = "production"`
  - Action 1: Send email to ops@company.com
  - Action 2: HTTP request to incident system

---

### Step 5: Configure Workflow Actions

**Common Action Examples:**

**1. Send Email:**
```json
{
  "type": "send_email",
  "recipients": ["${EVENT.owner}@company.com"],
  "subject": "Alert: {ProblemTitle}",
  "body": "Problem ID: {ProblemID}\nEntity: {ImpactedEntity}\nTime: {CreationTime}"
}
```

**2. Create JIRA Ticket:**
```json
{
  "type": "create_jira_issue",
  "integration": "jira-prod",
  "project": "OPS",
  "issueType": "Incident",
  "summary": "{ProblemTitle}",
  "description": "{ProblemDetails}",
  "priority": "High",
  "labels": ["dynatrace", "{ProblemType}"]
}
```

**3. Post to Slack:**
```json
{
  "type": "send_slack_message",
  "channel": "#incidents",
  "message": "🚨 Critical: {ProblemTitle}\nEntity: {ImpactedEntity}\n<Link>{ProblemURL}</Link>"
}
```

**4. HTTP Webhook:**
```json
{
  "type": "http_request",
  "url": "https://external-system.com/incidents",
  "method": "POST",
  "headers": {"Authorization": "Bearer ${SECRET.api_token}"},
  "body": {
    "title": "{ProblemTitle}",
    "severity": "{Severity}",
    "entity": "{ImpactedEntity}"
  }
}
```

---

## Key Advantages of Modern Approach

| Feature | Classic | Modern |
|---------|---------|--------|
| **Complexity** | 3 layers to manage | 2 layers (detector + workflow) |
| **Filtering** | Separate profile layer | Direct in workflow trigger |
| **Multi-channel** | Multiple notification objects per profile | Single workflow with multiple actions |
| **Custom logic** | Limited to predefined rules | Full DQL query language |
| **Integrations** | Limited, predefined types | 100+ native integrations |
| **Flexibility** | Rigid structure | Complete control via code |
| **Version control** | Difficult (API-only) | Easy (export/import as JSON) |
| **Maintenance** | Complex dependency chain | Simple, linear flow |
| **Remediation** | Notification only | Actions can trigger remediation |
| **Conditional logic** | None | Full workflow conditions |

---

## Migration Checklist

- [ ] Export classic alerting configuration (anomaly detection, profiles, notifications)
- [ ] Document current alert matrix (which detectors → which profiles → which notifications)
- [ ] For each detector: Create equivalent DQL detector
- [ ] For each (profile + notification) pair: Create workflow
- [ ] Test workflows with existing problems
- [ ] Validate notification delivery to all channels
- [ ] Document new workflow architecture
- [ ] Set timeline for classic alerting deprecation
- [ ] Train team on new workflow system
- [ ] Archive classic configuration backups

---

## Template: Complete Modern Workflow Configuration

```json
{
  "displayName": "Production Critical Alert Response",
  "enabled": true,
  "description": "Handles critical problems in production environment",
  "trigger": {
    "type": "problem",
    "filters": {
      "eventType": "CREATED",
      "severityLevel": "CRITICAL",
      "tags": {
        "environment": ["production"],
        "monitored": ["true"]
      },
      "affectedEntities": {
        "types": ["SERVICE", "APPLICATION", "DATABASE"]
      }
    }
  },
  "tasks": [
    {
      "id": "email_notification",
      "type": "send_email",
      "recipients": ["${VARIABLE.team_email}"],
      "subject": "🚨 CRITICAL: {ProblemTitle}",
      "body": "Problem: {ProblemTitle}\nID: {ProblemID}\nEntity: {ImpactedEntity}\nTime: {CreationTime}"
    },
    {
      "id": "jira_ticket",
      "type": "create_jira_issue",
      "integration": "jira-production",
      "project": "OPS",
      "issueType": "Incident",
      "summary": "{ProblemTitle}",
      "description": "{ProblemDetails}",
      "priority": "Highest"
    },
    {
      "id": "slack_alert",
      "type": "send_slack_message",
      "channel": "#incidents",
      "message": "⚠️ Critical Alert\n{ProblemTitle}\n<{ProblemURL}|View Details>"
    },
    {
      "id": "pagerduty_incident",
      "type": "create_pagerduty_incident",
      "integration": "pagerduty-prod",
      "title": "{ProblemTitle}",
      "urgency": "high"
    },
    {
      "id": "escalation_call",
      "type": "http_request",
      "url": "https://incident-commander.company.com/api/escalate",
      "method": "POST",
      "body": {
        "problem_id": "{ProblemID}",
        "severity": "critical",
        "timestamp": "{CreationTime}"
      }
    }
  ]
}
```

---

## References

- [Dynatrace DQL Documentation](https://docs.dynatrace.com/docs/platform/grail/dynatrace-query-language)
- [Dynatrace Workflows](https://docs.dynatrace.com/docs/platform/automation/workflows)
- [Anomaly Detection with DQL](https://docs.dynatrace.com/docs/platform/anomaly-detection/anomaly-detection-with-dql)
- [Workflow Actions & Integrations](https://docs.dynatrace.com/docs/platform/automation/workflows/actions)

---

**Created:** February 1, 2026  
**Purpose:** Guide for migrating from classic alerting to modern DQL-based alerting with Dynatrace Workflows
