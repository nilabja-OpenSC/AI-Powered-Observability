# Container Image Build and Registry Guide

This guide explains how to build container images for all custom components and push them to a container registry (Docker Hub, Quay.io, or OpenShift internal registry).

## Prerequisites

### 1. Install Required Tools
```bash
# Docker (for building images)
docker --version

# Podman (alternative to Docker, preferred for OpenShift)
podman --version

# Buildah (alternative image builder)
buildah --version
```

### 2. Container Registry Options

**Option A: Docker Hub**
```bash
# Login to Docker Hub
docker login
# Enter username and password
```

**Option B: Quay.io**
```bash
# Login to Quay.io
docker login quay.io
# Enter username and password
```

**Option C: OpenShift Internal Registry**
```bash
# Expose OpenShift registry
oc patch configs.imageregistry.operator.openshift.io/cluster --patch '{"spec":{"defaultRoute":true}}' --type=merge

# Get registry URL
REGISTRY=$(oc get route default-route -n openshift-image-registry -o jsonpath='{.spec.host}')
echo $REGISTRY

# Login to OpenShift registry
docker login -u $(oc whoami) -p $(oc whoami -t) $REGISTRY
```

---

## Component Images to Build

The following custom components need container images:

1. **Backend** (FastAPI Python application)
2. **Frontend** (Next.js React application)
3. **Chat-UI** (React application)
4. **Supervisor Agent** (Python AI agent)
5. **Observability Agent** (Python AI agent)
6. **Pod Recovery Agent** (Python AI agent)
7. **Backup/Restore Agent** (Python AI agent)

**Note:** Observability stack components (Prometheus, Grafana, Loki, etc.) use official images and don't need to be built.

---

## Dockerfiles Created

All Dockerfiles have been created in their respective directories:
- `src/backend/Dockerfile` - Backend API service
- `src/frontend/Dockerfile` - Frontend Next.js application
- `src/chat-ui/Dockerfile` - Chat UI React application
- `src/agents/Dockerfile` - Base Dockerfile for all AI agents

---

## Building Images

### Set Registry Variables
```bash
# Choose your registry
REGISTRY="docker.io"              # For Docker Hub
# REGISTRY="quay.io"              # For Quay.io
# REGISTRY="<openshift-registry>" # For OpenShift internal registry

# Set your username/organization
USERNAME="your-username"

# Set image tag (version)
TAG="v1.0.0"
```

### 1. Build Backend Image
```bash
cd src/backend

# Build image
docker build -t ${REGISTRY}/${USERNAME}/observability-backend:${TAG} .

# Also tag as latest
docker tag ${REGISTRY}/${USERNAME}/observability-backend:${TAG} \
           ${REGISTRY}/${USERNAME}/observability-backend:latest

# Push to registry
docker push ${REGISTRY}/${USERNAME}/observability-backend:${TAG}
docker push ${REGISTRY}/${USERNAME}/observability-backend:latest
```

### 2. Build Frontend Image
```bash
cd src/frontend

# Build image
docker build -t ${REGISTRY}/${USERNAME}/observability-frontend:${TAG} .

# Tag as latest
docker tag ${REGISTRY}/${USERNAME}/observability-frontend:${TAG} \
           ${REGISTRY}/${USERNAME}/observability-frontend:latest

# Push to registry
docker push ${REGISTRY}/${USERNAME}/observability-frontend:${TAG}
docker push ${REGISTRY}/${USERNAME}/observability-frontend:latest
```

### 3. Build Chat-UI Image
```bash
cd src/chat-ui

# Build image
docker build -t ${REGISTRY}/${USERNAME}/observability-chat-ui:${TAG} .

# Tag as latest
docker tag ${REGISTRY}/${USERNAME}/observability-chat-ui:${TAG} \
           ${REGISTRY}/${USERNAME}/observability-chat-ui:latest

# Push to registry
docker push ${REGISTRY}/${USERNAME}/observability-chat-ui:${TAG}
docker push ${REGISTRY}/${USERNAME}/observability-chat-ui:latest
```

