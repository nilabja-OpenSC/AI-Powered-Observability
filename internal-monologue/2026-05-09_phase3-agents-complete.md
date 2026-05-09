# Phase 3 Complete - AI Agent Helm Charts (32 files)

**Date:** 2026-05-09  
**Status:** Complete ✅

## Summary

Successfully created Helm charts for all 4 AI agents with comprehensive configurations, Kubernetes templates, and human-in-the-loop approval workflows.

## Completed Files (32 files)

### Phase 3A: Supervisor Agent (8 files) ✅
1. ✅ `charts/ai-agents/supervisor-agent/Chart.yaml`
2. ✅ `charts/ai-agents/supervisor-agent/values.yaml`
3. ✅ `charts/ai-agents/supervisor-agent/templates/deployment.yaml`
4. ✅ `charts/ai-agents/supervisor-agent/templates/service.yaml`
5. ✅ `charts/ai-agents/supervisor-agent/templates/serviceaccount.yaml`
6. ✅ `charts/ai-agents/supervisor-agent/templates/rbac.yaml`
7. ✅ `charts/ai-agents/supervisor-agent/templates/servicemonitor.yaml`
8. ✅ `charts/ai-agents/supervisor-agent/templates/route.yaml`

### Phase 3B: Observability Agent (8 files) ✅
1. ✅ `charts/ai-agents/observability-agent/Chart.yaml`
2. ✅ `charts/ai-agents/observability-agent/values.yaml`
3. ✅ `charts/ai-agents/observability-agent/templates/deployment.yaml`
4. ✅ `charts/ai-agents/observability-agent/templates/service.yaml`
5. ✅ `charts/ai-agents/observability-agent/templates/serviceaccount.yaml`
6. ✅ `charts/ai-agents/observability-agent/templates/rbac.yaml`
7. ✅ `charts/ai-agents/observability-agent/templates/servicemonitor.yaml`
8. ✅ `charts/ai-agents/observability-agent/templates/route.yaml`

### Phase 3C: Pod Recovery Agent (8 files) ✅
1. ✅ `charts/ai-agents/pod-recovery-agent/Chart.yaml`
2. ✅ `charts/ai-agents/pod-recovery-agent/values.yaml`
3. ✅ `charts/ai-agents/pod-recovery-agent/templates/deployment.yaml`
4. ✅ `charts/ai-agents/pod-recovery-agent/templates/service.yaml`
5. ✅ `charts/ai-agents/pod-recovery-agent/templates/serviceaccount.yaml`
6. ✅ `charts/ai-agents/pod-recovery-agent/templates/rbac.yaml`
7. ✅ `charts/ai-agents/pod-recovery-agent/templates/servicemonitor.yaml`
8. ✅ `charts/ai-agents/pod-recovery-agent/templates/route.yaml`

### Phase 3D: Backup/Restore Agent (8 files) ✅
1. ✅ `charts/ai-agents/backup-restore-agent/Chart.yaml`
2. ✅ `charts/ai-agents/backup-restore-agent/values.yaml`
3. ✅ `charts/ai-agents/backup-restore-agent/templates/deployment.yaml`
4. ✅ `charts/ai-agents/backup-restore-agent/templates/service.yaml`
5. ✅ `charts/ai-agents/backup-restore-agent/templates/serviceaccount.yaml`
6. ✅ `charts/ai-agents/backup-restore-agent/templates/rbac.yaml`
7. ✅ `charts/ai-agents/backup-restore-agent/templates/servicemonitor.yaml`
8. ✅ `charts/ai-agents/backup-restore-agent/templates/route.yaml`

## Cumulative Progress

**Total: 60 files completed (36%)**
- Phase 1: Platform & Observability Stack (30 files)
- Phase 2: E-commerce Application (6 files)
- Phase 3: AI Agent Helm Charts (32 files)
  - 3A: Supervisor Agent (8 files)
  - 3B: Observability Agent (8 files)
  - 3C: Pod Recovery Agent (8 files)
  - 3D: Backup/Restore Agent (8 files)

## Agent Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Chat UI (Next.js)                     │
│                  Natural Language Queries                    │
└──────────────────────────┬──────────────────────────────────┘
                           │ WebSocket/HTTP
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Supervisor Agent                          │
│              Intent Classification & Routing                 │
│         (OpenAI GPT-4 / Groq Llama-3.1-70b)                 │
└──────────┬────────────────┬────────────────┬────────────────┘
           │                │                │
           ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│Observability │  │Pod Recovery  │  │Backup/Restore│
│    Agent     │  │    Agent     │  │    Agent     │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│Prometheus    │  │Kubernetes    │  │Velero        │
│Thanos        │  │API           │  │Argo          │
│Loki          │  │              │  │Workflows     │
│Grafana       │  │              │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
       │                 │                 │
       └─────────────────┴─────────────────┘
                         │
                         ▼
                  ┌──────────────┐
                  │    Slack     │
                  │  Approval    │
                  │  Workflow    │
                  └──────────────┘
