# Deployment Guide - AI-Powered Observability Platform

This guide provides step-by-step instructions to deploy all components of the AI-Powered Observability Platform to OpenShift ROSA.

## Prerequisites

### 1. Tools Required
```bash
# Verify installations
helm version          # Helm 3.x required
oc version           # OpenShift CLI
kubectl version      # Kubernetes CLI
```

### 2. OpenShift Cluster Access
```bash
# Login to OpenShift cluster
oc login --token=<your-token> --server=<your-server-url>

# Verify access
oc whoami
oc cluster-info
```

### 3. Create Namespace
```bash
# Create the project namespace
oc new-project nilabja-haldar-dev

# Verify namespace
oc project nilabja-haldar-dev
```

## Deployment Order

Components must be deployed in the following order to ensure proper dependencies:

1. **Data Layer** (PostgreSQL)
2. **Observability Stack** (Prometheus, Loki, Promtail, Alertmanager, Thanos, Grafana)
3. **Backup/Restore** (Velero, Argo Workflows)
4. **E-commerce Application** (Backend, Frontend, Chat-UI)
5. **AI Agents** (Supervisor, Observability, Pod-Recovery, Backup-Restore)

---

## Phase 1: Data Layer Deployment

### 1.1 Create Secrets
```bash
# Create PostgreSQL secret
oc create secret generic postgresql-secret \
  --from-literal=postgres-password='your-secure-password' \
  --from-literal=replication-password='your-replication-password' \
  -n nilabja-haldar-dev

# Create AI Agents secret (for all agents)
oc create secret generic ai-agents-secret \
  --from-literal=OPENAI_API_KEY='your-openai-api-key' \
  --from-literal=SLACK_WEBHOOK_URL='your-slack-webhook-url' \
  --from-literal=SLACK_BOT_TOKEN='your-slack-bot-token' \
  --from-literal=SLACK_SIGNING_SECRET='your-slack-signing-secret' \
  -n nilabja-haldar-dev

# Verify secrets
oc get secrets -n nilabja-haldar-dev
```

### 1.2 Deploy PostgreSQL
```bash
# Validate chart
helm lint charts/data-layer/postgresql

# Dry-run to check manifests
helm install postgresql charts/data-layer/postgresql \
  --namespace nilabja-haldar-dev \
  --dry-run --debug

# Deploy PostgreSQL
helm install postgresql charts/data-layer/postgresql \
  --namespace nilabja-haldar-dev \
  --set secrets.name=postgresql-secret

# Verify deployment
oc get pods -n nilabja-haldar-dev -l app.kubernetes.io/name=postgresql
oc get pvc -n nilabja-haldar-dev
oc logs -f deployment/postgresql -n nilabja-haldar-dev
```

---

## Phase 2: Observability Stack Deployment

### 2.1 Deploy Prometheus
```bash
# Validate chart
helm lint charts/observability-stack/prometheus

# Deploy Prometheus
helm install prometheus charts/observability-stack/prometheus \
  --namespace nilabja-haldar-dev \
  --set config.alertmanagerUrl=http://alertmanager:9093

# Verify deployment
oc get pods -n nilabja-haldar-dev -l app.kubernetes.io/name=prometheus
oc get pvc -n nilabja-haldar-dev | grep prometheus
oc get svc -n nilabja-haldar-dev | grep prometheus

# Check Prometheus UI (port-forward)
oc port-forward svc/prometheus 9090:9090 -n nilabja-haldar-dev
# Access: http://localhost:9090
```

### 2.2 Deploy Loki
```bash
# Deploy Loki
helm install loki charts/observability-stack/loki \
  --namespace nilabja-haldar-dev \
  --set config.alertmanagerUrl=http://alertmanager:9093

# Verify deployment
oc get pods -n nilabja-haldar-dev -l app.kubernetes.io/name=loki
oc get pvc -n nilabja-haldar-dev | grep loki
```

### 2.3 Deploy Promtail
```bash
# Deploy Promtail (DaemonSet)
helm install promtail charts/observability-stack/promtail \
  --namespace nilabja-haldar-dev \
  --set config.lokiUrl=http://loki:3100

# Verify deployment (should have 1 pod per node)
oc get pods -n nilabja-haldar-dev -l app.kubernetes.io/name=promtail
oc get daemonset -n nilabja-haldar-dev
```

