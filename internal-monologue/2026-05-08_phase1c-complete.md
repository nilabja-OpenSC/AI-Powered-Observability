# Phase 1C Complete - Thanos + Alertmanager

**Date:** 2026-05-08  
**Status:** Complete ✅

## Completed Files (4 files)

### Thanos (2 files) ✅
1. ✅ `charts/observability-stack/thanos/Chart.yaml`
2. ✅ `charts/observability-stack/thanos/values.yaml`

**Features:**
- **Thanos Query:** Unified query interface (2 replicas for HA)
  - Query timeout: 5m
  - Max concurrent queries: 20
  - Auto downsampling enabled
  - Connects to Prometheus sidecars

- **Thanos Store Gateway:** Historical metrics access
  - Filesystem object storage (demo-friendly)
  - Index cache: 250MB in-memory
  - PVC: 10GB (EFS CSI)

- **Thanos Compactor:** Data optimization
  - Raw retention: 10 days
  - 5m downsampled: 30 days
  - 1h downsampled: 90 days
  - PVC: 20GB (EFS CSI)

- **Thanos Ruler:** Disabled (using Prometheus for alerting)

### Alertmanager (2 files) ✅
1. ✅ `charts/observability-stack/alertmanager/Chart.yaml`
2. ✅ `charts/observability-stack/alertmanager/values.yaml`

**Features:**
- **High Availability:** 2 replicas with cluster gossip
- **Persistent Storage:** 5GB PVC for alert state
- **Slack Integration:** Multiple channels for different alert types
  - `#observability-alerts` - General alerts
  - `#observability-critical` - Critical alerts (immediate)
  - `#observability-pods` - Pod health alerts
  - `#observability-database` - Database alerts
  - `#observability-apps` - Application alerts

- **Alert Routing:**
  - Group by: alertname, namespace, severity
  - Group wait: 30s (10s for critical)
  - Repeat interval: 4h (1h for critical)
  - Severity-based routing (critical, high, medium, low)

- **Inhibition Rules:**
  - Suppress warnings when critical alerts fire
  - Suppress pod alerts when node is down

- **Slack Notification Templates:**
  - Rich formatting with alert details
  - Affected resources list
  - Resolution steps
  - Color-coded by severity
  - Resolved notifications

## Cumulative Progress

### Phase 1A + 1B + 1C Total: 20 files ✅
- PostgreSQL: 8 files
- Prometheus: 2 files
- Grafana: 2 files
- Loki: 2 files
- Promtail: 2 files
- Thanos: 2 files
- Alertmanager: 2 files

### Project Status
- **Total files to generate:** ~165
- **Completed:** 20 files (12%)
- **Phase 1 (Observability Stack) Progress:** 20/~40 files (50%)

## Key Achievements

### Complete Long-Term Storage Stack ✅
```
Prometheus → Thanos Sidecar → Thanos Store → Object Storage
                    ↓
              Thanos Query ← Grafana
                    ↓
            Thanos Compactor (downsampling)
```
- 10-day raw retention in Prometheus
- 30-day 5m downsampled in Thanos
- 90-day 1h downsampled in Thanos
- Automatic compaction and downsampling

### Complete Alerting Stack ✅
```
Prometheus Alerts → Alertmanager → Slack Channels
                         ↓
                   Routing Rules
                         ↓
                  Inhibition Rules
```
- Severity-based routing
- Multiple Slack channels
- Rich notification templates
- Alert grouping and deduplication
- High availability (2 replicas)

### Slack Integration Ready ✅
- 5 dedicated Slack channels
- Alert templates with:
  - Severity indicators
  - Affected resources
  - Resolution steps
  - Color-coded messages
  - Resolved notifications
- Ready for human-in-the-loop approval workflow

## Observability Standards Met

1. **Long-Term Metrics** ✅
   - 10-day raw retention
   - 30-day 5m downsampled
   - 90-day 1h downsampled
   - Historical trend analysis

2. **Alert Management** ✅
   - Severity-based routing
   - Alert grouping
   - Inhibition rules
   - Multiple notification channels

3. **High Availability** ✅
   - Thanos Query: 2 replicas
   - Alertmanager: 2 replicas with gossip
   - Anti-affinity rules

4. **Namespace Isolation** ✅
   - All resources in nilabja-haldar-dev
   - No cluster-wide RBAC
   - Namespace-scoped ServiceMonitors

## Technical Decisions

1. **Thanos Storage:** Filesystem backend (simple, demo-friendly)
2. **Thanos Query:** 2 replicas for HA and load distribution
3. **Alertmanager:** 2 replicas with gossip protocol for HA
4. **Slack Channels:** Separate channels by alert type for better organization
5. **Alert Routing:** Severity-based with different repeat intervals
6. **Downsampling:** Automatic via Thanos Compactor

## Integration Points

### With Prometheus
- Thanos Sidecar connects to Prometheus
- Prometheus sends alerts to Alertmanager
- ServiceMonitors scrape Thanos and Alertmanager metrics

### With Grafana
- Thanos Query as data source
- Historical metrics visualization
- Alert visualization

### With Slack
- Alertmanager sends notifications
- Multiple channels for different alert types
- Rich message formatting
- Ready for interactive buttons (Phase 3)

## Next Phase Options

### Phase 1D: Velero + Argo Workflows (Recommended)
- Velero for backup/restore
- Argo Workflows for database operations
- Backup schedules
- Restore workflows
- Integration with Backup/Restore Agent

### Phase 2: E-commerce Application
- Backend (FastAPI)
- Frontend (Next.js)
- Chat UI (Next.js)
- Database seed data
- Observability instrumentation

### Phase 3: AI Agents
- Supervisor Agent
- Observability Agent
- Pod Recovery Agent
- Backup/Restore Agent
- Slack integration with approval workflow

## Validation Checklist

Before moving to next phase, ensure:
- [x] All Helm charts have Chart.yaml
- [x] All values.yaml files are complete
- [x] Namespace is hardcoded to nilabja-haldar-dev
- [x] No cluster-wide RBAC
- [x] PVCs use EFS CSI storage class
- [x] ServiceMonitors are configured
- [x] Security contexts are set
- [x] High availability configured
- [x] Slack integration configured

## Slack Webhook Setup Required

Before deployment, create secret:
```bash
oc create secret generic alertmanager-slack-webhook \
  --from-literal=webhook-url='https://hooks.slack.com/services/YOUR/WEBHOOK/URL' \
  -n nilabja-haldar-dev
```

## Testing Recommendations

1. **Thanos Query:**
   - Verify connection to Prometheus sidecar
   - Test historical queries
   - Verify downsampling

2. **Alertmanager:**
   - Test alert routing
   - Verify Slack notifications
   - Test inhibition rules
   - Verify HA failover

3. **Integration:**
   - Prometheus → Alertmanager
   - Thanos Query → Grafana
   - Alertmanager → Slack

---

**Status:** Phase 1C Complete ✅  
**Next:** Await user decision on next phase (1D: Velero + Argo or Phase 2: E-commerce App)