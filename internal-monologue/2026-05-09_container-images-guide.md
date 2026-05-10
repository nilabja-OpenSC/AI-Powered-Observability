# Container Images Guide Creation - 2026-05-09

## Context
User requested guidance on how to create container images and upload them to a container registry for all custom components.

## Actions Taken

### 1. Created Dockerfiles (4 files)

**Backend Dockerfile** (`src/backend/Dockerfile` - 30 lines)
- Base: Python 3.11-slim
- Installs system dependencies (gcc, postgresql-client)
- Copies requirements.txt and installs Python packages
- Runs as non-root user (appuser, UID 1000)
- Exposes port 8000
- Health check via HTTP endpoint
- CMD: uvicorn main:app

**Frontend Dockerfile** (`src/frontend/Dockerfile` - 42 lines)
- Multi-stage build (builder + production)
- Base: Node 18-alpine
- Builder stage: npm ci, npm run build
- Production stage: Copies built .next assets
- Runs as non-root user (appuser, UID 1000)
- Exposes port 3000
- Health check via HTTP endpoint
- CMD: npm start

**Chat-UI Dockerfile** (`src/chat-ui/Dockerfile` - 42 lines)
- Multi-stage build (builder + production)
- Base: Node 18-alpine
- Builder stage: npm ci, npm run build
- Production stage: Uses 'serve' for static files
- Runs as non-root user (appuser, UID 1000)
- Exposes port 3000
- Health check via wget
- CMD: serve -s build -l 3000

**AI Agents Dockerfile** (`src/agents/Dockerfile` - 32 lines)
- Base: Python 3.11-slim
- Shared Dockerfile for all 4 agents
- Installs system dependencies (gcc, curl)
- Copies common utilities and requirements
- Runs as non-root user (appuser, UID 1000)
- Exposes port 8080
- Health check via curl
- CMD: uvicorn main:app (overridable)

### 2. Created Container Image Guide (docs/container-image-guide.md - 450+ lines)

**Contents:**
- Prerequisites (Docker, Podman, Buildah)
- Registry options (Docker Hub, Quay.io, OpenShift internal)
- Component list (7 custom images needed)
- Dockerfile locations
- Build instructions for each component
- Automated build script documentation
- Helm chart update instructions
- Podman usage
- Multi-architecture builds
- Security scanning (Trivy, Snyk)
- Troubleshooting guide
- Best practices

**Registry Options Covered:**
1. **Docker Hub** - Public/private registry
2. **Quay.io** - Red Hat's container registry
3. **OpenShift Internal Registry** - Cluster-local registry

**Build Process:**
1. Set registry variables (REGISTRY, USERNAME, TAG)
2. Build each image with docker/podman
3. Tag as both versioned (v1.0.0) and latest
4. Push to registry
5. Update Helm chart values.yaml files

### 3. Created Automated Build Script (scripts/build-and-push-images.sh - 219 lines)

**Features:**
- Color-coded output (info, success, warning, error)
- Configurable via environment variables
- Supports both Docker and Podman
- Builds all 7 custom images
- Tags as both versioned and latest
- Pushes to registry
- Tracks successful/failed builds
- Displays summary and next steps
- Interactive confirmation before build

**Usage:**
```bash
chmod +x scripts/build-and-push-images.sh

export REGISTRY="docker.io"
export USERNAME="your-username"
export TAG="v1.0.0"
export BUILD_TOOL="docker"  # or "podman"

./scripts/build-and-push-images.sh
```

**Images Built:**
1. observability-backend
2. observability-frontend
3. observability-chat-ui
4. supervisor-agent
5. observability-agent
6. pod-recovery-agent
7. backup-restore-agent

## Technical Details

### Dockerfile Best Practices Applied
1. **Multi-stage builds** - Reduces final image size (Frontend, Chat-UI)
2. **Non-root users** - All images run as UID 1000
3. **Health checks** - All images include HEALTHCHECK
4. **Layer caching** - Optimized order (dependencies before code)
5. **Minimal base images** - Using slim/alpine variants
6. **Security** - No secrets in images, minimal attack surface

