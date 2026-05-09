# Basic Rules for AI-Powered Observability Platform

## Documentation Standards

Always include concise docstrings for every public function (Python docstrings, not JSDoc).

Be very concise in your wording.

Write a summary of every interaction into the folder `internal-monologue/`.
Name the file starting with a timestamp, followed by a concise description of the interaction.
Example: 2026-01-15_update-readme.md

## Project-Specific Rules

### Namespace Constraint
- ALL code MUST operate within namespace: `nilabja-haldar-dev`
- NO cluster-wide RBAC or SCC changes allowed
- Use namespace-scoped ServiceAccounts with minimal Role permissions

### Execution Safety
- Default mode: PLAN_ONLY (no mutations without approval)
- Corrective actions require HUMAN_APPROVAL via Slack
- Timeout (5 min) defaults to DENY (fail-safe)
- All actions must be auditable and reversible

### Communication Channels
- **Slack**: Issue notifications, approvals, incident updates
- **Chat UI**: Observability queries ONLY (Prometheus, Grafana, Loki)
- **Confluence**: Incident documentation and postmortems

### Tech Stack Preferences
- **Primary**: OpenAI + LangChain + Chroma
- **Alternative**: IBM watsonx.ai + watsonx Orchestrate + watsonx.data
- **Backend**: FastAPI (Python)
- **Frontend**: Next.js (React)
- **Database**: PostgreSQL with PVC (EFS CSI, 10GB)

### Observability Standards
- Always include: time range, namespace filter, workload labels in queries
- Use Thanos for long-range queries, Prometheus for recent data
- Dashboard panels must include Golden Signals (latency, traffic, errors, saturation)
- Label all dashboards/panels with namespace and app context

### Slack Notification Format
- Use Slack Block Kit for rich formatting
- Include interactive buttons for approve/deny workflows
- Provide issue summary, affected resources, resolution steps
- Send different responses based on approval/denial

### File Organization
- Helm charts in separate directories per layer
- Specs in `.bob/specs/`
- Architecture docs in `docs/`
- Internal monologue in `internal-monologue/`