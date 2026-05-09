# AI-Powered Observability Platform - Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OpenShift ROSA Cluster                               │
│                    Namespace: nilabja-haldar-dev                             │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                        User Interface Layer                             │ │
│  │                                                                          │ │
│  │  ┌──────────────────┐         ┌──────────────────┐                     │ │
│  │  │   Next.js UI     │         │  Chat Interface  │                     │ │
│  │  │  (E-commerce)    │◄────────┤  (Agent UI)      │                     │ │
│  │  │  Port: 3000      │         │  WebSocket       │                     │ │
│  │  └────────┬─────────┘         └────────┬─────────┘                     │ │
│  │           │                             │                               │ │
│  │           │ OpenShift Route             │ OpenShift Route               │ │
│  └───────────┼─────────────────────────────┼───────────────────────────────┘ │
│              │                             │                                 │
│  ┌───────────▼─────────────────────────────▼───────────────────────────────┐ │
│  │                      Application Layer                                   │ │
│  │                                                                           │ │
│  │  ┌──────────────────┐         ┌──────────────────────────────────────┐  │ │
│  │  │  FastAPI Backend │         │    Supervisor Agent                  │  │ │
│  │  │  Port: 8000      │         │    (LangChain Router)                │  │ │
│  │  │  - Products API  │         │    Port: 8080                        │  │ │
│  │  │  - Orders API    │         └──────────────┬───────────────────────┘  │ │
│  │  │  - Users API     │                        │                          │ │
│  │  │  - Chaos Toggle  │                        │ Routes to:               │ │
│  │  └────────┬─────────┘                        │                          │ │
│  │           │                         ┌────────┴────────┐                 │ │
│  │           │                         │                 │                 │ │
│  │  ┌────────▼─────────┐      ┌───────▼──────┐  ┌──────▼────────┐        │ │
│  │  │   PostgreSQL     │      │ Observability│  │ Pod Recovery  │        │ │
│  │  │   Database       │      │    Agent     │  │    Agent      │        │ │
│  │  │   Port: 5432     │      │  Port: 8081  │  │  Port: 8082   │        │ │
│  │  │   PVC: 10GB      │      └──────┬───────┘  └───────┬───────┘        │ │
│  │  │   (EFS CSI)      │             │                  │                 │ │
│  │  └──────────────────┘             │                  │                 │ │
│  │                            ┌───────▼──────────────────▼──────┐         │ │
│  │                            │   Backup/Restore Agent           │         │ │
│  │                            │   Port: 8083                     │         │ │
│  │                            └──────────────┬───────────────────┘         │ │
│  └───────────────────────────────────────────┼───────────────────────────┘ │
│                                               │                             │
│  ┌───────────────────────────────────────────▼───────────────────────────┐ │
│  │                      AI Agent Infrastructure                            │ │
│  │                                                                          │ │
│  │  ┌──────────────────┐         ┌──────────────────┐                     │ │
│  │  │  Chroma Vector   │         │   LLM Provider   │                     │ │
│  │  │  Store (Memory)  │         │   (Groq/OpenAI)  │                     │ │
│  │  │  PVC: 5GB        │         │   External API   │                     │ │
│  │  └──────────────────┘         └──────────────────┘                     │ │
│  │                                                                          │ │
│  │  Agent Tools:                                                           │ │
│  │  ┌────────────────────────────────────────────────────────────────┐    │ │
│  │  │ • oc (kubectl)  • velero  • loki_query  • thanos_query         │    │ │
│  │  │ • grafana_api   • slack_post  • confluence_create_draft         │    │ │
│  │  │ • EXECUTE guard: Requires explicit approval for mutations       │    │ │
│  │  └────────────────────────────────────────────────────────────────┘    │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Observability Stack                               │   │
│  │                                                                       │   │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │   │
│  │  │  Prometheus  │───▶│    Thanos    │───▶│ Object Store │          │   │
│  │  │  (Metrics)   │    │   Sidecar    │    │   (EFS CSI)  │          │   │
│  │  │  Port: 9090  │    │  + Query     │    │              │          │   │
│  │  └──────┬───────┘    └──────────────┘    └──────────────┘          │   │
│  │         │                                                            │   │
│  │         │ Scrapes                                                    │   │
│  │         │                                                            │   │
│  │  ┌──────▼───────────────────────────────────────────────┐           │   │
│  │  │  ServiceMonitors / PodMonitors                       │           │   │
│  │  │  • Frontend metrics  • Backend metrics               │           │   │
│  │  │  • Database metrics  • Agent metrics                 │           │   │
│  │  └──────────────────────────────────────────────────────┘           │   │
│  │                                                                       │   │
│  │  ┌──────────────┐    ┌──────────────┐                               │   │
│  │  │    Loki      │◄───│   Promtail   │                               │   │
│  │  │   (Logs)     │    │  (Collector) │                               │   │
│  │  │  Port: 3100  │    │  DaemonSet   │                               │   │
│  │  └──────┬───────┘    └──────────────┘                               │   │
│  │         │                                                            │   │
│  │         │                                                            │   │
│  │  ┌──────▼───────────────────────────────────────────────┐           │   │
│  │  │                   Grafana                             │           │   │
│  │  │              (Visualization)                          │           │   │
│  │  │               Port: 3000                              │           │   │
│  │  │  • Metrics Dashboards  • Log Explorer                │           │   │
│  │  │  • Alert Visualization • Agent-Generated Dashboards  │           │   │
│  │  └───────────────────────────────────────────────────────┘           │   │
│  │                                                                       │   │
│  │  ┌──────────────┐    ┌──────────────┐                               │   │
│  │  │ Alertmanager │───▶│    Slack     │                               │   │
│  │  │  Port: 9093  │    │   Webhook    │                               │   │
│  │  └──────────────┘    └──────────────┘                               │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    Backup & Restore Layer                            │  │
│  │                                                                       │  │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │  │
│  │  │    Velero    │───▶│   Backup     │───▶│ Object Store │          │  │
│  │  │  Port: 8085  │    │  Schedule    │    │   (EFS CSI)  │          │  │
│  │  │              │    │   (Daily)    │    │              │          │  │
│  │  └──────────────┘    └──────────────┘    └──────────────┘          │  │
│  │                                                                       │  │
│  │  Backup Targets:                                                     │  │
│  │  • PostgreSQL PVC  • Chroma Vector Store PVC                        │  │
│  │  • ConfigMaps      • Secrets                                         │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         External Integrations                                │
│                                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │    Slack     │    │  Confluence  │    │  Container   │                  │
│  │  Webhooks    │    │     API      │    │   Registry   │                  │
│  │  (Alerts)    │    │ (Postmortems)│    │ icr.io/...   │                  │
│  └──────────────┘    └──────────────┘    └──────────────┘                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Interactions