### 4. Build AI Agent Images

All agents use the same base Dockerfile but with different source code:

**Supervisor Agent:**
```bash
cd src/agents/supervisor

# Build image
docker build -f ../Dockerfile -t ${REGISTRY}/${USERNAME}/supervisor-agent:${TAG} .

# Tag as latest
docker tag ${REGISTRY}/${USERNAME}/supervisor-agent:${TAG} \
           ${REGISTRY}/${USERNAME}/supervisor-agent:latest

# Push to registry
docker push ${REGISTRY}/${USERNAME}/supervisor-agent:${TAG}
docker push ${REGISTRY}/${USERNAME}/supervisor-agent:latest
```

**Observability Agent:**
```bash
cd src/agents/observability

# Build image
docker build -f ../Dockerfile -t ${REGISTRY}/${USERNAME}/observability-agent:${TAG} .

# Tag as latest
docker tag ${REGISTRY}/${USERNAME}/observability-agent:${TAG} \
           ${REGISTRY}/${USERNAME}/observability-agent:latest

# Push to registry
docker push ${REGISTRY}/${USERNAME}/observability-agent:${TAG}
docker push ${REGISTRY}/${USERNAME}/observability-agent:latest
```

**Pod Recovery Agent:**
```bash
cd src/agents/pod-recovery

# Build image
docker build -f ../Dockerfile -t ${REGISTRY}/${USERNAME}/pod-recovery-agent:${TAG} .

# Tag as latest
docker tag ${REGISTRY}/${USERNAME}/pod-recovery-agent:${TAG} \
           ${REGISTRY}/${USERNAME}/pod-recovery-agent:latest

# Push to registry
docker push ${REGISTRY}/${USERNAME}/pod-recovery-agent:${TAG}
docker push ${REGISTRY}/${USERNAME}/pod-recovery-agent:latest
```

**Backup/Restore Agent:**
```bash
cd src/agents/backup-restore

# Build image
docker build -f ../Dockerfile -t ${REGISTRY}/${USERNAME}/backup-restore-agent:${TAG} .

# Tag as latest
docker tag ${REGISTRY}/${USERNAME}/backup-restore-agent:${TAG} \
           ${REGISTRY}/${USERNAME}/backup-restore-agent:latest

# Push to registry
docker push ${REGISTRY}/${USERNAME}/backup-restore-agent:${TAG}
docker push ${REGISTRY}/${USERNAME}/backup-restore-agent:latest
```

---

## Automated Build Script

Create a script to build and push all images:

