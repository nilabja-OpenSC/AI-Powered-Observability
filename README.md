# AI-Powered Observability Platform

An intelligent observability platform for Kubernetes/OpenShift that combines traditional monitoring tools (Prometheus, Grafana, Loki) with AI agents for automated issue detection, diagnostics, and recovery.

## 🎯 Overview

This platform provides:
- **Automated Observability**: AI agents that understand natural language queries about metrics, logs, and system health
- **Intelligent Diagnostics**: Automated root cause analysis using LLM-powered diagnostics
- **Human-in-the-Loop Recovery**: Automated recovery actions with Slack-based approval workflows
- **Backup/Restore Automation**: Velero and Argo Workflows integration for data protection
- **Demo E-commerce Application**: Sample application to demonstrate observability capabilities

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interfaces                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Chat UI    │  │   Grafana    │  │    Slack     │          │
│  │  (Port 5173) │  │  (Port 3000) │  │ Notifications│          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                         AI Agent Layer                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Supervisor Agent (Port 8080)                 │   │
│  │         Intent Classification & Query Routing             │   │
│  └────┬──────────────┬──────────────┬──────────────┬────────┘   │
│       │              │              │              │            │
│  ┌────▼────┐   ┌────▼────┐   ┌────▼────┐   ┌────▼────┐       │
│  │Observ.  │   │Pod      │   │Backup/  │   │Common   │       │
│  │Agent    │   │Recovery │   │Restore  │   │Infra    │       │
│  │(8081)   │   │(8082)   │   │(8083)   │   │         │       │
│  └────┬────┘   └────┬────┘   └────┬────┘   └─────────┘       │
└───────┼─────────────┼─────────────┼──────────────────────────┘
        │             │             │
        ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Observability Stack                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │Prometheus│  │  Loki    │  │ Thanos   │  │Alertmgr  │       │
│  │  (9090)  │  │  (3100)  │  │  (9090)  │  │  (9093)  │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
        │             │             │
        ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Application Layer                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Backend  │  │ Frontend │  │ Chat UI  │  │PostgreSQL│       │
│  │  (8000)  │  │  (3000)  │  │  (5173)  │  │  (5432)  │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- OpenShift ROSA cluster or Kubernetes 1.28+
- Helm 3.12+
- kubectl configured
- Namespace: `nilabja-haldar-dev`

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd AI-Powered-Observability
```

2. **Install Observability Stack**
```bash
# Prometheus
helm install prometheus ./charts/observability-stack/prometheus -n nilabja-haldar-dev

# Grafana
helm install grafana ./charts/observability-stack/grafana -n nilabja-haldar-dev

# Loki
helm install loki ./charts/observability-stack/loki -n nilabja-haldar-dev

# Promtail
helm install promtail ./charts/observability-stack/promtail -n nilabja-haldar-dev

# Thanos (optional, for long-term storage)
helm install thanos ./charts/observability-stack/thanos -n nilabja-haldar-dev

# Alertmanager
helm install alertmanager ./charts/observability-stack/alertmanager -n nilabja-haldar-dev
```

3. **Install Data Layer**
```bash
# PostgreSQL
helm install postgresql ./charts/data-layer/postgresql -n nilabja-haldar-dev
```

4. **Install AI Agents**
```bash
# Supervisor Agent
helm install supervisor-agent ./charts/ai-agents/supervisor-agent -n nilabja-haldar-dev

# Observability Agent
helm install observability-agent ./charts/ai-agents/observability-agent -n nilabja-haldar-dev

# Pod Recovery Agent
helm install pod-recovery-agent ./charts/ai-agents/pod-recovery-agent -n nilabja-haldar-dev

# Backup/Restore Agent
helm install backup-restore-agent ./charts/ai-agents/backup-restore-agent -n nilabja-haldar-dev
```

5. **Install E-commerce Application**
```bash
# Backend
helm install backend ./charts/ecommerce-app/backend -n nilabja-haldar-dev

# Frontend
helm install frontend ./charts/ecommerce-app/frontend -n nilabja-haldar-dev

# Chat UI
helm install chat-ui ./charts/ecommerce-app/chat-ui -n nilabja-haldar-dev
```

6. **Install Backup/Restore Tools (Optional)**
```bash
# Velero
helm install velero ./charts/backup-restore/velero -n nilabja-haldar-dev

# Argo Workflows
helm install argo-workflows ./charts/backup-restore/argo-workflows -n nilabja-haldar-dev
```

### Configuration

Create a `values-override.yaml` file with your configuration:

```yaml
# LLM Configuration
llm:
  provider: openai  # or groq
  apiKey: "your-api-key"

# Slack Configuration
slack:
  botToken: "xoxb-your-bot-token"
  channel: "#observability-alerts"

# Confluence Configuration (optional)
confluence:
  url: "https://your-company.atlassian.net"
  username: "user@company.com"
  apiToken: "your-api-token"
  space: "OBSERVABILITY"
```

Apply configuration:
```bash
helm upgrade supervisor-agent ./charts/ai-agents/supervisor-agent \
  -n nilabja-haldar-dev \
  -f values-override.yaml