### Image Naming Convention
```
${REGISTRY}/${USERNAME}/${IMAGE_NAME}:${TAG}

Examples:
- docker.io/myuser/observability-backend:v1.0.0
- quay.io/myorg/supervisor-agent:v1.0.0
- default-route-openshift-image-registry.apps.cluster/myproject/observability-frontend:v1.0.0
```

### Build Context Considerations
- Backend: `src/backend/` (includes requirements.txt, main.py, etc.)
- Frontend: `src/frontend/` (includes package.json, next.config.js, etc.)
- Chat-UI: `src/chat-ui/` (includes package.json, src/, public/)
- Agents: Context is agent-specific dir, Dockerfile is in parent (`src/agents/Dockerfile`)

### Agent Build Pattern
All agents share the same Dockerfile but build from different contexts:
```bash
cd src/agents/supervisor
docker build -f ../Dockerfile -t supervisor-agent:v1.0.0 .
```

This allows:
- Shared base configuration
- Common utilities from `src/agents/common/`
- Agent-specific code in each subdirectory

## Integration with Deployment

### Helm Chart Updates Required
After building and pushing images, update these files:

1. `charts/ecommerce-app/backend/values.yaml`
2. `charts/ecommerce-app/frontend/values.yaml`
3. `charts/ecommerce-app/chat-ui/values.yaml`
4. `charts/ai-agents/supervisor-agent/values.yaml`
5. `charts/ai-agents/observability-agent/values.yaml`
6. `charts/ai-agents/pod-recovery-agent/values.yaml`
7. `charts/ai-agents/backup-restore-agent/values.yaml`

**Update pattern:**
```yaml
image:
  repository: docker.io/your-username/image-name
  tag: v1.0.0
  pullPolicy: IfNotPresent
```

### Image Pull Secrets (if using private registry)
```bash
kubectl create secret docker-registry regcred \
  --docker-server=${REGISTRY} \
  --docker-username=${USERNAME} \
  --docker-password=${PASSWORD} \
  -n nilabja-haldar-dev

# Add to Helm values
imagePullSecrets:
  - name: regcred
```

## Security Considerations

### Vulnerability Scanning
Guide includes instructions for:
- **Trivy** - Open-source vulnerability scanner
- **Snyk** - Commercial security platform

### Image Hardening
- All images run as non-root
- Minimal base images (slim/alpine)
- No unnecessary packages
- Health checks for monitoring
- Proper signal handling

### Registry Security
- Use HTTPS for registry communication
- Store credentials securely (not in code)
- Use image pull secrets for private registries
- Enable registry scanning if available

## Files Created
1. `src/backend/Dockerfile` (30 lines)
2. `src/frontend/Dockerfile` (42 lines)
3. `src/chat-ui/Dockerfile` (42 lines)
4. `src/agents/Dockerfile` (32 lines)
5. `docs/container-image-guide.md` (450+ lines)
6. `scripts/build-and-push-images.sh` (219 lines)

**Total:** 6 new files, 815+ lines of code/documentation

## Workflow Summary

**Complete Build and Deploy Workflow:**
1. Write application code
2. Create Dockerfiles ✅
3. Build container images ✅ (script provided)
4. Push to registry ✅ (script provided)
5. Update Helm chart values ✅ (documented)
6. Deploy to OpenShift ✅ (deployment guide exists)

## Next Steps for User
1. Choose container registry (Docker Hub, Quay.io, or OpenShift)
2. Login to registry
3. Run build script: `./scripts/build-and-push-images.sh`
4. Update Helm chart values with image references
5. Deploy using: `./scripts/deploy-all.sh`

## Status
✅ Dockerfiles created for all components
✅ Container image guide complete
✅ Automated build script complete
✅ Ready for image building and registry push