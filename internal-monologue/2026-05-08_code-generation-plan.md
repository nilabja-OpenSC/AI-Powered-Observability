# Code Generation Plan - AI-Powered Observability Platform

**Date:** 2026-05-08  
**Task:** Generate complete codebase following specification order

## Implementation Order (from Generic-schema.md)

1. ✅ Generic-schema (guidelines understood)
2. ✅ tech-stack (architecture defined)
3. ⏳ Platform-Observability-Tools-Creation-Agent-prompt (CURRENT)
4. ⏳ ecommerce-demo-app-prompt
5. ⏳ Backup-Restore-Agent-prompt
6. ⏳ Pod-Recovery-Agent-promot
7. ⏳ Observability-Agent-prompt
8. ⏳ Supervisor-Agent

## Phase 1: Platform & Observability Stack (CURRENT)

### Components to Generate:
1. **Prometheus** (namespace-scoped)
   - ServiceMonitors/PodMonitors
   - Metrics scraping configuration
   - Thanos sidecar integration

2. **Grafana**
   - Dashboard provisioning
   - Data source configuration (Prometheus, Loki)
   - No cluster-wide plugins

3. **Thanos**
   - Query layer
   - Sidecar for Prometheus
   - Object store configuration (EFS)

4. **Loki**
   - Log aggregation
   - Label-based queries
   - Retention policies

5. **Promtail**
   - DaemonSet for log collection
   - Pod log scraping

6. **Alertmanager**
   - Alert routing
   - Slack webhook integration
   - Severity levels

7. **PostgreSQL**
   - PVC-backed storage (10GB, EFS CSI)
   - Service + Secret
   - Backup integration

8. **Velero**
   - Namespace-scoped backup/restore
   - PVC snapshots
   - Daily schedule

9. **Argo Workflows**
   - Database backup workflows
   - Database restore workflows
   - Agent integration

### Helm Chart Structure:
```
charts/
├── observability-stack/
│   ├── prometheus/
│   ├── grafana/
│   ├── thanos/
│   ├── loki/
│   ├── promtail/
│   └── alertmanager/
├── data-layer/
│   └── postgresql/
├── backup-restore/
│   ├── velero/
│   └── argo-workflows/
├── ecommerce-app/
│   ├── frontend/
│   ├── backend/
│   └── chat-ui/
└── ai-agents/
    ├── supervisor/
    ├── observability-agent/
    ├── pod-recovery-agent/
    └── backup-restore-agent/
```

## Phase 2: E-commerce Demo Application

### Components:
1. **Frontend (Next.js)**
   - Product search/add pages
   - Cart management
   - Checkout simulation
   - User management
   - Tailwind CSS styling

2. **Backend (FastAPI)**
   - CRUD APIs (products, users, carts)
   - Swagger/OpenAPI docs
   - Structured logging
   - Prometheus metrics endpoint
   - Chaos injection toggles

3. **Chat UI (Next.js)**
   - WebSocket/HTTP connection to agents
   - Natural language query interface
   - Response display

4. **Database Schema**
   - users, products, carts, cart_items tables
   - Sample seed data (10 users, 1 admin, 100 products)

## Phase 3: AI Agents

### Components:
1. **Supervisor Agent**
   - Intent classification
   - Agent routing
   - LangChain orchestration

2. **Observability Agent**
   - PromQL/LogQL generation
   - Dashboard creation
   - Issue detection
   - Slack notifications with approval workflow

3. **Pod Recovery Agent**
   - Pod diagnostics
   - Remediation actions
   - Helm value recommendations

4. **Backup/Restore Agent**
   - Velero operations
   - Backup health checks
   - Restore workflows

### Shared Agent Infrastructure:
- Chroma vector store (PVC-backed, 5GB)
- OpenAI LLM client
- LangChain tools and chains
- Slack integration (Block Kit)
- Confluence integration

## Technical Constraints

### Namespace Isolation:
- ALL resources in `nilabja-haldar-dev`
- NO cluster-wide RBAC/SCC
- Namespace-scoped ServiceAccounts

### Storage:
- PostgreSQL: 10GB PVC (EFS CSI, RWO)
- Chroma: 5GB PVC (EFS CSI, RWO)
- Thanos/Velero: EFS object store

### Execution Safety:
- Default: PLAN_ONLY mode
- Mutations require: EXECUTE: true
- Corrective actions require: HUMAN_APPROVAL via Slack
- Timeout (5 min) = DENY

### Communication Channels:
- **Slack**: Issue notifications, approvals, incident updates
- **Chat UI**: Observability queries ONLY (no mutations)
- **Confluence**: Incident documentation

## Environment Variables (Placeholders):

```bash
# LLM Configuration
OPENAI_API_KEY=<placeholder>
OPENAI_API_BASE=https://api.groq.com/openai/v1

# Slack Integration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
SLACK_BOT_TOKEN=<placeholder>
SLACK_SIGNING_SECRET=<placeholder>

# Confluence Integration
CONFLUENCE_API_URL=https://example.com/confluence/api/content
CONFLUENCE_API_TOKEN=<placeholder>

# Database
POSTGRES_PASSWORD=<placeholder>
POSTGRES_USER=postgres
POSTGRES_DB=ecommerce

# Container Registry
CONTAINER_REGISTRY=icr.io/nilabja-reg
```

## Implementation Strategy

### Step 1: Create Folder Structure
- Generate complete directory tree
- Create placeholder files

### Step 2: Implement Platform/Observability
- Helm charts for each component
- ConfigMaps, Secrets, Services
- PVCs and StatefulSets
- ServiceMonitors and PrometheusRules

### Step 3: Implement E-commerce App
- Backend FastAPI application
- Frontend Next.js application
- Chat UI Next.js application
- Database migrations and seed data

### Step 4: Implement AI Agents
- Shared agent infrastructure
- Individual agent implementations
- Tool definitions and chains
- Slack/Confluence integrations

### Step 5: Integration Testing
- End-to-end workflow tests
- Approval workflow tests
- Namespace isolation tests

## Success Criteria

- ✅ All components deployable via Helm
- ✅ Namespace-scoped (no cluster-wide resources)
- ✅ Human-in-the-loop approval workflow functional
- ✅ Chat UI separated from Slack notifications
- ✅ Observability signals (metrics, logs, traces) generated
- ✅ Backup/restore workflows operational
- ✅ Agent routing and execution working

## Next Steps

1. Create complete folder structure
2. Generate Helm charts for observability stack
3. Implement PostgreSQL with PVC
4. Implement Prometheus + Thanos
5. Implement Loki + Promtail
6. Implement Grafana with dashboards
7. Implement Alertmanager + Slack
8. Implement Velero + Argo Workflows
9. Generate e-commerce application code
10. Generate AI agent code
11. Create deployment documentation

---

**Status:** Ready to begin code generation
**Current Phase:** Platform & Observability Stack
**Next Action:** Create folder structure