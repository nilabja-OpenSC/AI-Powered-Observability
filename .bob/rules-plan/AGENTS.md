# Plan Mode Rules - AI-Powered Observability Platform

This file contains planning and architecture-specific rules for AI assistants working in Plan mode.

## Project Overview
- **Language**: Python 3.11+
- **Framework**: FastAPI (Backend), Next.js (Frontend)
- **Deployment**: Helm charts on OpenShift ROSA
- **Namespace**: `nilabja-haldar-dev` (ALL operations scoped here)
- **Architecture**: Microservices with AI agents for observability automation

## Hidden Architectural Constraints

### Namespace Isolation
- **CRITICAL**: All resources MUST be deployed in `nilabja-haldar-dev` namespace
- NO cluster-wide RBAC, SCC, or operators allowed
- Use namespace-scoped ServiceAccounts with minimal Role permissions
- This constraint affects: deployment strategy, RBAC design, monitoring scope

### Human-in-the-Loop Requirement
- **CRITICAL**: All corrective actions require human approval via Slack
- Default mode is PLAN_ONLY (no mutations without explicit approval)
- Timeout (5 minutes) defaults to DENY (fail-safe)
- This affects: agent workflow design, error handling, state management

### Communication Channel Separation
- **Slack**: Issue notifications, approvals, incident updates (mutation workflows)
- **Chat UI**: Observability queries ONLY (Prometheus, Grafana, Loki - read-only)
- **Confluence**: Incident documentation and postmortems (audit trail)
- This separation is MANDATORY and affects UI/UX design

### Storage Constraints
- PostgreSQL: Single instance with PVC (10GB, EFS CSI, RWO)
- Chroma Vector Store: PVC (5GB, EFS CSI, RWO)
- Thanos/Velero: Object Store (EFS CSI)
- No distributed databases or multi-node stateful sets

## Non-Standard Patterns

### Agent Orchestration Pattern
```
Supervisor Agent (Router)
    ↓
    ├─→ Observability Agent (Metrics, Logs, Dashboards)
    ├─→ Pod Recovery Agent (Kubernetes operations)
    └─→ Backup/Restore Agent (Velero operations)

Each specialist agent:
1. Receives task from supervisor
2. Analyzes issue/request
3. Generates resolution plan
4. Sends Slack notification with approve/deny buttons
5. Waits for human decision (5 min timeout)
6. Executes (if approved) or sends manual steps (if denied)
7. Reports results to Slack and Confluence
```

### Approval Workflow State Machine
```
DETECTED → NOTIFIED → WAITING → [APPROVED/DENIED] → [EXECUTING/MANUAL] → [RESOLVED/PENDING] → DOCUMENTED
```

### Query Routing Pattern
- **Recent data (< 6 hours)**: Prometheus (high resolution)
- **Historical data (> 6 hours)**: Thanos (long-term storage)
- **Logs**: Loki (label-based queries)
- **Dashboards**: Grafana (unified visualization)

### Dual Tech Stack Support
- **Primary**: OpenAI + LangChain + Chroma
- **Alternative**: IBM watsonx.ai + watsonx Orchestrate + watsonx.data
- Architecture must support both with minimal code changes

## Critical Design Decisions

### Why Slack for Approvals (Not Chat UI)
- **Rationale**: Slack provides:
  - Interactive buttons (Block Kit)
  - Persistent notification history
  - Mobile accessibility for on-call engineers
  - Integration with existing incident management workflows
- **Trade-off**: Requires Slack workspace setup and webhook configuration
- **Alternative considered**: In-app approval UI (rejected due to lack of mobile support)

### Why Namespace-Scoped (Not Cluster-Wide)
- **Rationale**: 
  - Demo/hackathon constraint (no cluster admin access)
  - Security best practice (principle of least privilege)
  - Easier to clean up and redeploy
- **Trade-off**: Cannot monitor cluster-level resources (nodes, namespaces)
- **Mitigation**: Focus on application-level observability

### Why Human-in-the-Loop (Not Fully Autonomous)
- **Rationale**:
  - Safety: Prevent accidental damage from AI mistakes
  - Compliance: Audit trail for all corrective actions
  - Trust: Build confidence in AI recommendations
- **Trade-off**: Slower incident response (5 min approval wait)
- **Mitigation**: Timeout defaults to DENY (fail-safe)

### Why Separate Chat UI and Slack
- **Rationale**:
  - Chat UI: Interactive exploration (developers, SREs)
  - Slack: Operational alerts (on-call, incident response)
  - Different user contexts and expectations
