# This is the generic guidelines to be followed by you while working on the other specifications.


# You must follow the specs filed in the below order and generate the artifacts in the same order.

    1. Generic-schema
    2. tech-stack
    3. Platform-Observability-Tools-Creation-Agent-prompt
    4. ecommerce-demo-app-prompt
    5. Backup-Restore-Agent-prompt
    6. Pod-Recovery-Agent-promot
    7. Observability-Agent-prompt
    8. Supervisor-Agent


# Shared Conventions (Used by all agents)

**You can reuse these sections across agents.**

## 0.1 **Environment Constraints** (must be baked into every agent)

- **Cluster**: OpenShift ROSA
- **Namespace/project scope:** ONLY nilabja-haldar-dev
- **No cluster-wide RBAC changes** (no ClusterRole/ClusterRoleBinding, no new SCC changes, etc.)
- **Prefer Helm-based changes** (avoid oc edit/manual drift)
- **Database uses PVC**: backups/restores via Velero (PVC snapshots/backups)
- **Observability components include**: Prometheus, Alertmanager, Grafana, Thanos, Loki
- **Collaboration/IM**: Slack, documentation: Confluence (or “basic incident mgmt tool like Confluence”)

## 0.2 **Moduler approach** (recommended)

- Create separate modules
- separate folder structure for each module
- helm chart for each module
- helm chart values file for each module
- All helm charts are stored in a central folder (e.g. `charts`)
- All helm chart values files are stored in a central folder (e.g. `values`)