```

## Key Features Implemented

### 1. Supervisor Agent
**Purpose:** Route queries to specialist agents

**Capabilities:**
- Intent-based routing (observability, pod_recovery, backup_restore)
- Keyword matching for fast classification
- Confidence threshold: 0.7
- Fallback to Observability Agent
- Multi-agent collaboration support
- WebSocket support for real-time communication

**Configuration:**
- Port: 8080
- Replicas: 2 (HA)
- LLM: OpenAI GPT-4 (temp: 0.7) or Groq
- Vector Store: Chroma (supervisor-memory collection)

### 2. Observability Agent
**Purpose:** Query metrics/logs, detect issues, send notifications

**Capabilities:**
- Natural language to PromQL/LogQL generation
- Data source routing (Prometheus <6h, Thanos >6h)
- Issue detection (8 pre-configured rules)
- Slack notifications with severity levels
- Confluence documentation
- Dashboard creation in Grafana
- Query templates for Golden Signals

**Issue Detection Rules:**
1. Pod CrashLoopBackOff (High)
2. Pod OOMKilled (Critical)
3. Pod NotReady >5min (Medium)
4. HTTP Error Rate >5% (High)
5. P95 Latency >1s (Medium)
6. CPU Usage >80% (Medium)
7. Memory Usage >80% (Medium)

**Configuration:**
- Port: 8081
- Replicas: 2 (HA)
- LLM: OpenAI GPT-4 (temp: 0.3 for deterministic queries)
- Vector Store: Chroma (observability-memory collection)
- Namespace Filter: ALWAYS `nilabja-haldar-dev`

### 3. Pod Recovery Agent
**Purpose:** Monitor pod health, execute recovery actions with approval

**Capabilities:**
- Pod health monitoring (60s interval)
- Issue detection (6 pre-configured rules)
- Automated diagnostics (logs, metrics, events)
- Recovery actions (restart, scale up/down)
- Human-in-the-loop approval via Slack
- Confluence documentation

**Issue Detection Rules:**
1. CrashLoopBackOff (High)
2. OOMKilled (Critical)
3. ImagePullBackOff (High)
4. Pod NotReady >5min (Medium)
5. High Restart Count >5 (Medium)
6. Pod Pending >2min (Medium)

**Recovery Actions:**
- Pod restart (delete + recreate)
- Deployment scale up
- Deployment scale down
- **ALL require human approval (5-min timeout = DENY)**

**Configuration:**
- Port: 8082
- Replicas: 2 (HA)
- LLM: OpenAI GPT-4 (temp: 0.5)
- Vector Store: Chroma (pod-recovery-memory collection)
- Execution Mode: PLAN_ONLY (default)
- Approval Required: TRUE (always)

### 4. Backup/Restore Agent
**Purpose:** Manage backups via Velero/Argo, execute restores with approval

**Capabilities:**
- Scheduled backups (daily 2 AM, weekly Sunday 3 AM)
- On-demand backups
- Database backups via Argo Workflows
- Restore operations (namespace, PVC, database)
- Backup monitoring (failed, timeout, no recent backup)
- Human-in-the-loop approval for restores
- Confluence documentation

**Backup Operations:**
- On-demand backup (no approval required)
- Scheduled backup (no approval required)
- Database backup via Argo Workflow (no approval required)

**Restore Operations:**
- Namespace restore (approval required)
- PVC restore (approval required)
- Database restore (approval required)
- **ALL require human approval (5-min timeout = DENY)**

**Configuration:**
- Port: 8083
- Replicas: 2 (HA)
- LLM: OpenAI GPT-4 (temp: 0.5)
- Vector Store: Chroma (backup-restore-memory collection)
- S3 Bucket: observability-backups
- Retention: 30 days

## Human-in-the-Loop Approval Workflow

**CRITICAL SAFETY FEATURE:**

```
1. Agent detects issue requiring corrective action
2. Agent generates resolution plan
3. Agent sends Slack notification with:
   - Issue summary
   - Affected resources
   - Proposed resolution steps
   - Approve/Deny buttons
