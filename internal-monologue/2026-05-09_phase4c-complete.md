# Phase 4C Complete: Observability Agent Source Code

**Date:** 2026-05-09
**Status:** ✅ Complete (5/5 files)

## Summary

Successfully created the Observability Agent source code. This agent handles all observability queries including metrics (Prometheus), logs (Loki), and dashboard creation (Grafana).

## Files Created (5 total)

1. `src/agents/observability/main.py` - FastAPI server (port 8081)
2. `src/agents/observability/query_generator.py` - PromQL/LogQL generation from natural language
3. `src/agents/observability/issue_detector.py` - Automated issue detection from metrics/logs
4. `src/agents/observability/notification_handler.py` - Slack notifications for issues
5. `src/agents/observability/dashboard_generator.py` - Grafana dashboard creation

## Architecture

### Observability Agent Flow
```
User Query → Query Generator → PromQL/LogQL → Prometheus/Loki → Response
                                                      ↓
                                              Issue Detector
                                                      ↓
                                           Notification Handler → Slack
```

### Endpoints (Port 8081)
- `POST /query` - Process observability queries (metrics/logs)
- `POST /detect-issues` - Detect issues from metrics/logs
- `POST /create-dashboard` - Create Grafana dashboard
- `GET /health` - Health check endpoint

## Key Features

### 1. Query Generator (`query_generator.py`)
- **Natural language to PromQL/LogQL** conversion
- **Few-shot prompting** with 5 example queries
- **Automatic namespace filtering** (nilabja-haldar-dev)
- **Time range parsing** (5m, 1h, 24h, etc.)
- **Response formatting** - Converts data to natural language

**Example Queries:**
```
"Show me CPU usage for backend pods"
→ rate(container_cpu_usage_seconds_total{namespace="nilabja-haldar-dev",pod=~"backend-.*"}[5m])

"Show error logs from backend"
→ {namespace="nilabja-haldar-dev",app="backend"} |= "error" or "ERROR"
```

### 2. Issue Detector (`issue_detector.py`)
- **5 detection queries:**
  - High CPU usage (>80%)
  - High memory usage (>90%)
  - Pod crashes (>5 restarts)
  - High error rate (>10%)
  - Slow response times (p95 >1s)
- **Log analysis** for error patterns
- **LLM-generated resolution steps**
- **Severity filtering** (low, medium, high, critical)

**Detection Queries:**
```promql
# High CPU
rate(container_cpu_usage_seconds_total{namespace="nilabja-haldar-dev"}[5m]) > 0.8

# High Memory
container_memory_usage_bytes{namespace="nilabja-haldar-dev"} / 
container_spec_memory_limit_bytes{namespace="nilabja-haldar-dev"} > 0.9

# Pod Crashes
kube_pod_container_status_restarts_total{namespace="nilabja-haldar-dev"} > 5
```

### 3. Notification Handler (`notification_handler.py`)
- **Issue notifications** with severity emoji
- **Resolution notifications** for fixed issues
- **Batch notifications** for multiple issues
- **Severity grouping** (critical, high, medium, low)
- **Resource deduplication**

**Notification Format:**
```
🚨 Issue Detected: High CPU Usage
Severity: HIGH
Affected Resources:
• pod/backend-abc123
• container/backend

Resolution Steps:
1. Check for resource-intensive operations
2. Review recent deployments
3. Scale deployment if needed
```

### 4. Dashboard Generator (`dashboard_generator.py`)
- **LLM-based panel generation** from descriptions
- **Grafana API integration** for dashboard creation
- **Default panels** (CPU, memory, HTTP requests)
- **Auto-layout** with grid positioning
- **Namespace tagging** for organization

**Generated Dashboard Structure:**
```json
{
  "title": "Backend Service Dashboard",
  "panels": [
    {"title": "CPU Usage", "type": "graph", "query": "..."},
    {"title": "Memory Usage", "type": "graph", "query": "..."},
    {"title": "HTTP Request Rate", "type": "graph", "query": "..."}
  ]
}
```

### 5. FastAPI Server (`main.py`)
- **3 main endpoints** for queries, issue detection, dashboard creation
- **Tool integration** (Prometheus, Loki, Slack)
- **Vector store** for query memory
- **Error handling** with detailed logging
- **CORS middleware** for frontend integration

## Query Examples

### Metrics Queries
```
"Show CPU usage for backend pods" → Prometheus query
"What's the memory usage of frontend?" → Prometheus query
"Show HTTP request rate" → Prometheus query
```

### Log Queries
```
"Show error logs from backend" → Loki query
"Get logs from frontend in last hour" → Loki query
"Find exception logs" → Loki query
```

### Dashboard Requests
```
"Create a dashboard for backend service"
"Build a dashboard showing HTTP latency"
"Generate a dashboard for pod health"
```

