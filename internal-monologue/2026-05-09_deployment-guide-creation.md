# Deployment Guide Creation - 2026-05-09

## Context
User requested detailed deployment steps with commands for all components of the AI-Powered Observability Platform.

## Actions Taken

### 1. Created Comprehensive Deployment Guide (619 lines)
**File:** `docs/deployment-guide.md`

**Contents:**
- Prerequisites and setup instructions
- 6 deployment phases with detailed commands
- Verification and testing procedures
- Monitoring and maintenance guidelines
- Troubleshooting section
- Cleanup procedures

**Deployment Order:**
1. **Data Layer** - PostgreSQL with PVC
2. **Observability Stack** - Prometheus, Loki, Promtail, Alertmanager, Thanos, Grafana
3. **Backup/Restore** - Velero, Argo Workflows
4. **E-commerce App** - Backend, Frontend, Chat-UI
5. **AI Agents** - Supervisor, Observability, Pod-Recovery, Backup-Restore

**Key Features:**
- Secret creation commands for all components
- Helm install commands with proper parameters
- Verification commands for each deployment
- Port-forwarding instructions for local access
- Route creation for external access
- Troubleshooting for common issues

### 2. Created Automated Deployment Script (545 lines)
**File:** `scripts/deploy-all.sh`

**Features:**
- Automated deployment of all 14 Helm charts
- Interactive prompts for secrets and configuration
- Color-coded output (info, success, warning, error)
- Wait functions for deployment readiness
- Automatic route creation for frontend and chat-ui
- Deployment summary with access URLs
- Error handling with exit on failure

**Usage:**
```bash
chmod +x scripts/deploy-all.sh
./scripts/deploy-all.sh
```

**Script Flow:**
1. Prerequisites check (oc, helm, login status)
2. Namespace creation
3. Secret creation (interactive prompts)
4. Sequential deployment of all components
5. Readiness checks for each component
6. Summary with access URLs

## Technical Details

### Secret Management
All secrets are created interactively:
- `postgresql-secret` - Database credentials
- `ai-agents-secret` - OpenAI API key, Slack credentials
- `alertmanager-secret` - Slack webhook for alerts
- `thanos-s3-secret` - S3 credentials for long-term storage
- `grafana-secret` - Admin credentials
- `velero-credentials` - AWS credentials for backups
- `argo-workflows-secret` - S3 credentials for artifacts

### Deployment Commands Pattern
```bash
helm upgrade --install <release-name> charts/<chart-path> \
  --namespace nilabja-haldar-dev \
  --set key=value \
  --timeout 5m \
  --wait
```

### Verification Pattern
- StatefulSets: Wait for `readyReplicas=1`
- Deployments: Wait for `condition=available`
- DaemonSets: Sleep 10s (schedules on all nodes)

### Access Methods
1. **External Routes** (Frontend, Chat-UI)
   ```bash
   oc expose svc/<service-name>
   oc get route <service-name>
   ```

2. **Port Forwarding** (Grafana, Prometheus, Argo)
   ```bash
   oc port-forward svc/<service-name> <local-port>:<service-port>
   ```

## Deployment Guide Sections

### 1. Prerequisites
- Tool verification (helm, oc, kubectl)
- Cluster access and login
- Namespace creation

### 2. Phase-by-Phase Deployment
Each phase includes:
- Helm lint command
- Dry-run command
- Install command with parameters
- Verification commands
- Access instructions

### 3. Verification & Testing
- Pod status checks
- Service and route listing
- PVC verification
- Observability stack testing
- AI agent log inspection
- E-commerce app testing

### 4. Monitoring & Maintenance
- Log viewing commands
- Scaling procedures
- Update and rollback commands

### 5. Troubleshooting
Common issues covered:
- Pod not starting
- PVC not binding
- Service not accessible
- Agent not connecting to Slack

### 6. Cleanup
Complete uninstall procedure in reverse order

## Key Commands Reference

### Deployment
```bash
# Deploy single component
helm install <name> charts/<path> -n nilabja-haldar-dev

# Deploy all components
./scripts/deploy-all.sh
```

### Verification
```bash
# Check all pods
oc get pods -n nilabja-haldar-dev

# Check specific deployment
oc get deployment <name> -n nilabja-haldar-dev

# View logs
oc logs -f deployment/<name> -n nilabja-haldar-dev
```

### Access
```bash
# Port-forward Grafana
oc port-forward svc/grafana 3000:3000 -n nilabja-haldar-dev

# Get route URL
oc get route frontend -n nilabja-haldar-dev -o jsonpath='{.spec.host}'
```

## Files Created
1. `docs/deployment-guide.md` (619 lines)
2. `scripts/deploy-all.sh` (545 lines)

## Next Steps for User
1. Review deployment guide
2. Prepare required credentials:
   - OpenAI API key
   - Slack webhook URL and tokens
   - S3 credentials for Thanos, Velero, Argo
   - Database passwords
3. Run automated deployment script OR follow manual steps
4. Verify all components are running
5. Access Grafana dashboards
6. Test AI agents via Chat-UI

## Status
✅ Deployment documentation complete
✅ Automated deployment script complete
✅ Ready for production deployment to OpenShift ROSA