4. Human reviews and decides within 5 minutes
5. If APPROVED: Execute action → Monitor → Document in Confluence
6. If DENIED: Send manual steps to Slack
7. If TIMEOUT (5 min): Default to DENY (fail-safe)
```

**Approval Required For:**
- Pod restart/deletion
- Deployment scaling
- Namespace restore
- PVC restore
- Database restore

**No Approval Required For:**
- Metrics queries
- Log queries
- Dashboard creation
- Backups (non-destructive)
- Issue detection

## Namespace Enforcement

**CRITICAL:** ALL operations scoped to `nilabja-haldar-dev`

1. **Query Filters:** ALWAYS include `namespace="nilabja-haldar-dev"`
2. **RBAC:** Namespace-scoped Role (NOT ClusterRole)
3. **ServiceAccount:** Created in target namespace
4. **Resources:** All Kubernetes resources in target namespace

## Security Standards

### 1. Non-root User
- runAsUser: 1000
- runAsNonRoot: true

### 2. Read-only Filesystem
- readOnlyRootFilesystem: true
- Writable volumes: /tmp, /app/.cache (emptyDir)

### 3. Dropped Capabilities
- Drop ALL capabilities
- No privilege escalation

### 4. Namespace-scoped RBAC
- Role (not ClusterRole)
- Minimal permissions (get, list, watch)
- Write permissions only where needed (pod delete, deployment patch)

### 5. Secret Management
- LLM credentials in secrets
- Slack credentials in secrets
- Grafana API key in secrets
- Confluence credentials in secrets
- AWS credentials in secrets

## Observability Standards

### 1. Prometheus Metrics
All agents expose custom metrics:
- Request counters
- Duration histograms
- Issue detection counters
- Approval workflow counters
- Success rate gauges

### 2. ServiceMonitor
- 30-second scrape interval
- 10-second timeout
- Labeled for kube-prometheus

### 3. Health Checks
- Liveness probe: /health
- Readiness probe: /ready
- Proper timeouts and thresholds

### 4. Structured Logging
- JSON format
- LOG_LEVEL configurable
- Request tracking

## High Availability

### 1. Multiple Replicas
- Supervisor: 2 replicas
- Observability: 2 replicas
- Pod Recovery: 2 replicas
- Backup/Restore: 2 replicas

### 2. Pod Anti-Affinity
- Prefer different nodes
- Weight: 100

### 3. Resource Limits
- CPU: 100m-1000m
- Memory: 256Mi-1Gi

## Integration Points

### Supervisor ↔ Specialist Agents
- HTTP endpoints for synchronous calls
- WebSocket for real-time updates
- Shared vector store for context

### Observability Agent ↔ Data Sources
- Prometheus: http://prometheus.nilabja-haldar-dev.svc.cluster.local:9090
- Thanos: http://thanos-query.nilabja-haldar-dev.svc.cluster.local:9090
- Loki: http://loki.nilabja-haldar-dev.svc.cluster.local:3100
- Grafana: http://grafana.nilabja-haldar-dev.svc.cluster.local:3000
- Alertmanager: http://alertmanager.nilabja-haldar-dev.svc.cluster.local:9093

### Pod Recovery Agent ↔ Kubernetes
- In-cluster Kubernetes API
- Namespace: nilabja-haldar-dev
- ServiceAccount with minimal RBAC

### Backup/Restore Agent ↔ Velero/Argo
- Velero namespace: velero
- Argo namespace: argo
- S3 bucket: observability-backups

### All Agents ↔ Slack
- Webhook URL for notifications
- Bot token for interactive messages
- Channel: #observability-alerts, #pod-recovery-alerts, #backup-restore-alerts

### All Agents ↔ Confluence
- REST API with username/token auth
- Space: OBSERVABILITY
- Auto-create incident pages

## Environment Variables Required

### Common (All Agents)
- OPENAI_API_KEY or GROQ_API_KEY (from llm-credentials secret)
- CHROMA_HOST, CHROMA_PORT
- SLACK_WEBHOOK_URL, SLACK_BOT_TOKEN (from slack-credentials secret)
- CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN (from confluence-credentials secret)

### Observability Agent
- PROMETHEUS_URL, THANOS_URL, LOKI_URL, GRAFANA_URL, ALERTMANAGER_URL
- GRAFANA_API_KEY (from grafana-credentials secret)

### Backup/Restore Agent
- AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY (from aws-credentials secret)
- S3_BUCKET, S3_REGION, S3_PREFIX

## Next Steps

### Phase 4: Agent Source Code (~30 files)
Now that Helm charts are complete, implement the actual agent code:

1. **Common Infrastructure:**
   - LLM client (OpenAI/Groq)
   - Vector store client (Chroma)
   - Tool registry
   - Approval workflow implementation
   - Namespace guard

2. **Supervisor Agent:**
   - Intent classification
   - Query routing
   - WebSocket handler
   - Agent coordination

3. **Observability Agent:**
   - PromQL/LogQL generation
   - Dashboard creation
   - Issue detection
   - Slack notifications

4. **Pod Recovery Agent:**
   - Pod health monitoring
   - Diagnostics (logs, metrics, events)
   - Recovery actions
   - Approval workflow

5. **Backup/Restore Agent:**
   - Velero integration
   - Argo Workflows integration
   - Backup monitoring
   - Restore operations

---

**Status:** Phase 3 Complete ✅  
**Next:** Phase 4 (Agent Source Code) - Implement actual agent logic