```bash
#!/bin/bash
# File: scripts/build-and-push-images.sh

set -e

# Configuration
REGISTRY="${REGISTRY:-docker.io}"
USERNAME="${USERNAME:-your-username}"
TAG="${TAG:-v1.0.0}"

echo "Building and pushing images to ${REGISTRY}/${USERNAME}"
echo "Tag: ${TAG}"

# Build Backend
echo "Building backend..."
cd src/backend
docker build -t ${REGISTRY}/${USERNAME}/observability-backend:${TAG} .
docker tag ${REGISTRY}/${USERNAME}/observability-backend:${TAG} ${REGISTRY}/${USERNAME}/observability-backend:latest
docker push ${REGISTRY}/${USERNAME}/observability-backend:${TAG}
docker push ${REGISTRY}/${USERNAME}/observability-backend:latest
cd ../..

# Build Frontend
echo "Building frontend..."
cd src/frontend
docker build -t ${REGISTRY}/${USERNAME}/observability-frontend:${TAG} .
docker tag ${REGISTRY}/${USERNAME}/observability-frontend:${TAG} ${REGISTRY}/${USERNAME}/observability-frontend:latest
docker push ${REGISTRY}/${USERNAME}/observability-frontend:${TAG}
docker push ${REGISTRY}/${USERNAME}/observability-frontend:latest
cd ../..

# Build Chat-UI
echo "Building chat-ui..."
cd src/chat-ui
docker build -t ${REGISTRY}/${USERNAME}/observability-chat-ui:${TAG} .
docker tag ${REGISTRY}/${USERNAME}/observability-chat-ui:${TAG} ${REGISTRY}/${USERNAME}/observability-chat-ui:latest
docker push ${REGISTRY}/${USERNAME}/observability-chat-ui:${TAG}
docker push ${REGISTRY}/${USERNAME}/observability-chat-ui:latest
cd ../..

# Build Supervisor Agent
echo "Building supervisor-agent..."
cd src/agents/supervisor
docker build -f ../Dockerfile -t ${REGISTRY}/${USERNAME}/supervisor-agent:${TAG} .
docker tag ${REGISTRY}/${USERNAME}/supervisor-agent:${TAG} ${REGISTRY}/${USERNAME}/supervisor-agent:latest
docker push ${REGISTRY}/${USERNAME}/supervisor-agent:${TAG}
docker push ${REGISTRY}/${USERNAME}/supervisor-agent:latest
cd ../../..

# Build Observability Agent
echo "Building observability-agent..."
cd src/agents/observability
docker build -f ../Dockerfile -t ${REGISTRY}/${USERNAME}/observability-agent:${TAG} .
docker tag ${REGISTRY}/${USERNAME}/observability-agent:${TAG} ${REGISTRY}/${USERNAME}/observability-agent:latest
docker push ${REGISTRY}/${USERNAME}/observability-agent:${TAG}
docker push ${REGISTRY}/${USERNAME}/observability-agent:latest
cd ../../..

# Build Pod Recovery Agent
echo "Building pod-recovery-agent..."
cd src/agents/pod-recovery
docker build -f ../Dockerfile -t ${REGISTRY}/${USERNAME}/pod-recovery-agent:${TAG} .
docker tag ${REGISTRY}/${USERNAME}/pod-recovery-agent:${TAG} ${REGISTRY}/${USERNAME}/pod-recovery-agent:latest
docker push ${REGISTRY}/${USERNAME}/pod-recovery-agent:${TAG}
docker push ${REGISTRY}/${USERNAME}/pod-recovery-agent:latest
cd ../../..

# Build Backup/Restore Agent
echo "Building backup-restore-agent..."
cd src/agents/backup-restore
docker build -f ../Dockerfile -t ${REGISTRY}/${USERNAME}/backup-restore-agent:${TAG} .
docker tag ${REGISTRY}/${USERNAME}/backup-restore-agent:${TAG} ${REGISTRY}/${USERNAME}/backup-restore-agent:latest
docker push ${REGISTRY}/${USERNAME}/backup-restore-agent:${TAG}
docker push ${REGISTRY}/${USERNAME}/backup-restore-agent:latest
cd ../../..

echo "All images built and pushed successfully!"
```

**Usage:**
```bash
chmod +x scripts/build-and-push-images.sh

# Set environment variables
export REGISTRY="docker.io"
export USERNAME="your-username"
export TAG="v1.0.0"

# Run script
./scripts/build-and-push-images.sh
```

---

## Update Helm Charts with Image References

After pushing images, update the Helm chart values files:

### Backend Chart
```bash
# Edit charts/ecommerce-app/backend/values.yaml
image:
  repository: docker.io/your-username/observability-backend
  tag: v1.0.0
  pullPolicy: IfNotPresent
```

### Frontend Chart
```bash
# Edit charts/ecommerce-app/frontend/values.yaml
image:
  repository: docker.io/your-username/observability-frontend
  tag: v1.0.0
  pullPolicy: IfNotPresent
```

