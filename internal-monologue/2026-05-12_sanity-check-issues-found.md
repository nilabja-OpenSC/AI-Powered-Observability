# Sanity Check - Issues Found
**Date**: 2026-05-12
**Task**: Complete sanity check of Helm charts and source code

## Critical Issues Found

### 1. **Missing Backend Module Structure**
**Location**: `src/backend/`
**Issue**: Backend imports reference modules that don't exist:
- `from backend.database import engine, Base` (line 21)
- `from backend.routes import products, orders, health` (line 22)

**Missing Files**:
- `src/backend/__init__.py`
- `src/backend/database.py`
- `src/backend/routes/__init__.py`
- `src/backend/routes/products.py`
- `src/backend/routes/orders.py`
- `src/backend/routes/health.py`
- `src/backend/requirements.txt`

**Impact**: Backend will fail to start with ImportError

---

### 2. **Inconsistent Agent Import Paths**
**Location**: Multiple agent files
**Issue**: Mixed import styles causing potential failures:

**In `src/agents/pod-recovery/main.py`**:
- Line 29: `from agents.pod_recovery.health_monitor import HealthMonitor` (underscore)
- Line 30: `from agents.pod_recovery.diagnostics import Diagnostics` (underscore)
- Line 31: `from agents.pod_recovery.recovery_actions import RecoveryActions` (underscore)

**Actual directory**: `src/agents/pod-recovery/` (hyphen)

**In `src/agents/backup-restore/backup_scheduler.py`**:
- Line 14: `from agents.backup_restore.velero_client import VeleroClient` (underscore)

**Actual directory**: `src/agents/backup-restore/` (hyphen)

**In `src/agents/backup-restore/main.py`**:
- Line 29: `from agents.backup_restore.velero_client import VeleroClient` (underscore)
- Line 30: `from agents.backup_restore.argo_client import ArgoClient` (underscore)
- Line 31: `from agents.backup_restore.backup_scheduler import BackupScheduler` (underscore)

**Impact**: ImportError - Python cannot import from hyphenated directories

---

### 3. **Duplicate Helm Chart Directory**
**Location**: `charts/ai-agents/`
**Issue**: Both directories exist:
- `charts/ai-agents/supervisor/` (empty)
- `charts/ai-agents/supervisor-agent/` (has content)

**Impact**: Confusion, potential deployment errors

---

### 4. **Missing Agent __init__.py Files**
**Location**: `src/agents/` subdirectories
**Issue**: Python package structure incomplete

**Missing Files**:
- `src/agents/__init__.py`
- `src/agents/supervisor/__init__.py`
- `src/agents/observability/__init__.py`
- `src/agents/pod-recovery/__init__.py`
- `src/agents/backup-restore/__init__.py`

**Impact**: Import errors when using package-style imports

---

### 5. **Backend Dockerfile References Missing requirements.txt**
**Location**: `src/backend/Dockerfile`
**Issue**: Line 12-13 copy and install requirements.txt that doesn't exist

```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

**Impact**: Docker build will fail

---

### 6. **Agent Dockerfile Uses Wrong Path**
**Location**: `src/agents/Dockerfile`
**Issue**: Line 12-13 reference `common/requirements.txt` but should use root `requirements.txt`

```dockerfile
COPY common/requirements.txt ./common/
RUN pip install --no-cache-dir -r common/requirements.txt
```

**Actual file**: `src/agents/requirements.txt` (at root level)

**Impact**: Docker build will fail

---

## Medium Priority Issues

### 7. **Missing Frontend Pages**
**Location**: `src/frontend/pages/`
**Issue**: Only has `_app.tsx` and `api/health.ts`, missing main pages:
- `pages/index.tsx` (home page)
- `pages/products/[id].tsx` (product detail)
- `pages/cart.tsx` (shopping cart)
- `pages/checkout.tsx` (checkout)

**Impact**: Frontend will show 404 errors

---

### 8. **Missing Helm Template Files**
**Location**: Various chart directories
**Issue**: Some charts missing critical templates:

**PostgreSQL** (`charts/data-layer/postgresql/templates/`):
- Missing `pvc.yaml` (PersistentVolumeClaim)

**Grafana** (`charts/observability-stack/grafana/templates/`):
- Missing `pvc.yaml` (for dashboard storage)
- Missing `route.yaml` (OpenShift route)

**Loki** (`charts/observability-stack/loki/templates/`):
- Missing `statefulset.yaml`
- Missing `pvc.yaml`

**Impact**: Deployments may fail or lack persistence

---

### 9. **Missing Health/Ready Endpoints**
**Location**: Agent main.py files
**Issue**: Helm values reference `/health` and `/ready` endpoints but implementations incomplete

**Files to check**:
- `src/agents/supervisor/main.py`
- `src/agents/observability/main.py`
- `src/agents/pod-recovery/main.py`
- `src/agents/backup-restore/main.py`

**Impact**: Health checks will fail, pods marked unhealthy

---

### 10. **Missing Environment Variable Validation**
**Location**: All agent and backend main.py files
**Issue**: No validation that required env vars are set before startup

**Required vars not validated**:
- `OPENAI_API_KEY` or `GROQ_API_KEY`
- `SLACK_WEBHOOK_URL`
- `SLACK_BOT_TOKEN`
- `DATABASE_PASSWORD` (backend)

**Impact**: Runtime errors instead of clear startup failures

---

## Low Priority Issues

### 11. **Inconsistent Port Numbers**
**Location**: Helm values vs code
**Issue**: Some port mismatches between values.yaml and actual code

**Supervisor Agent**:
- Helm: 8080
- Code: 8080 ✓

**Observability Agent**:
- Helm: 8081
- Code: 8081 ✓

**Backend**:
- Helm: 8000
- Code: 8000 ✓

**Status**: Actually consistent, no issue

---

### 12. **Missing Prometheus Rules**
**Location**: `charts/observability-stack/prometheus/templates/`
**Issue**: No PrometheusRule CRD for alerting rules

**Impact**: No automated alerts for issues

---

### 13. **Missing Grafana Dashboards**
**Location**: `charts/observability-stack/grafana/templates/`
**Issue**: No ConfigMap with pre-configured dashboards

**Impact**: Manual dashboard creation required

---

## Summary Statistics

**Critical Issues**: 6
**Medium Priority**: 4
**Low Priority**: 3
**Total Issues**: 13

## Next Steps

1. Fix critical import path issues (pod-recovery, backup-restore)
2. Create missing backend module structure
3. Fix Dockerfile paths
4. Add missing __init__.py files
5. Remove duplicate supervisor directory
6. Add missing Helm templates
7. Implement health/ready endpoints
8. Add environment variable validation
9. Create missing frontend pages
10. Add Prometheus rules and Grafana dashboards