# Deployment Guide

Complete guide for deploying the AI-Powered Observability Platform on OpenShift ROSA or Kubernetes.

## Prerequisites

### Required Tools
- `kubectl` 1.28+
- `helm` 3.12+
- `oc` CLI (for OpenShift)
- `git`

### Required Access
- OpenShift ROSA cluster or Kubernetes 1.28+
- Namespace: `nilabja-haldar-dev`
- Cluster-admin or namespace-admin permissions

### Required Credentials
- OpenAI API key or Groq API key
- Slack bot token (for notifications)
- Confluence credentials (optional)

## Deployment Steps

### 1. Prepare Namespace

```bash
# Create namespace
kubectl create namespace nilabja-haldar-dev

# Set as default namespace
kubectl config set-context --current --namespace=nilabja-haldar-dev

# Verify
kubectl get namespace nilabja-haldar-dev
```

### 2. Create Secrets

```bash
# LLM API Keys
kubectl create secret generic llm-credentials \
  --from-literal=openai-api-key='sk-...' \
  --from-literal=groq-api-key='gsk_...' \
  -n nilabja-haldar-dev

# Slack Credentials
kubectl create secret generic slack-credentials \
  --from-literal=bot-token='xoxb-...' \
  --from-literal=webhook-url='https://hooks.slack.com/...' \
  -n nilabja-haldar-dev

# Confluence Credentials (optional)
kubectl create secret generic confluence-credentials \
  --from-literal=username='user@company.com' \
  --from-literal=api-token='...' \
  -n nilabja-haldar-dev

# Database Credentials
kubectl create secret generic postgresql-credentials \
  --from-literal=password='your-secure-password' \
  -n nilabja-haldar-dev
```

### 3. Deploy Observability Stack

#### 3.1 Prometheus

```bash
helm install prometheus ./charts/observability-stack/prometheus \
  -n nilabja-haldar-dev \
  --set persistence.enabled=true \
  --set persistence.size=10Gi
```

Verify:
```bash
kubectl get pods -l app=prometheus -n nilabja-haldar-dev
kubectl port-forward svc/prometheus 9090:9090 -n nilabja-haldar-dev
# Access: http://localhost:9090
```

#### 3.2 Grafana

```bash
helm install grafana ./charts/observability-stack/grafana \
  -n nilabja-haldar-dev \
  --set adminPassword='admin'
```

Verify:
```bash
kubectl get pods -l app=grafana -n nilabja-haldar-dev
kubectl port-forward svc/grafana 3000:3000 -n nilabja-haldar-dev
# Access: http://localhost:3000 (admin/admin)
```

#### 3.3 Loki

```bash
helm install loki ./charts/observability-stack/loki \
  -n nilabja-haldar-dev \
  --set persistence.enabled=true \
  --set persistence.size=10Gi
```

Verify:
```bash
kubectl get pods -l app=loki -n nilabja-haldar-dev
```

#### 3.4 Promtail

```bash
helm install promtail ./charts/observability-stack/promtail \
  -n nilabja-haldar-dev
```

Verify:
```bash
kubectl get daemonset promtail -n nilabja-haldar-dev
```

#### 3.5 Thanos (Optional)

```bash
helm install thanos ./charts/observability-stack/thanos \
  -n nilabja-haldar-dev \
  --set objstore.type=s3 \
  --set objstore.config.bucket='your-s3-bucket'
```

#### 3.6 Alertmanager

```bash
helm install alertmanager ./charts/observability-stack/alertmanager \
  -n nilabja-haldar-dev
```

### 4. Deploy Data Layer

#### 4.1 PostgreSQL

```bash
helm install postgresql ./charts/data-layer/postgresql \
  -n nilabja-haldar-dev \
  --set persistence.enabled=true \
  --set persistence.size=10Gi \
  --set auth.existingSecret=postgresql-credentials
```

Verify:
```bash
kubectl get statefulset postgresql -n nilabja-haldar-dev
kubectl get pvc -n nilabja-haldar-dev

# Test connection
kubectl exec -it postgresql-0 -n nilabja-haldar-dev -- psql -U postgres -c "SELECT version();"
```

### 5. Deploy AI Agents

#### 5.1 Supervisor Agent