### 1. User Request Flow
```
User → Next.js UI → FastAPI Backend → PostgreSQL
                                    ↓
                              Prometheus (metrics)
                              Loki (logs)
```

### 2. Agent Request Flow (Chat UI - Query Only)
```
User → Chat UI → Supervisor Agent → Route to Specialist Agent
                                   ↓
                          Observability Agent → Query Prometheus/Loki/Grafana
                                   ↓
                          Return Results to Chat UI
```

### 3. Issue Detection & Resolution Flow (Slack - Human-in-the-Loop)
```
Issue Detected (Alerts/Metrics/Logs)
         ↓
Observability Agent analyzes issue
         ↓
Generate resolution steps
         ↓
Send Slack notification with [Approve] [Deny] buttons
         ↓
Wait for human decision (5 min timeout)
         ↓
    ┌────┴────┐
    ↓         ↓
APPROVED   DENIED
    ↓         ↓
Execute    Send manual
corrective  resolution
actions     steps only
    ↓         ↓
Monitor    No action
execution   taken
    ↓         ↓
Send Slack update with results
    ↓
Create Confluence incident report
```

### 4. Observability Flow
```
Application Pods → Promtail → Loki → Grafana
                ↓
           ServiceMonitor → Prometheus → Thanos → Grafana
                                      ↓
                              PrometheusRules → Alertmanager → Slack
```

