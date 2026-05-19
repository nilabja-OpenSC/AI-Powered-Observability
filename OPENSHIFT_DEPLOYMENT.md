# OpenShift Deployment Guide for Frontend & Chat-UI

This guide explains how the Frontend UI and Chat-UI are deployed to OpenShift using Helm charts and container images.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    OpenShift ROSA Cluster                        │
│                  Namespace: nilabja-haldar-dev                   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    External Access                        │  │
│  │  ┌────────────────┐         ┌────────────────┐          │  │
│  │  │  OpenShift     │         │  OpenShift     │          │  │
│  │  │  Route (TLS)   │         │  Route (TLS)   │          │  │
│  │  │  shop.apps...  │         │  chat.apps...  │          │  │
│  │  └───────┬────────┘         └───────┬────────┘          │  │
│  └──────────┼──────────────────────────┼───────────────────┘  │
│             │                          │                        │
│  ┌──────────▼────────┐      ┌──────────▼────────┐             │
│  │   Service          │      │   Service          │             │
│  │   frontend-ui      │      │   chat-ui          │             │
│  │   Port: 3000       │      │   Port: 3001       │             │
│  └──────────┬─────────┘      └──────────┬─────────┘             │
│             │                           │                        │
│  ┌──────────▼─────────┐     ┌──────────▼─────────┐             │
│  │  Deployment (HPA)  │     │  Deployment (HPA)  │             │
│  │  Replicas: 2-5     │     │  Replicas: 2-5     │             │
│  │  ┌──────┐ ┌──────┐ │     │  ┌──────┐ ┌──────┐ │             │
│  │  │ Pod  │ │ Pod  │ │     │  │ Pod  │ │ Pod  │ │             │
│  │  │Next.js│ │Next.js│ │     │  │React │ │React │ │             │
│  │  └──────┘ └──────┘ │     │  └──────┘ └──────┘ │             │
│  └────────────────────┘     └────────────────────┘             │
│             │                           │                        │
│             │ Connects to               │ Connects to            │
│             ▼                           ▼                        │
│  ┌─────────────────────┐    ┌─────────────────────┐            │
│  │  Backend API        │    │  Supervisor Agent   │            │
│  │  Service: backend   │    │  Service: supervisor│            │
│  │  Port: 8000         │    │  Port: 8080         │            │
│  └─────────────────────┘    └─────────────────────┘            │
└───────────────────────────────────────────────────────────────┘
```

## 📦 Container Images

### Frontend UI Dockerfile
Location: [`src/frontend/Dockerfile`](src/frontend/Dockerfile)

**Multi-stage Build:**
1. **Builder Stage**: Builds Next.js application
   - Base: `node:18-alpine`
   - Runs `npm ci` and `npm run build`
   - Optimizes for production

2. **Production Stage**: Runs the application
   - Base: `node:18-alpine`
   - Non-root user (UID 1000)
   - Exposes port 3000
   - Health check on `/api/health`
   - Command: `npm start`

### Chat-UI Dockerfile
Location: [`src/chat-ui/Dockerfile`](src/chat-ui/Dockerfile)

**Multi-stage Build:**
1. **Builder Stage**: Builds React/Vite application
   - Base: `node:18-alpine`
   - Runs `npm ci` and `npm run build`
   - Creates optimized static bundle

2. **Production Stage**: Serves static files
   - Base: `node:18-alpine`
   - Uses `serve` to host static files
   - Non-root user (UID 1000)
   - Exposes port 3000
   - Health check with wget
   - Command: `serve -s build -l 3000`

## 🎯 Helm Charts

### Frontend UI Chart
Location: [`charts/ecommerce-app/frontend/`](charts/ecommerce-app/frontend/)

**Key Configuration ([`values.yaml`](charts/ecommerce-app/frontend/values.yaml)):**

```yaml
# Deployment
replicaCount: 2
image:
  repository: frontend-ui
  tag: "1.0.0"

# Service
service:
  type: ClusterIP
  port: 3000

# OpenShift Route (External Access)
route:
  enabled: true
  host: shop-nilabja-haldar-dev.apps.rosa.example.com
  tls:
    enabled: true
    termination: edge

# Environment Variables
env:
  - name: NEXT_PUBLIC_API_URL
    value: "https://backend-api-nilabja-haldar-dev.apps.rosa.example.com/api/v1"
  - name: NODE_ENV
    value: "production"

# Resources
resources:
  requests:
    cpu: 50m
    memory: 128Mi
  limits:
    cpu: 200m
    memory: 256Mi

# Autoscaling
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 5
  targetCPUUtilizationPercentage: 70

# Security
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000
```

### Chat-UI Chart
Location: [`charts/ecommerce-app/chat-ui/`](charts/ecommerce-app/chat-ui/)

**Key Configuration ([`values.yaml`](charts/ecommerce-app/chat-ui/values.yaml)):**

```yaml
# Deployment
replicaCount: 2
image:
  repository: chat-ui
  tag: "1.0.0"

# Service
service:
  type: ClusterIP
  port: 3001