```bash
helm install supervisor-agent ./charts/ai-agents/supervisor-agent \
  -n nilabja-haldar-dev \
  --set llm.provider=openai \
  --set llm.existingSecret=llm-credentials
```

Verify:
```bash
kubectl get pods -l app=supervisor-agent -n nilabja-haldar-dev
kubectl logs -f deployment/supervisor-agent -n nilabja-haldar-dev

# Test endpoint
kubectl port-forward svc/supervisor-agent 8080:8080 -n nilabja-haldar-dev
curl http://localhost:8080/health
```

#### 5.2 Observability Agent

```bash
helm install observability-agent ./charts/ai-agents/observability-agent \
  -n nilabja-haldar-dev \
  --set prometheus.url=http://prometheus:9090 \
  --set loki.url=http://loki:3100 \
  --set grafana.url=http://grafana:3000
```

Verify:
```bash
kubectl get pods -l app=observability-agent -n nilabja-haldar-dev
curl http://observability-agent:8081/health
```

#### 5.3 Pod Recovery Agent

```bash
helm install pod-recovery-agent ./charts/ai-agents/pod-recovery-agent \
  -n nilabja-haldar-dev
```

Verify:
```bash
kubectl get pods -l app=pod-recovery-agent -n nilabja-haldar-dev
curl http://pod-recovery-agent:8082/health
```

#### 5.4 Backup/Restore Agent

```bash
helm install backup-restore-agent ./charts/ai-agents/backup-restore-agent \
  -n nilabja-haldar-dev
```

Verify:
```bash
kubectl get pods -l app=backup-restore-agent -n nilabja-haldar-dev
curl http://backup-restore-agent:8083/health
```

### 6. Deploy E-commerce Application

#### 6.1 Backend

```bash
helm install backend ./charts/ecommerce-app/backend \
  -n nilabja-haldar-dev \
  --set database.host=postgresql \
  --set database.existingSecret=postgresql-credentials
```

Verify:
```bash
kubectl get pods -l app=backend -n nilabja-haldar-dev
kubectl logs -f deployment/backend -n nilabja-haldar-dev

# Test API
kubectl port-forward svc/backend 8000:8000 -n nilabja-haldar-dev
curl http://localhost:8000/health
```

#### 6.2 Frontend

```bash
helm install frontend ./charts/ecommerce-app/frontend \
  -n nilabja-haldar-dev \
  --set backend.url=http://backend:8000
```

Verify:
```bash
kubectl get pods -l app=frontend -n nilabja-haldar-dev
kubectl port-forward svc/frontend 3000:3000 -n nilabja-haldar-dev
# Access: http://localhost:3000
```

#### 6.3 Chat UI

```bash
helm install chat-ui ./charts/ecommerce-app/chat-ui \
  -n nilabja-haldar-dev \
  --set supervisor.url=http://supervisor-agent:8080
```

Verify:
```bash
kubectl get pods -l app=chat-ui -n nilabja-haldar-dev
kubectl port-forward svc/chat-ui 5173:5173 -n nilabja-haldar-dev
# Access: http://localhost:5173
```

### 7. Deploy Backup/Restore Tools (Optional)

#### 7.1 Velero

```bash
helm install velero ./charts/backup-restore/velero \
  -n nilabja-haldar-dev \
  --set configuration.provider=aws \
  --set configuration.backupStorageLocation.bucket=your-s3-bucket \
  --set credentials.existingSecret=velero-credentials
```

#### 7.2 Argo Workflows

```bash
helm install argo-workflows ./charts/backup-restore/argo-workflows \
  -n nilabja-haldar-dev
```

## Post-Deployment Configuration

### 1. Configure Grafana Data Sources

```bash
# Port-forward to Grafana
kubectl port-forward svc/grafana 3000:3000 -n nilabja-haldar-dev

# Login: admin/admin
# Add Prometheus data source: http://prometheus:9090
# Add Loki data source: http://loki:3100
```

### 2. Configure Slack Integration

1. Create Slack app at https://api.slack.com/apps
2. Enable Bot Token Scopes: `chat:write`, `chat:write.public`
3. Install app to workspace
4. Copy Bot Token to secret (already done in step 2)
5. Invite bot to channel: `/invite @your-bot-name`

### 3. Test AI Agents