### 2.4 Deploy Alertmanager
```bash
# Create Alertmanager secret for Slack
oc create secret generic alertmanager-secret \
  --from-literal=slack-webhook-url='your-slack-webhook-url' \
  -n nilabja-haldar-dev

# Deploy Alertmanager
helm install alertmanager charts/observability-stack/alertmanager \
  --namespace nilabja-haldar-dev \
  --set config.slackWebhookUrl='your-slack-webhook-url'

# Verify deployment
oc get pods -n nilabja-haldar-dev -l app.kubernetes.io/name=alertmanager
```

### 2.5 Deploy Thanos
```bash
# Create Thanos S3 secret
oc create secret generic thanos-s3-secret \
  --from-literal=access-key='your-s3-access-key' \
  --from-literal=secret-key='your-s3-secret-key' \
  -n nilabja-haldar-dev

# Deploy Thanos
helm install thanos charts/observability-stack/thanos \
  --namespace nilabja-haldar-dev \
  --set config.prometheusUrl=http://prometheus:9090 \
  --set config.s3Bucket=your-bucket-name \
  --set config.s3Endpoint=s3.amazonaws.com

# Verify deployment
oc get pods -n nilabja-haldar-dev -l app.kubernetes.io/name=thanos
```

### 2.6 Deploy Grafana
```bash
# Create Grafana secret
oc create secret generic grafana-secret \
  --from-literal=admin-user=admin \
  --from-literal=admin-password='your-grafana-password' \
  -n nilabja-haldar-dev

# Deploy Grafana
helm install grafana charts/observability-stack/grafana \
  --namespace nilabja-haldar-dev \
  --set secrets.name=grafana-secret \
  --set config.prometheusUrl=http://prometheus:9090 \
  --set config.lokiUrl=http://loki:3100 \
  --set config.thanosUrl=http://thanos-query:10902

# Verify deployment
oc get pods -n nilabja-haldar-dev -l app.kubernetes.io/name=grafana

# Access Grafana UI
oc port-forward svc/grafana 3000:3000 -n nilabja-haldar-dev
# Access: http://localhost:3000 (admin/your-grafana-password)
```

---

## Phase 3: Backup/Restore Stack Deployment

### 3.1 Deploy Velero
```bash
# Create Velero S3 credentials
cat > credentials-velero <<EOF
[default]
aws_access_key_id=your-access-key
aws_secret_access_key=your-secret-key
EOF

oc create secret generic velero-credentials \
  --from-file=cloud=credentials-velero \
  -n nilabja-haldar-dev

rm credentials-velero  # Clean up

# Deploy Velero
helm install velero charts/backup-restore/velero \
  --namespace nilabja-haldar-dev \
  --set secrets.name=velero-credentials \
  --set config.bucket=your-velero-bucket \
  --set config.region=us-east-1

# Verify deployment
oc get pods -n nilabja-haldar-dev -l app.kubernetes.io/name=velero

# Check backup schedule
oc get schedule -n nilabja-haldar-dev
```

### 3.2 Deploy Argo Workflows
```bash
# Create Argo Workflows S3 secret
oc create secret generic argo-workflows-secret \
  --from-literal=accesskey='your-s3-access-key' \
  --from-literal=secretkey='your-s3-secret-key' \
  -n nilabja-haldar-dev

# Deploy Argo Workflows
helm install argo-workflows charts/backup-restore/argo-workflows \
  --namespace nilabja-haldar-dev \
  --set secrets.name=argo-workflows-secret \
  --set config.artifactBucket=your-argo-bucket

# Verify deployment
oc get pods -n nilabja-haldar-dev -l app.kubernetes.io/name=argo-workflows

# Access Argo UI
oc port-forward svc/argo-workflows-server 2746:2746 -n nilabja-haldar-dev
# Access: http://localhost:2746
```

---

## Phase 4: E-commerce Application Deployment

### 4.1 Deploy Backend
```bash
# Deploy Backend
helm install backend charts/ecommerce-app/backend \
  --namespace nilabja-haldar-dev \
  --set config.databaseUrl=postgresql://postgres:password@postgresql:5432/ecommerce

# Verify deployment
oc get pods -n nilabja-haldar-dev -l app.kubernetes.io/name=backend
oc logs -f deployment/backend -n nilabja-haldar-dev
```

### 4.2 Deploy Frontend
```bash
# Deploy Frontend
helm install frontend charts/ecommerce-app/frontend \
  --namespace nilabja-haldar-dev \
  --set config.backendUrl=http://backend:8000

# Verify deployment
oc get pods -n nilabja-haldar-dev -l app.kubernetes.io/name=frontend

# Create route for external access
oc expose svc/frontend -n nilabja-haldar-dev
oc get route frontend -n nilabja-haldar-dev
```