### Chat-UI Chart
```bash
# Edit charts/ecommerce-app/chat-ui/values.yaml
image:
  repository: docker.io/your-username/observability-chat-ui
  tag: v1.0.0
  pullPolicy: IfNotPresent
```

### AI Agent Charts
```bash
# Edit charts/ai-agents/supervisor-agent/values.yaml
image:
  repository: docker.io/your-username/supervisor-agent
  tag: v1.0.0
  pullPolicy: IfNotPresent

# Edit charts/ai-agents/observability-agent/values.yaml
image:
  repository: docker.io/your-username/observability-agent
  tag: v1.0.0
  pullPolicy: IfNotPresent

# Edit charts/ai-agents/pod-recovery-agent/values.yaml
image:
  repository: docker.io/your-username/pod-recovery-agent
  tag: v1.0.0
  pullPolicy: IfNotPresent

# Edit charts/ai-agents/backup-restore-agent/values.yaml
image:
  repository: docker.io/your-username/backup-restore-agent
  tag: v1.0.0
  pullPolicy: IfNotPresent
```

---

## Using Podman Instead of Docker

If using Podman (recommended for OpenShift):

```bash
# Replace 'docker' with 'podman' in all commands
podman build -t ${REGISTRY}/${USERNAME}/observability-backend:${TAG} .
podman push ${REGISTRY}/${USERNAME}/observability-backend:${TAG}

# Or create an alias
alias docker=podman
```

---

## Multi-Architecture Builds

To build images for multiple architectures (amd64, arm64):

```bash
# Enable buildx
docker buildx create --use

# Build and push multi-arch image
docker buildx build --platform linux/amd64,linux/arm64 \
  -t ${REGISTRY}/${USERNAME}/observability-backend:${TAG} \
  --push .
```

---

## Image Security Scanning

### Using Trivy
```bash
# Install Trivy
# https://github.com/aquasecurity/trivy

# Scan image for vulnerabilities
trivy image ${REGISTRY}/${USERNAME}/observability-backend:${TAG}

# Scan with severity filter
trivy image --severity HIGH,CRITICAL ${REGISTRY}/${USERNAME}/observability-backend:${TAG}
```

### Using Snyk
```bash
# Install Snyk CLI
npm install -g snyk

# Authenticate
snyk auth

# Scan image
snyk container test ${REGISTRY}/${USERNAME}/observability-backend:${TAG}
```

---

## Troubleshooting

### Build Fails
```bash
# Check Dockerfile syntax
docker build --no-cache -t test-image .

# View build logs
docker build -t test-image . 2>&1 | tee build.log
```

### Push Fails
```bash
# Verify login
docker login ${REGISTRY}

# Check image exists locally
docker images | grep observability

# Retry push
docker push ${REGISTRY}/${USERNAME}/observability-backend:${TAG}
```

### Image Pull Fails in Kubernetes
```bash
# Create image pull secret
kubectl create secret docker-registry regcred \
  --docker-server=${REGISTRY} \
  --docker-username=${USERNAME} \
  --docker-password=${PASSWORD} \
  -n nilabja-haldar-dev

# Add to Helm values
imagePullSecrets:
  - name: regcred
```

---

## Best Practices

1. **Use Multi-Stage Builds** - Reduces final image size
2. **Tag Images Properly** - Use semantic versioning (v1.0.0)
3. **Scan for Vulnerabilities** - Use Trivy or Snyk before deployment
4. **Use .dockerignore** - Exclude unnecessary files from build context
5. **Run as Non-Root** - All Dockerfiles use non-root users
6. **Health Checks** - All images include HEALTHCHECK instructions
7. **Layer Caching** - Order Dockerfile commands for optimal caching

---

## Next Steps

1. Build all images using the automated script
2. Push images to your container registry
3. Update Helm chart values with image references
4. Deploy using the deployment guide

### 1. Backend Dockerfile

<write_to_file>
<path>src/backend/Dockerfile</path>
<content>
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]