# OpenShift Route
route:
  enabled: true
  host: chat-nilabja-haldar-dev.apps.rosa.example.com
  tls:
    enabled: true
    termination: edge

# Environment Variables
env:
  - name: NEXT_PUBLIC_AGENT_API_URL
    value: "http://supervisor-agent.nilabja-haldar-dev.svc.cluster.local:8080"
  - name: NEXT_PUBLIC_AGENT_WS_URL
    value: "ws://supervisor-agent.nilabja-haldar-dev.svc.cluster.local:8080/ws"

# WebSocket Support
websocket:
  enabled: true
  path: /ws
  pingInterval: 30000
  timeout: 300000
```

## 🚀 Deployment Process

### Step 1: Build Container Images

```bash
# Set your container registry
export REGISTRY="quay.io"  # or docker.io, ghcr.io
export USERNAME="your-username"
export TAG="v1.0.0"

# Build Frontend UI
cd src/frontend
docker build -t ${REGISTRY}/${USERNAME}/frontend-ui:${TAG} .
docker push ${REGISTRY}/${USERNAME}/frontend-ui:${TAG}

# Build Chat-UI
cd ../chat-ui
docker build -t ${REGISTRY}/${USERNAME}/chat-ui:${TAG} .
docker push ${REGISTRY}/${USERNAME}/chat-ui:${TAG}
```

**Or use the automated script:**
```bash
chmod +x scripts/build-and-push-images.sh
./scripts/build-and-push-images.sh
```

### Step 2: Update Helm Values

Update image references in Helm charts:

**Frontend (`charts/ecommerce-app/frontend/values.yaml`):**
```yaml
image:
  repository: quay.io/your-username/frontend-ui
  tag: "v1.0.0"
  pullPolicy: IfNotPresent
```

**Chat-UI (`charts/ecommerce-app/chat-ui/values.yaml`):**
```yaml
image:
  repository: quay.io/your-username/chat-ui
  tag: "v1.0.0"
  pullPolicy: IfNotPresent
```

### Step 3: Deploy to OpenShift

```bash
# Login to OpenShift
oc login --token=<your-token> --server=<your-server-url>

# Create/switch to namespace
oc new-project nilabja-haldar-dev
# or
oc project nilabja-haldar-dev

# Deploy Frontend UI
helm upgrade --install frontend-ui \
  charts/ecommerce-app/frontend/ \
  --namespace nilabja-haldar-dev \
  --timeout 5m \
  --wait

# Deploy Chat-UI
helm upgrade --install chat-ui \
  charts/ecommerce-app/chat-ui/ \
  --namespace nilabja-haldar-dev \
  --timeout 5m \
  --wait
```

**Or use the automated deployment script:**
```bash
chmod +x scripts/deploy-all.sh
./scripts/deploy-all.sh
```

### Step 4: Verify Deployment

```bash
# Check deployments
oc get deployments -n nilabja-haldar-dev

# Check pods
oc get pods -n nilabja-haldar-dev | grep -E 'frontend-ui|chat-ui'

# Check services
oc get svc -n nilabja-haldar-dev | grep -E 'frontend-ui|chat-ui'

# Check routes
oc get routes -n nilabja-haldar-dev | grep -E 'frontend-ui|chat-ui'

# View logs
oc logs -f deployment/frontend-ui -n nilabja-haldar-dev
oc logs -f deployment/chat-ui -n nilabja-haldar-dev
```

## 🔗 Accessing the Applications

### Frontend UI
```bash
# Get the route URL
oc get route frontend-ui -n nilabja-haldar-dev -o jsonpath='{.spec.host}'

# Access via browser
https://shop-nilabja-haldar-dev.apps.rosa.example.com
```

### Chat-UI
```bash
# Get the route URL
oc get route chat-ui -n nilabja-haldar-dev -o jsonpath='{.spec.host}'

# Access via browser
https://chat-nilabja-haldar-dev.apps.rosa.example.com
```

## 🔧 Configuration

### Environment Variables

**Frontend UI:**
- `NEXT_PUBLIC_API_URL` - Backend API endpoint
- `NODE_ENV` - Environment (production/development)
- `NEXT_PUBLIC_ENABLE_CART` - Enable shopping cart
- `NEXT_PUBLIC_CURRENCY` - Currency code (USD)

**Chat-UI:**
- `NEXT_PUBLIC_AGENT_API_URL` - Supervisor agent HTTP endpoint
- `NEXT_PUBLIC_AGENT_WS_URL` - Supervisor agent WebSocket endpoint
- `NEXT_PUBLIC_PROMETHEUS_URL` - Prometheus endpoint
- `NEXT_PUBLIC_LOKI_URL` - Loki endpoint
- `NEXT_PUBLIC_GRAFANA_URL` - Grafana endpoint

### Updating Configuration

```bash
# Edit values
vim charts/ecommerce-app/frontend/values.yaml

# Apply changes
helm upgrade frontend-ui charts/ecommerce-app/frontend/ \
  --namespace nilabja-haldar-dev \
  --reuse-values