### 4.3 Deploy Chat-UI
```bash
# Deploy Chat-UI
helm install chat-ui charts/ecommerce-app/chat-ui \
  --namespace nilabja-haldar-dev \
  --set config.backendUrl=http://backend:8000 \
  --set config.supervisorUrl=http://supervisor-agent:8080

# Verify deployment
oc get pods -n nilabja-haldar-dev -l app.kubernetes.io/name=chat-ui

# Create route for external access
oc expose svc/chat-ui -n nilabja-haldar-dev
oc get route chat-ui -n nilabja-haldar-dev
```

---

## Phase 5: AI Agents Deployment

### 5.1 Deploy Supervisor Agent
```bash
# Deploy Supervisor Agent
helm install supervisor-agent charts/ai-agents/supervisor-agent \
  --namespace nilabja-haldar-dev \
  --set secrets.name=ai-agents-secret \
  --set config.llmProvider=openai \
  --set config.llmModel=gpt-4

# Verify deployment
oc get pods -n nilabja-haldar-dev -l app.kubernetes.io/name=supervisor-agent
oc logs -f deployment/supervisor-agent -n nilabja-haldar-dev
```

### 5.2 Deploy Observability Agent
```bash
# Deploy Observability Agent
helm install observability-agent charts/ai-agents/observability-agent \
  --namespace nilabja-haldar-dev \
  --set secrets.name=ai-agents-secret \
  --set config.prometheusUrl=http://prometheus:9090 \
  --set config.grafanaUrl=http://grafana:3000 \
  --set config.lokiUrl=http://loki:3100 \
  --set config.supervisorUrl=http://supervisor-agent:8080

# Verify deployment
oc get pods -n nilabja-haldar-dev -l app.kubernetes.io/name=observability-agent
```

### 5.3 Deploy Pod Recovery Agent
```bash
# Deploy Pod Recovery Agent
helm install pod-recovery-agent charts/ai-agents/pod-recovery-agent \
  --namespace nilabja-haldar-dev \
  --set secrets.name=ai-agents-secret \
  --set config.prometheusUrl=http://prometheus:9090 \
  --set config.supervisorUrl=http://supervisor-agent:8080

# Verify deployment
oc get pods -n nilabja-haldar-dev -l app.kubernetes.io/name=pod-recovery-agent
```

### 5.4 Deploy Backup/Restore Agent
```bash
# Deploy Backup/Restore Agent
helm install backup-restore-agent charts/ai-agents/backup-restore-agent \
  --namespace nilabja-haldar-dev \
  --set secrets.name=ai-agents-secret \
  --set config.veleroNamespace=nilabja-haldar-dev \
  --set config.argoWorkflowsNamespace=nilabja-haldar-dev \
  --set config.supervisorUrl=http://supervisor-agent:8080

# Verify deployment
oc get pods -n nilabja-haldar-dev -l app.kubernetes.io/name=backup-restore-agent
```

---

## Verification & Testing

### 1. Check All Deployments
```bash
# List all pods
oc get pods -n nilabja-haldar-dev

# Check pod status
oc get pods -n nilabja-haldar-dev --field-selector=status.phase!=Running

# View all services
oc get svc -n nilabja-haldar-dev

# View all routes
oc get routes -n nilabja-haldar-dev

# Check PVCs
oc get pvc -n nilabja-haldar-dev
```

### 2. Test Observability Stack
```bash
# Port-forward Prometheus
oc port-forward svc/prometheus 9090:9090 -n nilabja-haldar-dev &

# Port-forward Grafana
oc port-forward svc/grafana 3000:3000 -n nilabja-haldar-dev &

# Test Prometheus query
curl http://localhost:9090/api/v1/query?query=up

# Access Grafana dashboards
# http://localhost:3000
```

### 3. Test AI Agents
```bash
# Check supervisor agent logs
oc logs -f deployment/supervisor-agent -n nilabja-haldar-dev

# Test observability agent
oc logs -f deployment/observability-agent -n nilabja-haldar-dev

# Trigger a test alert (optional)
oc scale deployment/backend --replicas=0 -n nilabja-haldar-dev
# Wait for alert to fire, then restore
oc scale deployment/backend --replicas=1 -n nilabja-haldar-dev
```

