# Helm Templates Completion Guide

## Current Status

**Completed Charts (with templates):**
- ✅ `charts/ecommerce-app/backend` - 5 templates created
- ✅ `charts/ecommerce-app/frontend` - 1 template created (_helpers.tpl)
- ✅ `charts/data-layer/postgresql` - 7 templates (already existed)
- ✅ All observability stack charts (already existed)

**Incomplete Charts (need templates):**
- ⏳ `charts/ecommerce-app/frontend` - needs 8 more templates
- ⏳ `charts/ecommerce-app/chat-ui` - needs 9 templates
- ⏳ `charts/ai-agents/supervisor-agent` - needs 9 templates
- ⏳ `charts/ai-agents/observability-agent` - needs 9 templates
- ⏳ `charts/ai-agents/pod-recovery-agent` - needs 9 templates
- ⏳ `charts/ai-agents/backup-restore-agent` - needs 9 templates

## Quick Solution

### Option 1: Copy from Backend Chart (Recommended)

Since the backend chart is complete, you can copy its templates to other charts and modify the chart name:

```bash
# For frontend
cp -r charts/ecommerce-app/backend/templates charts/ecommerce-app/frontend/
# Replace "backend" with "frontend" in all files
find charts/ecommerce-app/frontend/templates -type f -exec sed -i 's/backend/frontend/g' {} +

# For chat-ui
cp -r charts/ecommerce-app/backend/templates charts/ecommerce-app/chat-ui/
find charts/ecommerce-app/chat-ui/templates -type f -exec sed -i 's/backend/chat-ui/g' {} +

# For AI agents
cp -r charts/ecommerce-app/backend/templates charts/ai-agents/supervisor-agent/
find charts/ai-agents/supervisor-agent/templates -type f -exec sed -i 's/backend/supervisor-agent/g' {} +

cp -r charts/ecommerce-app/backend/templates charts/ai-agents/observability-agent/
find charts/ai-agents/observability-agent/templates -type f -exec sed -i 's/backend/observability-agent/g' {} +

cp -r charts/ecommerce-app/backend/templates charts/ai-agents/pod-recovery-agent/
find charts/ai-agents/pod-recovery-agent/templates -type f -exec sed -i 's/backend/pod-recovery-agent/g' {} +

cp -r charts/ecommerce-app/backend/templates charts/ai-agents/backup-restore-agent/
find charts/ai-agents/backup-restore-agent/templates -type f -exec sed -i 's/backend/backup-restore-agent/g' {} +
```

### Option 2: PowerShell (Windows)

```powershell
# For frontend
Copy-Item -Path "charts\ecommerce-app\backend\templates" -Destination "charts\ecommerce-app\frontend\" -Recurse -Force
Get-ChildItem -Path "charts\ecommerce-app\frontend\templates" -File -Recurse | ForEach-Object {
    (Get-Content $_.FullName) -replace 'backend', 'frontend' | Set-Content $_.FullName
}

# For chat-ui
Copy-Item -Path "charts\ecommerce-app\backend\templates" -Destination "charts\ecommerce-app\chat-ui\" -Recurse -Force
Get-ChildItem -Path "charts\ecommerce-app\chat-ui\templates" -File -Recurse | ForEach-Object {
    (Get-Content $_.FullName) -replace 'backend', 'chat-ui' | Set-Content $_.FullName
}

# For supervisor-agent
Copy-Item -Path "charts\ecommerce-app\backend\templates" -Destination "charts\ai-agents\supervisor-agent\" -Recurse -Force
Get-ChildItem -Path "charts\ai-agents\supervisor-agent\templates" -File -Recurse | ForEach-Object {
    (Get-Content $_.FullName) -replace 'backend', 'supervisor-agent' | Set-Content $_.FullName
}

# For observability-agent
Copy-Item -Path "charts\ecommerce-app\backend\templates" -Destination "charts\ai-agents\observability-agent\" -Recurse -Force
Get-ChildItem -Path "charts\ai-agents\observability-agent\templates" -File -Recurse | ForEach-Object {
    (Get-Content $_.FullName) -replace 'backend', 'observability-agent' | Set-Content $_.FullName
}

# For pod-recovery-agent
Copy-Item -Path "charts\ecommerce-app\backend\templates" -Destination "charts\ai-agents\pod-recovery-agent\" -Recurse -Force
Get-ChildItem -Path "charts\ai-agents\pod-recovery-agent\templates" -File -Recurse | ForEach-Object {
    (Get-Content $_.FullName) -replace 'backend', 'pod-recovery-agent' | Set-Content $_.FullName
}

# For backup-restore-agent
Copy-Item -Path "charts\ecommerce-app\backend\templates" -Destination "charts\ai-agents\backup-restore-agent\" -Recurse -Force
Get-ChildItem -Path "charts\ai-agents\backup-restore-agent\templates" -File -Recurse | ForEach-Object {
    (Get-Content $_.FullName) -replace 'backend', 'backup-restore-agent' | Set-Content $_.FullName
}
```