```

## 📊 Features

### 1. Natural Language Queries

Ask questions in plain English:
- "Show me CPU usage for backend pods"
- "What are the error logs from the last hour?"
- "Why is the backend pod crashing?"
- "Create a backup of the database"

### 2. Automated Issue Detection

The Observability Agent continuously monitors:
- High CPU/memory usage (>80%/90%)
- Pod crashes (>5 restarts)
- High error rates (>10%)
- Slow response times (p95 >1s)
- Error log patterns

### 3. Intelligent Diagnostics

The Pod Recovery Agent provides:
- Root cause analysis using LLM
- Log analysis for error patterns
- Resource usage diagnostics
- Automated recommendations

### 4. Human-in-the-Loop Recovery

All corrective actions require approval:
- Slack notification with Approve/Deny buttons
- 5-minute timeout (defaults to DENY)
- Manual steps provided on denial
- Confluence documentation on approval

### 5. Automated Backups

The Backup/Restore Agent provides:
- Scheduled backups (every 24 hours)
- On-demand backups via API
- Velero integration
- Argo Workflows for automation
- 30-day retention policy

## 🔧 AI Agents

### Supervisor Agent (Port 8080)

**Purpose:** Routes user queries to appropriate specialist agents

**Endpoints:**
- `POST /query` - Process user query
- `WebSocket /ws` - Real-time query processing
- `GET /health` - Health check

**Example:**
```bash
curl -X POST http://supervisor-agent:8080/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show CPU usage for backend pods"}'
```

### Observability Agent (Port 8081)

**Purpose:** Handles metrics, logs, and dashboard queries

**Endpoints:**
- `POST /query` - Process observability query
- `POST /detect-issues` - Detect issues from metrics/logs
- `POST /create-dashboard` - Create Grafana dashboard
- `GET /health` - Health check

**Example:**
```bash
curl -X POST http://observability-agent:8081/detect-issues \
  -H "Content-Type: application/json" \
  -d '{"time_range": "5m", "severity_threshold": "medium"}'
```

### Pod Recovery Agent (Port 8082)

**Purpose:** Handles pod diagnostics and recovery

**Endpoints:**
- `POST /query` - Process pod recovery query
- `POST /diagnose` - Diagnose pod issues
- `POST /recover` - Execute recovery action (requires approval)
- `GET /health` - Health check

**Example:**
```bash
curl -X POST http://pod-recovery-agent:8082/diagnose \
  -H "Content-Type: application/json" \
  -d '{"pod_name": "backend-abc123", "namespace": "nilabja-haldar-dev"}'
```

### Backup/Restore Agent (Port 8083)

**Purpose:** Handles backup and restore operations

**Endpoints:**
- `POST /backup` - Create backup (requires approval)
- `POST /restore` - Restore from backup (requires approval)
- `GET /backups` - List available backups
- `GET /health` - Health check

**Example:**
```bash
curl -X POST http://backup-restore-agent:8083/backup \
  -H "Content-Type: application/json" \
  -d '{"name": "backup-20260509", "namespace": "nilabja-haldar-dev", "execute": true}'
```

## 📈 Monitoring

### Prometheus Metrics

All components expose Prometheus metrics at `/metrics`:

**Backend Metrics:**
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request duration
- `orders_total` - Total orders created
- `products_total` - Total products

**Agent Metrics:**
- `agent_queries_total` - Total queries processed
- `agent_query_duration_seconds` - Query processing time
- `agent_errors_total` - Total errors

### Grafana Dashboards

Access Grafana at `http://grafana:3000` (default credentials: admin/admin)

**Pre-configured Dashboards:**
- Kubernetes Cluster Overview
- Application Performance
- AI Agent Performance
- Database Performance

### Loki Logs

Query logs using LogQL:
```logql
{namespace="nilabja-haldar-dev",app="backend"} |= "error"
```

## 🔐 Security

### Namespace Isolation

All operations are scoped to `nilabja-haldar-dev`:
- Kubernetes RBAC with namespace-scoped roles
- PromQL/LogQL queries include namespace filter
- No cluster-wide permissions

### Human-in-the-Loop

All corrective actions require approval:
- Slack approval with 5-minute timeout
- Timeout defaults to DENY (fail-safe)
- Manual steps provided on denial

### Secrets Management

Sensitive data stored in Kubernetes Secrets:
- LLM API keys
- Slack bot tokens
- Confluence credentials
- Database passwords

## 🧪 Testing

### Unit Tests

```bash
# Backend tests
cd src/backend
pytest tests/

# Agent tests
cd src/agents/observability
pytest tests/
```

### Integration Tests

```bash
# Test agent communication
curl -X POST http://supervisor-agent:8080/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show CPU usage"}'

# Verify routing to Observability Agent
kubectl logs -f deployment/supervisor-agent -n nilabja-haldar-dev
```

### Load Tests

```bash
# Install k6
brew install k6

# Run load test
k6 run tests/load/backend-load-test.js
```

## 📚 Documentation

- [Architecture](docs/architecture.md) - Detailed architecture documentation
- [Deployment Guide](docs/deployment.md) - Step-by-step deployment
- [API Reference](docs/api-reference.md) - Complete API documentation
- [Troubleshooting](docs/troubleshooting.md) - Common issues and solutions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- Groq for Llama-3.1-70b API
- Prometheus, Grafana, Loki teams
- Kubernetes and OpenShift communities

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/your-repo/issues)
- **Slack:** #observability-platform
- **Email:** support@your-company.com

---

**Made with Bob** 🤖

**Version:** 1.0.0  
**Last Updated:** 2026-05-09