### 4. Test E-commerce Application
```bash
# Get frontend URL
FRONTEND_URL=$(oc get route frontend -n nilabja-haldar-dev -o jsonpath='{.spec.host}')
echo "Frontend: https://$FRONTEND_URL"

# Get chat-ui URL
CHAT_UI_URL=$(oc get route chat-ui -n nilabja-haldar-dev -o jsonpath='{.spec.host}')
echo "Chat UI: https://$CHAT_UI_URL"

# Test backend health
oc port-forward svc/backend 8000:8000 -n nilabja-haldar-dev &
curl http://localhost:8000/health
```

---

## Monitoring & Maintenance

### View Logs
```bash
# View logs for specific component
oc logs -f deployment/<component-name> -n nilabja-haldar-dev

# View logs for all pods with label
oc logs -l app.kubernetes.io/name=<component-name> -n nilabja-haldar-dev --tail=100

# Stream logs from multiple pods
stern <component-name> -n nilabja-haldar-dev
```

### Scale Components
```bash
# Scale deployment
oc scale deployment/<component-name> --replicas=3 -n nilabja-haldar-dev

# Check scaling status
oc get hpa -n nilabja-haldar-dev
```

### Update Components
```bash
# Update a deployment
helm upgrade <release-name> charts/<chart-path> \
  --namespace nilabja-haldar-dev \
  --set <key>=<value>

# Rollback if needed
helm rollback <release-name> -n nilabja-haldar-dev
```

---

## Troubleshooting

### Common Issues

#### 1. Pod Not Starting
```bash
# Describe pod to see events
oc describe pod <pod-name> -n nilabja-haldar-dev

# Check pod logs
oc logs <pod-name> -n nilabja-haldar-dev

# Check previous container logs (if crashed)
oc logs <pod-name> -n nilabja-haldar-dev --previous
```

#### 2. PVC Not Binding
```bash
# Check PVC status
oc get pvc -n nilabja-haldar-dev

# Describe PVC
oc describe pvc <pvc-name> -n nilabja-haldar-dev

# Check storage class
oc get storageclass
```

#### 3. Service Not Accessible
```bash
# Check service endpoints
oc get endpoints <service-name> -n nilabja-haldar-dev

# Test service connectivity
oc run test-pod --image=curlimages/curl -it --rm -- sh
# Inside pod: curl http://<service-name>:<port>
```

#### 4. Agent Not Connecting to Slack
```bash
# Verify secret exists
oc get secret ai-agents-secret -n nilabja-haldar-dev -o yaml

# Check agent logs for connection errors
oc logs deployment/supervisor-agent -n nilabja-haldar-dev | grep -i slack

# Test Slack webhook manually
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test message"}' \
  <your-slack-webhook-url>
```

---

## Cleanup

### Uninstall All Components
```bash
# Uninstall in reverse order
helm uninstall backup-restore-agent -n nilabja-haldar-dev
helm uninstall pod-recovery-agent -n nilabja-haldar-dev
helm uninstall observability-agent -n nilabja-haldar-dev
helm uninstall supervisor-agent -n nilabja-haldar-dev

helm uninstall chat-ui -n nilabja-haldar-dev
helm uninstall frontend -n nilabja-haldar-dev
helm uninstall backend -n nilabja-haldar-dev

helm uninstall argo-workflows -n nilabja-haldar-dev
helm uninstall velero -n nilabja-haldar-dev

helm uninstall grafana -n nilabja-haldar-dev
helm uninstall thanos -n nilabja-haldar-dev
helm uninstall alertmanager -n nilabja-haldar-dev
helm uninstall promtail -n nilabja-haldar-dev
helm uninstall loki -n nilabja-haldar-dev
helm uninstall prometheus -n nilabja-haldar-dev

helm uninstall postgresql -n nilabja-haldar-dev

# Delete PVCs (if needed)
oc delete pvc --all -n nilabja-haldar-dev

# Delete secrets
oc delete secret --all -n nilabja-haldar-dev

# Delete namespace
oc delete project nilabja-haldar-dev
```

---

## Additional Resources

- **Helm Documentation**: https://helm.sh/docs/
- **OpenShift Documentation**: https://docs.openshift.com/
- **Prometheus Documentation**: https://prometheus.io/docs/
- **Grafana Documentation**: https://grafana.com/docs/
- **Velero Documentation**: https://velero.io/docs/
- **Argo Workflows Documentation**: https://argoproj.github.io/argo-workflows/

---

## Support

For issues or questions:
1. Check component logs: `oc logs -f deployment/<component> -n nilabja-haldar-dev`
2. Review Slack notifications in `#observability-alerts` channel
3. Check Grafana dashboards for metrics
4. Review Confluence documentation for incident reports