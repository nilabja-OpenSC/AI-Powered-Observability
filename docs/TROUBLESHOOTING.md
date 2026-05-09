# Troubleshooting Guide

Common issues and solutions for the AI-Powered Observability Platform.

## Table of Contents

- [Deployment Issues](#deployment-issues)
- [AI Agent Issues](#ai-agent-issues)
- [Observability Stack Issues](#observability-stack-issues)
- [Database Issues](#database-issues)
- [E-commerce Application Issues](#ecommerce-application-issues)
- [Slack Integration Issues](#slack-integration-issues)
- [Performance Issues](#performance-issues)

---

## Deployment Issues

### Pods Stuck in Pending State

**Symptoms:**
```bash
kubectl get pods -n nilabja-haldar-dev
NAME                    READY   STATUS    RESTARTS   AGE
backend-abc123          0/1     Pending   0          5m
```

**Diagnosis:**
```bash
kubectl describe pod backend-abc123 -n nilabja-haldar-dev
```

**Common Causes:**

1. **Insufficient Resources**
   ```
   Events:
     Warning  FailedScheduling  pod has unbound immediate PersistentVolumeClaims
   ```
   
   **Solution:**
   ```bash
   # Check PVC status
   kubectl get pvc -n nilabja-haldar-dev
   
   # If PVC is pending, check storage class
   kubectl get storageclass
   
   # Ensure storage class exists and is default
   kubectl patch storageclass gp2 -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
   ```

2. **Node Selector Mismatch**
   ```
   Events:
     Warning  FailedScheduling  0/3 nodes are available: 3 node(s) didn't match node selector
   ```
   
   **Solution:**
   ```bash
   # Remove node selector from values.yaml or add matching labels to nodes
   helm upgrade backend ./charts/ecommerce-app/backend \
     --set nodeSelector=null \
     -n nilabja-haldar-dev
   ```

### ImagePullBackOff Errors

**Symptoms:**
```bash
NAME                    READY   STATUS             RESTARTS   AGE
backend-abc123          0/1     ImagePullBackOff   0          2m
```

**Diagnosis:**
```bash
kubectl describe pod backend-abc123 -n nilabja-haldar-dev
```

**Common Causes:**

1. **Image Does Not Exist**
   ```
   Events:
     Warning  Failed  Failed to pull image "backend:latest": rpc error: code = NotFound
   ```
   
   **Solution:**
   ```bash
   # Build and push image
   docker build -t your-registry/backend:v1.0.0 ./src/backend
   docker push your-registry/backend:v1.0.0
   
   # Update Helm values
   helm upgrade backend ./charts/ecommerce-app/backend \
     --set image.repository=your-registry/backend \
     --set image.tag=v1.0.0 \
     -n nilabja-haldar-dev
   ```

2. **Private Registry Authentication**
   ```
   Events:
     Warning  Failed  Failed to pull image: unauthorized
   ```
   
   **Solution:**
   ```bash
   # Create image pull secret
   kubectl create secret docker-registry regcred \
     --docker-server=your-registry.com \
     --docker-username=your-username \
     --docker-password=your-password \
     -n nilabja-haldar-dev
   
   # Update Helm values
   helm upgrade backend ./charts/ecommerce-app/backend \
     --set imagePullSecrets[0].name=regcred \
     -n nilabja-haldar-dev
   ```

### CrashLoopBackOff Errors

**Symptoms:**
```bash
NAME                    READY   STATUS             RESTARTS   AGE
backend-abc123          0/1     CrashLoopBackOff   5          5m
```

**Diagnosis:**
```bash
# Check logs
kubectl logs backend-abc123 -n nilabja-haldar-dev

# Check previous container logs
kubectl logs backend-abc123 -n nilabja-haldar-dev --previous
```

**Common Causes:**

1. **Missing Environment Variables**
   ```
   Error: DATABASE_URL environment variable not set
   ```
   
   **Solution:**
   ```bash
   # Check ConfigMap/Secret
   kubectl get configmap backend-config -n nilabja-haldar-dev -o yaml
   kubectl get secret backend-secrets -n nilabja-haldar-dev -o yaml
   
   # Update values
   helm upgrade backend ./charts/ecommerce-app/backend \
     --set env.DATABASE_URL=postgresql://... \
     -n nilabja-haldar-dev
   ```

2. **Database Connection Failed**
   ```
   Error: could not connect to database: connection refused
   ```
   
   **Solution:**
   ```bash
   # Check PostgreSQL is running
   kubectl get pods -l app=postgresql -n nilabja-haldar-dev
   
   # Test connection
   kubectl exec -it backend-abc123 -n nilabja-haldar-dev -- \
     nc -zv postgresql 5432
   
   # Check service
   kubectl get svc postgresql -n nilabja-haldar-dev
   ```

---

## AI Agent Issues

### Agent Not Responding

**Symptoms:**
```bash
curl http://supervisor-agent:8080/health
curl: (7) Failed to connect to supervisor-agent port 8080: Connection refused
```

**Diagnosis:**
```bash
# Check pod status
kubectl get pods -l app=supervisor-agent -n nilabja-haldar-dev

# Check logs
kubectl logs -f deployment/supervisor-agent -n nilabja-haldar-dev
```

**Common Causes:**

1. **LLM API Key Invalid**
   ```
   Error: OpenAI API key is invalid
   ```
   
   **Solution:**
   ```bash
   # Update secret
   kubectl delete secret llm-credentials -n nilabja-haldar-dev
   kubectl create secret generic llm-credentials \
     --from-literal=openai-api-key='sk-...' \
     -n nilabja-haldar-dev
   
   # Restart agent
   kubectl rollout restart deployment/supervisor-agent -n nilabja-haldar-dev
   ```

2. **Vector Store Initialization Failed**
   ```
   Error: Failed to initialize Chroma vector store
   ```
   
   **Solution:**
   ```bash
   # Check PVC
   kubectl get pvc -l app=supervisor-agent -n nilabja-haldar-dev
   
   # Delete and recreate PVC if corrupted
   kubectl delete pvc supervisor-agent-data -n nilabja-haldar-dev
   kubectl rollout restart deployment/supervisor-agent -n nilabja-haldar-dev
   ```

### Agent Queries Timing Out

**Symptoms:**
```bash
curl -X POST http://supervisor-agent:8080/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show CPU usage"}' \
  --max-time 30
curl: (28) Operation timed out after 30000 milliseconds
```

**Diagnosis:**
```bash
# Check agent logs
kubectl logs -f deployment/supervisor-agent -n nilabja-haldar-dev

# Check resource usage
kubectl top pod -l app=supervisor-agent -n nilabja-haldar-dev
```

**Common Causes:**

1. **LLM Rate Limiting**
   ```
   Error: Rate limit exceeded for OpenAI API
   ```
   
   **Solution:**
   ```bash
   # Switch to Groq or increase OpenAI tier
   helm upgrade supervisor-agent ./charts/ai-agents/supervisor-agent \
     --set llm.provider=groq \
     --set llm.model=llama-3.1-70b-versatile \
     -n nilabja-haldar-dev
   ```

2. **Insufficient Resources**
   ```
   Warning: Memory usage at 95%
   ```
   
   **Solution:**
   ```bash
   # Increase resources
   helm upgrade supervisor-agent ./charts/ai-agents/supervisor-agent \
     --set resources.limits.memory=2Gi \
     --set resources.limits.cpu=1000m \
     -n nilabja-haldar-dev
   ```

### Approval Workflow Not Working

**Symptoms:**
- Slack notifications not received
- Approval buttons not responding

**Diagnosis:**
```bash
# Check Slack credentials
kubectl get secret slack-credentials -n nilabja-haldar-dev -o yaml

# Check agent logs
kubectl logs -f deployment/pod-recovery-agent -n nilabja-haldar-dev | grep -i slack
```

**Common Causes:**

1. **Invalid Slack Token**
   ```
   Error: Slack API error: invalid_auth
   ```
   
   **Solution:**
   ```bash
   # Update Slack token
   kubectl delete secret slack-credentials -n nilabja-haldar-dev
   kubectl create secret generic slack-credentials \
     --from-literal=bot-token='xoxb-...' \
     --from-literal=webhook-url='https://hooks.slack.com/...' \
     -n nilabja-haldar-dev
   
   # Restart agents
   kubectl rollout restart deployment/pod-recovery-agent -n nilabja-haldar-dev
   ```

2. **Bot Not Invited to Channel**
   ```
   Error: Slack API error: channel_not_found
   ```
   
   **Solution:**
   ```
   1. Go to Slack channel
   2. Type: /invite @your-bot-name
   3. Verify bot appears in channel members
   ```

---

## Observability Stack Issues

### Prometheus Not Scraping Metrics

**Symptoms:**
- No metrics in Prometheus UI
- Targets showing as "Down"

**Diagnosis:**
```bash
# Check Prometheus targets
kubectl port-forward svc/prometheus 9090:9090 -n nilabja-haldar-dev
# Visit: http://localhost:9090/targets

# Check ServiceMonitor
kubectl get servicemonitor -n nilabja-haldar-dev
```

**Common Causes:**

1. **ServiceMonitor Not Created**
   ```bash
   # Create ServiceMonitor
   kubectl apply -f - <<EOF
   apiVersion: monitoring.coreos.com/v1
   kind: ServiceMonitor
   metadata:
     name: backend
     namespace: nilabja-haldar-dev
   spec:
     selector:
       matchLabels:
         app: backend
     endpoints:
     - port: http
       path: /metrics
   EOF
   ```

2. **Metrics Endpoint Not Exposed**
   ```bash
   # Test metrics endpoint
   kubectl exec -it deployment/backend -n nilabja-haldar-dev -- \
     curl http://localhost:8000/metrics
   
   # If 404, ensure Prometheus client is configured in app
   ```

### Grafana Dashboards Not Loading

**Symptoms:**
- Dashboards show "No data"
- Data source connection failed

**Diagnosis:**
```bash
# Check Grafana logs
kubectl logs -f deployment/grafana -n nilabja-haldar-dev

# Check data source configuration
kubectl port-forward svc/grafana 3000:3000 -n nilabja-haldar-dev
# Visit: http://localhost:3000/datasources
```

**Common Causes:**

1. **Prometheus Data Source Not Configured**
   ```bash
   # Add Prometheus data source via API
   kubectl exec -it deployment/grafana -n nilabja-haldar-dev -- \
     curl -X POST http://admin:admin@localhost:3000/api/datasources \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Prometheus",
       "type": "prometheus",
       "url": "http://prometheus:9090",
       "access": "proxy",
       "isDefault": true
     }'
   ```

2. **Incorrect Query**
   ```
   Error: parse error: unexpected character: 'U+0027'
   ```
   
   **Solution:**
   - Check PromQL syntax
   - Ensure metric names are correct
   - Verify label selectors match actual labels

### Loki Not Receiving Logs

**Symptoms:**
- No logs in Grafana Explore
- Promtail pods not running

**Diagnosis:**
```bash
# Check Promtail pods
kubectl get pods -l app=promtail -n nilabja-haldar-dev

# Check Promtail logs
kubectl logs -f daemonset/promtail -n nilabja-haldar-dev

# Test Loki endpoint
kubectl exec -it deployment/loki -n nilabja-haldar-dev -- \
  curl http://localhost:3100/ready
```

**Common Causes:**

1. **Promtail Not Running on All Nodes**
   ```bash
   # Check DaemonSet
   kubectl get daemonset promtail -n nilabja-haldar-dev
   
   # Check node taints
   kubectl get nodes -o json | jq '.items[].spec.taints'
   
   # Add tolerations if needed
   helm upgrade promtail ./charts/observability-stack/promtail \
     --set tolerations[0].key=node-role.kubernetes.io/master \
     --set tolerations[0].effect=NoSchedule \
     -n nilabja-haldar-dev
   ```

2. **Loki Storage Full**
   ```
   Error: failed to write to storage: disk full
   ```
   
   **Solution:**
   ```bash
   # Increase PVC size
   kubectl patch pvc loki-data -n nilabja-haldar-dev \
     -p '{"spec":{"resources":{"requests":{"storage":"20Gi"}}}}'
   
   # Or enable log retention
   helm upgrade loki ./charts/observability-stack/loki \
     --set config.table_manager.retention_deletes_enabled=true \
     --set config.table_manager.retention_period=168h \
     -n nilabja-haldar-dev
   ```

---

## Database Issues

### PostgreSQL Not Starting

**Symptoms:**
```bash
kubectl get pods -l app=postgresql -n nilabja-haldar-dev
NAME           READY   STATUS    RESTARTS   AGE
postgresql-0   0/1     Error     3          5m
```

**Diagnosis:**
```bash
# Check logs
kubectl logs postgresql-0 -n nilabja-haldar-dev

# Check PVC
kubectl get pvc -l app=postgresql -n nilabja-haldar-dev
```

**Common Causes:**

1. **PVC Mount Failed**
   ```
   Error: failed to mount volume: permission denied
   ```
   
   **Solution:**
   ```bash
   # Check PVC status
   kubectl describe pvc postgresql-data -n nilabja-haldar-dev
   
   # If using EFS, ensure security group allows NFS traffic
   # If using EBS, ensure volume is in same AZ as node
   ```

2. **Data Directory Corrupted**
   ```
   Error: database files are incompatible with server
   ```
   
   **Solution:**
   ```bash
   # Backup data if possible
   kubectl exec -it postgresql-0 -n nilabja-haldar-dev -- \
     pg_dump -U postgres > backup.sql
   
   # Delete PVC and recreate
   kubectl delete pvc postgresql-data -n nilabja-haldar-dev
   kubectl delete pod postgresql-0 -n nilabja-haldar-dev
   
   # Restore from backup
   kubectl exec -it postgresql-0 -n nilabja-haldar-dev -- \
     psql -U postgres < backup.sql
   ```

### Connection Pool Exhausted

**Symptoms:**
```
Error: remaining connection slots are reserved for non-replication superuser connections
```

**Diagnosis:**
```bash
# Check active connections
kubectl exec -it postgresql-0 -n nilabja-haldar-dev -- \
  psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"
```

**Solution:**
```bash
# Increase max_connections
helm upgrade postgresql ./charts/data-layer/postgresql \
  --set postgresql.max_connections=200 \
  -n nilabja-haldar-dev

# Or configure connection pooling in application
```

---

## E-commerce Application Issues

### Backend API Errors

**Symptoms:**
```bash
curl http://backend:8000/api/products
{"error": "Internal Server Error"}
```

**Diagnosis:**
```bash
# Check logs
kubectl logs -f deployment/backend -n nilabja-haldar-dev

# Check database connection
kubectl exec -it deployment/backend -n nilabja-haldar-dev -- \
  python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://...'); print(engine.connect())"
```

**Common Causes:**

1. **Database Migration Not Run**
   ```
   Error: relation "products" does not exist
   ```
   
   **Solution:**
   ```bash
   # Run migrations
   kubectl exec -it deployment/backend -n nilabja-haldar-dev -- \
     alembic upgrade head
   ```

2. **CORS Issues**
   ```
   Error: CORS policy: No 'Access-Control-Allow-Origin' header
   ```
   
   **Solution:**
   ```bash
   # Update CORS settings
   helm upgrade backend ./charts/ecommerce-app/backend \
     --set env.CORS_ORIGINS='["http://frontend:3000"]' \
     -n nilabja-haldar-dev
   ```

### Frontend Not Loading

**Symptoms:**
- Blank page
- Console errors

**Diagnosis:**
```bash
# Check logs
kubectl logs -f deployment/frontend -n nilabja-haldar-dev

# Check browser console
# Press F12 in browser and check Console tab
```

**Common Causes:**

1. **Backend URL Incorrect**
   ```
   Error: Failed to fetch: net::ERR_NAME_NOT_RESOLVED
   ```
   
   **Solution:**
   ```bash
   # Update backend URL
   helm upgrade frontend ./charts/ecommerce-app/frontend \
     --set env.NEXT_PUBLIC_API_URL=http://backend:8000 \
     -n nilabja-haldar-dev
   ```

2. **Build Failed**
   ```
   Error: Module not found: Can't resolve 'react'
   ```
   
   **Solution:**
   ```bash
   # Rebuild image with dependencies
   cd src/frontend
   npm install
   docker build -t frontend:v1.0.1 .
   docker push frontend:v1.0.1
   ```

---

## Slack Integration Issues

### Notifications Not Sent

**Diagnosis:**
```bash
# Test Slack webhook
curl -X POST https://hooks.slack.com/services/YOUR/WEBHOOK/URL \
  -H "Content-Type: application/json" \
  -d '{"text": "Test message"}'
```

**Solution:**
```bash
# Verify webhook URL
kubectl get secret slack-credentials -n nilabja-haldar-dev -o jsonpath='{.data.webhook-url}' | base64 -d

# Update if incorrect
kubectl delete secret slack-credentials -n nilabja-haldar-dev
kubectl create secret generic slack-credentials \
  --from-literal=webhook-url='https://hooks.slack.com/...' \
  -n nilabja-haldar-dev
```

---

## Performance Issues

### High Memory Usage

**Diagnosis:**
```bash
# Check memory usage
kubectl top pods -n nilabja-haldar-dev

# Check OOMKilled events
kubectl get events -n nilabja-haldar-dev | grep OOMKilled
```

**Solution:**
```bash
# Increase memory limits
helm upgrade <component> ./charts/<path> \
  --set resources.limits.memory=2Gi \
  -n nilabja-haldar-dev

# Enable memory profiling
kubectl exec -it deployment/<component> -n nilabja-haldar-dev -- \
  python -m memory_profiler app.py
```

### Slow Query Performance

**Diagnosis:**
```bash
# Check slow queries in PostgreSQL
kubectl exec -it postgresql-0 -n nilabja-haldar-dev -- \
  psql -U postgres -c "SELECT query, calls, total_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

**Solution:**
```bash
# Add indexes
kubectl exec -it postgresql-0 -n nilabja-haldar-dev -- \
  psql -U postgres -c "CREATE INDEX idx_products_name ON products(name);"

# Analyze query plans
kubectl exec -it postgresql-0 -n nilabja-haldar-dev -- \
  psql -U postgres -c "EXPLAIN ANALYZE SELECT * FROM products WHERE name LIKE '%search%';"
```

---

## Getting Help

If you're still experiencing issues:

1. **Check Logs:** Always start with pod logs
2. **Search Issues:** Check GitHub issues for similar problems
3. **Ask Community:** Post in Slack #observability-help channel
4. **Create Issue:** Open GitHub issue with:
   - Detailed description
   - Steps to reproduce
   - Logs and error messages
   - Environment details

---

**Made with Bob** 🤖