# Restart pods to pick up changes
oc rollout restart deployment/frontend-ui -n nilabja-haldar-dev
```

## 📊 Monitoring & Scaling

### Horizontal Pod Autoscaling (HPA)

Both UIs have HPA enabled:

```bash
# Check HPA status
oc get hpa -n nilabja-haldar-dev

# View HPA details
oc describe hpa frontend-ui -n nilabja-haldar-dev
oc describe hpa chat-ui -n nilabja-haldar-dev
```

**Scaling Configuration:**
- Min Replicas: 2
- Max Replicas: 5
- Target CPU: 70%
- Target Memory: 80%

### Manual Scaling

```bash
# Scale frontend
oc scale deployment/frontend-ui --replicas=3 -n nilabja-haldar-dev

# Scale chat-ui
oc scale deployment/chat-ui --replicas=3 -n nilabja-haldar-dev
```

### Resource Monitoring

```bash
# View resource usage
oc top pods -n nilabja-haldar-dev | grep -E 'frontend-ui|chat-ui'

# View events
oc get events -n nilabja-haldar-dev --sort-by='.lastTimestamp'
```

## 🔒 Security Features

### Non-Root Containers
Both containers run as UID 1000 (non-root user)

### Read-Only Root Filesystem
```yaml
podSecurityContext:
  readOnlyRootFilesystem: true
```

### Security Context Constraints (SCC)
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000
  seccompProfile:
    type: RuntimeDefault
```

### Network Policies
- Frontend: Allows ingress from OpenShift Router, egress to Backend API
- Chat-UI: Allows ingress from OpenShift Router, egress to Supervisor Agent

## 🐛 Troubleshooting

### Pods Not Starting

```bash
# Check pod status
oc get pods -n nilabja-haldar-dev | grep -E 'frontend-ui|chat-ui'

# View pod events
oc describe pod <pod-name> -n nilabja-haldar-dev

# Check logs
oc logs <pod-name> -n nilabja-haldar-dev
```

### Image Pull Errors

```bash
# Check image pull secrets
oc get secrets -n nilabja-haldar-dev

# Create image pull secret if needed
oc create secret docker-registry regcred \
  --docker-server=<registry> \
  --docker-username=<username> \
  --docker-password=<password> \
  -n nilabja-haldar-dev

# Link secret to service account
oc secrets link default regcred --for=pull -n nilabja-haldar-dev
```

### Route Not Accessible

```bash
# Check route
oc get route frontend-ui -n nilabja-haldar-dev

# Test route
curl -I https://shop-nilabja-haldar-dev.apps.rosa.example.com

# Check service endpoints
oc get endpoints frontend-ui -n nilabja-haldar-dev
```

### WebSocket Connection Issues (Chat-UI)

```bash
# Check supervisor agent is running
oc get pods -n nilabja-haldar-dev | grep supervisor-agent

# Test WebSocket endpoint
oc port-forward svc/supervisor-agent 8080:8080 -n nilabja-haldar-dev
# Then test: wscat -c ws://localhost:8080/ws
```

## 🔄 Updates & Rollbacks

### Rolling Update

```bash
# Update image tag
helm upgrade frontend-ui charts/ecommerce-app/frontend/ \
  --set image.tag=v1.1.0 \
  --namespace nilabja-haldar-dev

# Watch rollout
oc rollout status deployment/frontend-ui -n nilabja-haldar-dev
```

### Rollback

```bash
# View rollout history
oc rollout history deployment/frontend-ui -n nilabja-haldar-dev

# Rollback to previous version
oc rollout undo deployment/frontend-ui -n nilabja-haldar-dev

# Rollback to specific revision
oc rollout undo deployment/frontend-ui --to-revision=2 -n nilabja-haldar-dev
```

## 📝 Summary

**Deployment Architecture:**
1. ✅ Multi-stage Docker builds for optimized images
2. ✅ Helm charts for declarative deployment
3. ✅ OpenShift Routes for external access with TLS
4. ✅ Horizontal Pod Autoscaling for high availability
5. ✅ Non-root containers with security best practices
6. ✅ Health checks and readiness probes
7. ✅ Resource limits and requests
8. ✅ Pod disruption budgets for availability

**Key Files:**
- [`src/frontend/Dockerfile`](src/frontend/Dockerfile) - Frontend container image
- [`src/chat-ui/Dockerfile`](src/chat-ui/Dockerfile) - Chat-UI container image
- [`charts/ecommerce-app/frontend/values.yaml`](charts/ecommerce-app/frontend/values.yaml) - Frontend Helm config
- [`charts/ecommerce-app/chat-ui/values.yaml`](charts/ecommerce-app/chat-ui/values.yaml) - Chat-UI Helm config
- [`scripts/deploy-all.sh`](scripts/deploy-all.sh) - Automated deployment script
- [`scripts/build-and-push-images.sh`](scripts/build-and-push-images.sh) - Image build script

Both UIs are production-ready and fully configured for OpenShift deployment! 🚀