### 5. Backup Flow
```
Velero Schedule (Daily) → Backup PVCs/Resources → Object Store (EFS)
                                                 ↓
                                    Backup/Restore Agent monitors
                                                 ↓
                                    Slack notification on completion
```

## Data Flow

### Metrics Path
```
App (Prometheus client) → ServiceMonitor → Prometheus → Thanos Sidecar → Object Store
                                                      ↓
                                              Thanos Query ← Grafana
                                                      ↓
                                              Observability Agent (PromQL)
```

### Logs Path
```
App (stdout/stderr) → Promtail → Loki → Grafana
                                      ↓
                              Observability Agent (LogQL)
```

### Agent Memory Path
```
Agent Interaction → LangChain → Chroma Vector Store (PVC)
                              ↓
                    Context retrieval for future queries
```

## Security & Isolation

### Namespace Scope
- All resources in `nilabja-haldar-dev` namespace
- No cluster-wide RBAC or operators
- ServiceAccount per agent with minimal Role permissions

### Execution Guard
```
Agent Tool Call → Execution Guard Check
                ↓
        PLAN_ONLY (default) → Return plan, no execution
                ↓
        EXECUTE: true → Require user approval
                ↓
        Approved → Execute with audit log
```

### Network Policies
```
Frontend → Backend (allowed)
Backend → Database (allowed)
Agents → Kubernetes API (namespace-scoped)
Agents → Observability Stack (read-only)
Agents → Velero (backup/restore only)
```

## Storage Architecture

### Persistent Volumes
```
PostgreSQL PVC (10GB, EFS CSI, RWO)
    ↓
Database data + WAL logs

Chroma Vector Store PVC (5GB, EFS CSI, RWO)
    ↓
Agent conversation memory

Thanos/Velero Object Store (EFS CSI)
    ↓
Long-term metrics + backups
```

## Deployment Architecture

### Helm Chart Structure
```
observability-stack/
    ↓
Prometheus, Thanos, Loki, Promtail, Grafana, Alertmanager, Velero

ecommerce-app/
    ↓
Frontend, Backend, PostgreSQL

ai-agents/
    ↓
Supervisor, Observability, Pod Recovery, Backup/Restore, Chroma
```

### Deployment Order
1. Observability Stack (monitoring infrastructure)
2. E-commerce App (generates signals)
3. AI Agents (consume signals, take actions)

## Scalability Considerations

### Horizontal Scaling
- Frontend: 2-3 replicas (stateless)
- Backend: 2-3 replicas (stateless)
- Agents: 1 replica each (stateful with vector store)

### Vertical Scaling
- PostgreSQL: Single instance (demo constraint)
- Prometheus: Memory-intensive (metrics retention)
- Thanos: Offloads historical data

## Monitoring the Monitors