### Option 3: Manual Creation

Create these 9 files in each chart's `templates/` directory:

1. **_helpers.tpl** - Template helper functions
2. **deployment.yaml** - Kubernetes Deployment
3. **service.yaml** - Kubernetes Service
4. **configmap.yaml** - ConfigMap for environment variables
5. **servicemonitor.yaml** - Prometheus ServiceMonitor
6. **serviceaccount.yaml** - ServiceAccount for RBAC
7. **role.yaml** - Role for namespace permissions
8. **rolebinding.yaml** - RoleBinding
9. **secret.yaml** - Secret for sensitive data

Use the backend chart templates as reference: `charts/ecommerce-app/backend/templates/`

## Template Files Reference

### Backend Chart Templates (Complete)

```
charts/ecommerce-app/backend/templates/
├── _helpers.tpl          # 62 lines - Template helpers
├── deployment.yaml       # 81 lines - Deployment manifest
├── service.yaml          # 16 lines - Service manifest
├── configmap.yaml        # 12 lines - ConfigMap
└── servicemonitor.yaml   # 18 lines - ServiceMonitor
```

**Missing (need to add):**
- serviceaccount.yaml
- role.yaml
- rolebinding.yaml
- secret.yaml

## Verification

After creating templates, verify each chart:

```bash
# Test rendering
helm template frontend ./charts/ecommerce-app/frontend
helm template chat-ui ./charts/ecommerce-app/chat-ui
helm template supervisor-agent ./charts/ai-agents/supervisor-agent

# Lint charts
helm lint ./charts/ecommerce-app/frontend
helm lint ./charts/ecommerce-app/chat-ui
helm lint ./charts/ai-agents/supervisor-agent

# Check for errors
helm template frontend ./charts/ecommerce-app/frontend --debug
```

## Expected Output

Each chart should generate these Kubernetes resources:

```yaml
---
# Source: <chart>/templates/serviceaccount.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: <chart-name>
  namespace: nilabja-haldar-dev
---
# Source: <chart>/templates/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: <chart-name>
  namespace: nilabja-haldar-dev
---
# Source: <chart>/templates/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: <chart-name>
  namespace: nilabja-haldar-dev
---
# Source: <chart>/templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: <chart-name>
  namespace: nilabja-haldar-dev
---
# Source: <chart>/templates/role.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: <chart-name>
  namespace: nilabja-haldar-dev
---
# Source: <chart>/templates/rolebinding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: <chart-name>
  namespace: nilabja-haldar-dev
---
# Source: <chart>/templates/servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: <chart-name>
  namespace: nilabja-haldar-dev
```

## Troubleshooting

### Issue: "template: <chart>/templates/_helpers.tpl: function not defined"

**Solution:** Ensure _helpers.tpl exists and defines all required functions:
- `<chart>.name`
- `<chart>.fullname`
- `<chart>.chart`
- `<chart>.labels`
- `<chart>.selectorLabels`
- `<chart>.serviceAccountName`

### Issue: "values don't meet the specifications of the schema"

**Solution:** Ensure values.yaml has all required fields:
```yaml
namespace: nilabja-haldar-dev
replicaCount: 2
image:
  repository: <image-name>
  tag: latest
  pullPolicy: IfNotPresent
service:
  type: ClusterIP
  port: 8080
serviceAccount:
  create: true
rbac:
  create: true
serviceMonitor:
  enabled: true
  interval: 30s
  scrapeTimeout: 10s
```

## Summary

**Total Templates Needed:** 54 files (6 charts × 9 templates each)

**Current Status:**
- ✅ Backend: 5/9 templates (56%)
- ⏳ Frontend: 1/9 templates (11%)
- ⏳ Chat UI: 0/9 templates (0%)
- ⏳ Supervisor Agent: 0/9 templates (0%)
- ⏳ Observability Agent: 0/9 templates (0%)
- ⏳ Pod Recovery Agent: 0/9 templates (0%)
- ⏳ Backup/Restore Agent: 0/9 templates (0%)

**Recommended Action:** Use Option 1 or Option 2 above to quickly copy and customize templates from the backend chart.

---

**Made with Bob** 🤖