- **Trade-off**: Two interfaces to maintain
- **Mitigation**: Shared backend agent logic

## Component Interactions

### Agent → Observability Stack
```
Agent → Prometheus/Thanos (PromQL queries)
      → Loki (LogQL queries)
      → Grafana API (dashboard creation)
      → Alertmanager (alert routing)
```

### Agent → Kubernetes
```
Agent → oc/kubectl (via subprocess or Python client)
      → Namespace-scoped operations only
      → ServiceAccount with minimal RBAC
```

### Agent → External Services
```
Agent → Slack (webhooks + interactive messages)
      → Confluence (REST API for documentation)
      → Velero (backup/restore operations)
```

### Hidden Dependencies
- **Slack interactive messages**: Require public endpoint for callbacks (ngrok for dev, OpenShift Route for prod)
- **Chroma vector store**: Must be initialized before agents start
- **LLM API keys**: Must be configured in environment variables before deployment

## Performance & Scalability Considerations

### Agent Scalability
- **Current**: 1 replica per agent (stateful with vector store)
- **Bottleneck**: Vector store is single-node (RWO PVC)
- **Future**: Consider distributed vector store (Milvus, Weaviate) for multi-replica agents

### Prometheus/Thanos Query Performance
- **Optimization**: Route queries based on time range
- **Bottleneck**: Large time ranges can timeout
- **Mitigation**: Implement query result caching, limit time range in UI

### Slack Rate Limits
- **Constraint**: Slack API has rate limits (1 message/second per channel)
- **Mitigation**: Queue notifications, batch updates, use threads for related messages

### Approval Timeout Impact
- **Issue**: 5-minute timeout can delay incident response
- **Mitigation**: 
  - Send notifications to multiple channels (primary + backup)
  - Implement escalation (page on-call if no response)
  - Allow pre-approved actions for known safe operations

## Testing & Deployment Architecture

### Testing Strategy
```
Unit Tests:
- Agent tool functions (mocked external APIs)
- PromQL/LogQL generation
- Approval workflow state machine

Integration Tests:
- Agent → Prometheus/Loki (real queries)
- Agent → Slack (test webhooks)
- Agent → Kubernetes (test namespace)

E2E Tests:
- Full workflow: detect → notify → approve → execute → document
- Timeout scenarios
- Denial scenarios
```

### Deployment Order
```
1. Observability Stack (Prometheus, Loki, Grafana, Alertmanager)
   ↓
2. E-commerce App (generates signals)
   ↓
3. AI Agents (consume signals, take actions)
```

### Rollback Strategy
- **Helm rollback**: Revert to previous chart version
- **Agent failures**: Agents fail gracefully, send Slack alerts
- **Database migrations**: Use Alembic with down migrations
- **PVC data**: Daily Velero backups for recovery

## Backwards Compatibility Requirements

### API Versioning
- FastAPI endpoints: `/api/v1/...`
- Grafana dashboard JSON: Version field for compatibility
- Prometheus metrics: Follow naming conventions (no breaking changes)

### Agent Memory Migration
- Chroma vector store: Backup before schema changes
- LangChain agent state: Serialize/deserialize with version tags

### Helm Chart Upgrades
- Use `helm upgrade --install` for idempotent deployments
- ConfigMaps/Secrets: Immutable, create new versions
- PVCs: Retain policy to prevent data loss

## Architecture Evolution Path

### Phase 1 (Current): Manual Approval
- All corrective actions require human approval
- Focus on building trust and collecting data

### Phase 2 (Future): Conditional Autonomy
- Pre-approved actions for known safe operations (e.g., restart pod with < 5 restarts)
- Approval required only for high-risk operations

### Phase 3 (Future): Full Autonomy with Guardrails
- AI decides when to request approval based on confidence score
- Automatic rollback if action fails
- Continuous learning from approval/denial patterns

## Key Architectural Principles

1. **Safety First**: Default to DENY, require explicit approval
2. **Namespace Isolation**: All operations scoped to single namespace
3. **Separation of Concerns**: Chat UI (queries) vs Slack (approvals)
4. **Fail-Safe Design**: Timeouts default to DENY, agent failures don't crash system
5. **Audit Trail**: All actions logged to Confluence
6. **Modular Architecture**: Independent Helm charts per layer
7. **Dual Tech Stack**: Support both OpenAI and IBM watsonx.ai

---

**Note**: Only include information discovered by reading actual code and architecture. Standard Python architectural patterns should NOT be documented here.