```bash
# Test Supervisor Agent
curl -X POST http://supervisor-agent:8080/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me CPU usage for backend pods"}'

# Test Observability Agent
curl -X POST http://observability-agent:8081/detect-issues \
  -H "Content-Type: application/json" \
  -d '{"time_range": "5m"}'

# Test Pod Recovery Agent
curl -X POST http://pod-recovery-agent:8082/diagnose \
  -H "Content-Type: application/json" \
  -d '{"pod_name": "backend-xxx", "namespace": "nilabja-haldar-dev"}'

# Test Backup/Restore Agent
curl http://backup-restore-agent:8083/backups
```

## Verification Checklist

- [ ] All pods are running
- [ ] Prometheus is scraping metrics
- [ ] Grafana dashboards are accessible
- [ ] Loki is receiving logs
- [ ] AI agents are responding to queries
- [ ] Slack notifications are working
- [ ] E-commerce application is accessible
- [ ] Database is connected and healthy

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n nilabja-haldar-dev

# Check pod logs
kubectl logs <pod-name> -n nilabja-haldar-dev

# Check pod events
kubectl describe pod <pod-name> -n nilabja-haldar-dev
```

### Database Connection Issues

```bash
# Check PostgreSQL logs
kubectl logs postgresql-0 -n nilabja-haldar-dev

# Test connection
kubectl exec -it postgresql-0 -n nilabja-haldar-dev -- psql -U postgres

# Check secret
kubectl get secret postgresql-credentials -n nilabja-haldar-dev -o yaml
```

### AI Agent Errors

```bash
# Check agent logs
kubectl logs -f deployment/supervisor-agent -n nilabja-haldar-dev

# Check LLM credentials
kubectl get secret llm-credentials -n nilabja-haldar-dev -o yaml

# Test LLM connection
kubectl exec -it deployment/supervisor-agent -n nilabja-haldar-dev -- \
  python -c "from agents.common.llm_client import LLMClient; print(LLMClient().generate('test'))"
```

### Slack Integration Issues

```bash
# Check Slack credentials
kubectl get secret slack-credentials -n nilabja-haldar-dev -o yaml

# Test Slack connection
kubectl exec -it deployment/supervisor-agent -n nilabja-haldar-dev -- \
  python -c "from agents.common.tools.slack import SlackTool; SlackTool().send_message('test')"
```

## Upgrade

```bash
# Upgrade specific component
helm upgrade supervisor-agent ./charts/ai-agents/supervisor-agent \
  -n nilabja-haldar-dev \
  -f values-override.yaml

# Upgrade all components
./scripts/upgrade-all.sh
```

## Rollback

```bash
# Rollback specific component
helm rollback supervisor-agent -n nilabja-haldar-dev

# List releases
helm list -n nilabja-haldar-dev

# Get release history
helm history supervisor-agent -n nilabja-haldar-dev
```

## Uninstall

```bash
# Uninstall all components
helm uninstall supervisor-agent -n nilabja-haldar-dev
helm uninstall observability-agent -n nilabja-haldar-dev
helm uninstall pod-recovery-agent -n nilabja-haldar-dev
helm uninstall backup-restore-agent -n nilabja-haldar-dev
helm uninstall backend -n nilabja-haldar-dev
helm uninstall frontend -n nilabja-haldar-dev
helm uninstall chat-ui -n nilabja-haldar-dev
helm uninstall postgresql -n nilabja-haldar-dev
helm uninstall prometheus -n nilabja-haldar-dev
helm uninstall grafana -n nilabja-haldar-dev
helm uninstall loki -n nilabja-haldar-dev
helm uninstall promtail -n nilabja-haldar-dev

# Delete namespace (WARNING: This deletes all data)
kubectl delete namespace nilabja-haldar-dev
```

## Production Considerations

### High Availability

- Deploy multiple replicas of AI agents
- Use StatefulSets for databases
- Configure pod anti-affinity
- Use PodDisruptionBudgets

### Security

- Use NetworkPolicies to restrict traffic
- Enable RBAC with minimal permissions
- Use Secrets for sensitive data
- Enable TLS for all services
- Regular security scans

### Monitoring

- Set up alerts for critical metrics
- Configure log retention policies
- Monitor resource usage
- Set up backup verification

### Backup

- Schedule regular backups (daily)
- Test restore procedures
- Store backups off-cluster
- Document recovery procedures

---

**Made with Bob** 🤖