## Issue Detection

### Automated Detection
- Runs every 5 minutes (configurable)
- Checks 5 predefined issue types
- Analyzes logs for error patterns
- Generates resolution steps using LLM

### Issue Object Structure
```python
{
    "id": "high_cpu-backend-abc-1234567890",
    "type": "high_cpu",
    "severity": "high",
    "summary": "High CPU usage detected",
    "affected_resources": ["pod/backend-abc", "container/backend"],
    "details": {
        "pod": "backend-abc",
        "container": "backend",
        "value": "0.85",
        "time_range": "5m"
    },
    "resolution_steps": [
        "Check for resource-intensive operations",
        "Review recent deployments",
        "Scale deployment if needed"
    ],
    "timestamp": "2026-05-09T06:00:00Z"
}
```

## Notification Patterns

### Single Issue Notification
```
🚨 Issue Detected: High CPU Usage
Severity: HIGH
Affected Resources: pod/backend-abc
Details: CPU usage at 85%
```

### Batch Notification
```
Multiple Issues Detected
🚨 2 critical issue(s)
🔴 3 high severity issue(s)
⚠️ 1 medium severity issue(s)
Total: 6 issues
```

### Resolution Notification
```
✅ Success: Issue Resolved
Summary: CPU usage returned to normal
Details: Scaled deployment from 2 to 4 replicas
```

## Configuration

### Environment Variables
```bash
# Prometheus/Thanos
PROMETHEUS_URL=http://prometheus:9090
THANOS_QUERY_URL=http://thanos-query:9090

# Loki
LOKI_URL=http://loki:3100

# Grafana
GRAFANA_URL=http://grafana:3000
GRAFANA_API_KEY=glsa_...

# Slack
SLACK_BOT_TOKEN=xoxb-...
SLACK_CHANNEL=#observability-alerts

# LLM (from common)
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...

# Server
PORT=8081
```

## Integration Points

### With Supervisor Agent
- Receives queries routed from Supervisor (port 8080)
- Returns formatted responses with data

### With Prometheus/Loki
- Executes PromQL/LogQL queries
- Auto-routes based on time range (<6h = Prometheus, >6h = Thanos)

### With Slack
- Sends issue notifications
- Sends resolution updates
- Batch notifications for multiple issues

### With Grafana
- Creates dashboards via API
- Generates panels with PromQL queries
- Tags dashboards with namespace

## Error Handling

### Query Generation Errors
- Falls back to default query: `up{namespace="nilabja-haldar-dev"}`
- Logs error for debugging
- Returns user-friendly message

### Issue Detection Errors
- Continues with other detection queries
- Logs individual query failures
- Returns partial results

### Notification Errors
- Logs error but doesn't block processing
- Allows graceful degradation

## Next Steps

**Phase 4D: Pod Recovery Agent Source Code (4 files)**
1. `src/agents/pod-recovery/main.py` - FastAPI server
2. `src/agents/pod-recovery/health_monitor.py` - Pod health monitoring
3. `src/agents/pod-recovery/diagnostics.py` - Pod diagnostics
4. `src/agents/pod-recovery/recovery_actions.py` - Recovery actions (restart, scale, etc.)

## Progress Update

**Overall Progress:** 79/~165 files (48%)
- Phase 1: Platform & Observability Stack (30 files) ✅
- Phase 2: E-commerce Application Helm Charts (6 files) ✅
- Phase 3: AI Agent Helm Charts (32 files) ✅
- Phase 4A: Common Agent Infrastructure (12 files) ✅
- Phase 4B: Supervisor Agent (3 files) ✅
- Phase 4C: Observability Agent (5 files) ✅ **COMPLETE**
- Phase 4D: Pod Recovery Agent (4 files) - Next
- Phase 4E: Backup/Restore Agent (4 files) - Pending
- Phase 5: E-commerce Source Code (~50 files) - Pending
- Phase 6: Documentation & Configuration (~10 files) - Pending

## Technical Highlights

### Pattern: Few-Shot Query Generation
```python
examples = [
    {"query": "Show CPU usage", "promql": "rate(...)"},
    # ... more examples
]
# LLM learns from examples to generate new queries
```

### Pattern: Automated Issue Detection
```python
detection_queries = {
    "high_cpu": {"query": "...", "severity": "high"},
    "high_memory": {"query": "...", "severity": "high"},
    # ... more checks
}
# Run all checks, generate resolution steps
```

### Pattern: LLM-Generated Resolution Steps
```python
prompt = f"Issue: {issue_type}\nGenerate resolution steps..."
steps = llm.generate(prompt)
# Provides actionable steps for each issue
```

---

**Made with Bob** 🤖