### Self-Observability
```
Observability Stack → ServiceMonitors for itself
                   ↓
Prometheus scrapes Prometheus, Loki, Grafana
                   ↓
Alerts on observability stack health
                   ↓

## Human-in-the-Loop Architecture

### Slack Integration for Issue Resolution

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Issue Detection & Resolution Workflow                     │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  Step 1: Issue Detection                                               │ │
│  │                                                                          │ │
│  │  Prometheus Alerts ──┐                                                  │ │
│  │  Metric Thresholds ──┼──► Observability Agent                          │ │
│  │  Log Errors ─────────┘         │                                        │ │
│  │                                 ↓                                        │ │
│  │                        Analyze Issue Severity                           │ │
│  │                                 ↓                                        │ │
│  │                        Generate Resolution Steps                        │ │
│  └────────────────────────────────┼─────────────────────────────────────┘ │
│                                    │                                         │
│  ┌────────────────────────────────▼─────────────────────────────────────┐ │
│  │  Step 2: Slack Notification (with Interactive Buttons)               │ │
│  │                                                                        │ │
│  │  ┌──────────────────────────────────────────────────────────────┐    │ │
│  │  │  🚨 Issue Detected: High Error Rate                          │    │ │
│  │  │  Severity: Critical | Namespace: nilabja-haldar-dev          │    │ │
│  │  │  Affected: backend-api pods                                  │    │ │
│  │  │                                                               │    │ │
│  │  │  Resolution Steps:                                           │    │ │
│  │  │  1. Restart affected pods                                    │    │ │
│  │  │  2. Scale deployment to 3 replicas                           │    │ │
│  │  │  3. Clear cache                                              │    │ │
│  │  │                                                               │    │ │
│  │  │  [✅ Approve]  [❌ Deny]                                      │    │ │
│  │  └──────────────────────────────────────────────────────────────┘    │ │
│  │                                                                        │ │
│  │  Channel: #observability-alerts                                       │ │
│  └────────────────────────────────┬───────────────────────────────────┘ │
│                                    │                                       │
│  ┌────────────────────────────────▼───────────────────────────────────┐ │
│  │  Step 3: Wait for Human Decision (5 min timeout)                   │ │
│  │                                                                      │ │
│  │  Agent blocks and waits for Slack interactive message response     │ │
│  │  Timeout = DENY (safety default)                                   │ │
│  └────────────────────────────────┬───────────────────────────────────┘ │
│                                    │                                       │
│                         ┌──────────┴──────────┐                            │
│                         ↓                     ↓                            │
│  ┌──────────────────────────────┐  ┌──────────────────────────────────┐  │
│  │  APPROVED Path               │  │  DENIED Path                     │  │
│  │                              │  │                                  │  │
│  │  1. Execute corrective       │  │  1. NO actions executed          │  │
│  │     actions:                 │  │                                  │  │
│  │     • Restart pods           │  │  2. Send manual resolution       │  │
│  │     • Scale deployment       │  │     steps to Slack:              │  │
│  │     • Clear cache            │  │     ```                          │  │
│  │                              │  │     oc rollout restart ...       │  │
│  │  2. Monitor execution        │  │     oc scale ...                 │  │
│  │                              │  │     ```                          │  │
│  │  3. Send Slack update:       │  │                                  │  │
│  │     ✅ Issue Resolved        │  │  3. Human performs manual        │  │
│  │     • Actions taken          │  │     steps if needed              │  │
│  │     • Current state          │  │                                  │  │
│  │     • Metrics improved       │  │                                  │  │
│  │                              │  │                                  │  │
│  │  4. Create Confluence        │  │                                  │  │
│  │     incident report          │  │                                  │  │
│  └──────────────────────────────┘  └──────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Chat UI vs Slack Separation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Communication Channel Separation                     │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  Chat UI (Observability Queries ONLY)                                  │ │
│  │                                                                          │ │
│  │  ✅ Allowed:                                                            │ │
│  │  • Query Prometheus metrics (PromQL)                                   │ │
│  │  • Query Loki logs (LogQL)                                             │ │
│  │  • View/create Grafana dashboards                                      │ │
│  │  • Explain metrics and logs                                            │ │
│  │  • Troubleshooting guidance                                            │ │
│  │  • Historical data analysis                                            │ │
│  │                                                                          │ │
│  │  ❌ NOT Allowed:                                                        │ │
│  │  • Issue notifications                                                  │ │
│  │  • Alert management                                                     │ │
│  │  • Approval workflows                                                   │ │
│  │  • Incident reports                                                     │ │
│  │  • Corrective action execution                                          │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  Slack (Issue Management & Human-in-the-Loop)                          │ │
│  │                                                                          │ │
│  │  ✅ Used for:                                                           │ │
│  │  • Issue detection notifications                                        │ │
│  │  • Alert routing and escalation                                         │ │
│  │  • Human approval workflows (Approve/Deny)                              │ │
│  │  • Corrective action results                                            │ │
│  │  • Incident status updates                                              │ │
│  │  • Manual resolution steps (when denied)                                │ │
│  │  • Links to Confluence incident reports                                 │ │
│  │                                                                          │ │
│  │  ❌ NOT Used for:                                                       │ │
│  │  • Ad-hoc observability queries                                         │ │
│  │  • Dashboard creation requests                                          │ │
│  │  • Metric exploration                                                   │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Approval Workflow State Machine

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Approval State Machine                               │
│                                                                               │
│                              ┌─────────────┐                                 │
│                              │   DETECTED  │                                 │
│                              │   (Issue)   │                                 │
│                              └──────┬──────┘                                 │
│                                     │                                        │
│                                     ↓                                        │
│                              ┌─────────────┐                                 │
│                              │  NOTIFIED   │                                 │
│                              │  (Slack)    │                                 │
│                              └──────┬──────┘                                 │
│                                     │                                        │
│                                     ↓                                        │
│                              ┌─────────────┐                                 │
│                              │   WAITING   │◄──── Timeout (5 min)           │
│                              │ (Approval)  │                                 │
│                              └──────┬──────┘                                 │
│                                     │                                        │
│                         ┌───────────┴───────────┐                            │
│                         ↓                       ↓                            │
│                  ┌─────────────┐         ┌─────────────┐                    │
│                  │  APPROVED   │         │   DENIED    │                    │
│                  └──────┬──────┘         └──────┬──────┘                    │
│                         │                       │                            │
│                         ↓                       ↓                            │
│                  ┌─────────────┐         ┌─────────────┐                    │
│                  │  EXECUTING  │         │   MANUAL    │                    │
│                  │  (Actions)  │         │  (Steps)    │                    │
│                  └──────┬──────┘         └──────┬──────┘                    │
│                         │                       │                            │
│                         ↓                       ↓                            │
│                  ┌─────────────┐         ┌─────────────┐                    │
│                  │  RESOLVED   │         │  PENDING    │                    │
│                  │  (Success)  │         │  (Manual)   │                    │
│                  └──────┬──────┘         └──────┬──────┘                    │
│                         │                       │                            │
│                         └───────────┬───────────┘                            │
│                                     ↓                                        │
│                              ┌─────────────┐                                 │
│                              │  DOCUMENTED │                                 │
│                              │ (Confluence)│                                 │
│                              └─────────────┘                                 │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Security & Audit Trail

**Approval Logging:**
- All approval requests logged to Confluence
- Timestamp, user, decision, and outcome recorded
- Audit trail for compliance and postmortems

**Safety Mechanisms:**
- Default timeout = DENY (fail-safe)
- No automated actions without explicit approval
- All actions reversible and logged
- Namespace-scoped permissions only

**Notification Channels:**
- Primary: #observability-alerts (Slack)
- Backup: Email notifications (optional)
- Escalation: On-call rotation (PagerDuty integration)
Agents can diagnose observability issues
```

## Chaos Engineering Integration

### Failure Injection Points
```
Backend API → /chaos/enable endpoint
           ↓
Simulates: slow queries, 500 errors, pod crashes
           ↓
Triggers alerts → Agent auto-remediation
```

## Key Design Principles

1. **Namespace Isolation**: All resources scoped to single namespace
2. **Helm-Based**: Repeatable, version-controlled deployments
3. **Agent Safety**: EXECUTE guard prevents accidental mutations
4. **Observable by Design**: Every component emits metrics/logs
5. **Stateful Resilience**: PVCs backed up daily via Velero
6. **Modular Architecture**: Independent Helm charts per layer
7. **Production-Realistic**: Real databases, real failures, real recovery