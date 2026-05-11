# Phase 1: Requirements Analysis & Architecture Design - Detailed Summary

**Date:** May 7, 2026  
**Phase:** Requirements & Architecture  
**Status:** ✅ COMPLETE  

---

## Overview

Phase 1 established the foundation for the AI-Powered Observability Platform by conducting comprehensive requirements analysis and designing a robust 5-layer architecture. This phase involved stakeholder identification, goal definition, and critical architectural decisions.

---

## 1. Requirements Analysis

### 1.1 Functional Requirements (5 total)

**FR-001: Real-time Anomaly Detection**
- **Description:** AI agents must detect anomalies in metrics and logs in real-time
- **Priority:** Critical
- **Acceptance Criteria:** Detection within 30 seconds of anomaly occurrence
- **Rationale:** Early detection enables faster incident response
- **Implementation:** Prometheus/Loki queries with ML-based anomaly detection

**FR-002: Human-in-the-Loop Approval**
- **Description:** All corrective actions require human approval via Slack
- **Priority:** Critical
- **Acceptance Criteria:** Approval request sent to Slack with approve/deny buttons
- **Rationale:** Safety mechanism to prevent automated mistakes
- **Implementation:** Slack Block Kit with interactive buttons, 5-min timeout

**FR-003: Automated Incident Documentation**
- **Description:** System must automatically document incidents in Confluence
- **Priority:** High
- **Acceptance Criteria:** Confluence page created within 1 minute of resolution
- **Rationale:** Knowledge base for future incidents
- **Implementation:** Confluence REST API integration

**FR-004: Multi-Channel Communication**
- **Description:** Support both Slack (approvals) and Chat UI (queries)
- **Priority:** High
- **Acceptance Criteria:** Separate interfaces for different use cases
- **Rationale:** Slack for critical actions, Chat UI for exploration
- **Implementation:** FastAPI backend with dual endpoints

**FR-005: Observability Query Interface**
- **Description:** Natural language queries for Prometheus/Loki data
- **Priority:** Medium
- **Acceptance Criteria:** Query response within 5 seconds
- **Rationale:** Democratize observability data access
- **Implementation:** LLM-powered query translation to PromQL/LogQL

### 1.2 Non-Functional Requirements (1 total)

**NFR-001: Namespace Isolation**
- **Description:** All operations must be scoped to `nilabja-haldar-dev` namespace
- **Priority:** Critical
- **Acceptance Criteria:** No cluster-wide RBAC or operations outside namespace
- **Rationale:** Security constraint for multi-tenant OpenShift cluster
- **Implementation:** Namespace guard decorator on all Kubernetes operations
- **Impact:** Cannot use ClusterRoles, must use namespace-scoped Roles

### 1.3 Security Requirements (2 total)

**SEC-001: Approval Timeout Fail-Safe**
- **Description:** Approval timeout (5 min) must default to DENY
- **Priority:** Critical
- **Acceptance Criteria:** No action executed without explicit approval
- **Rationale:** Fail-safe mechanism to prevent unauthorized actions
- **Implementation:** Async timeout with default DENY state

**SEC-002: Audit Trail**
- **Description:** All actions must be logged and auditable
- **Priority:** High
- **Acceptance Criteria:** Immutable audit log in Loki
- **Rationale:** Compliance and forensic analysis
- **Implementation:** Structured logging to Loki with retention policy

### 1.4 Performance Requirements (2 total)

**PERF-001: Query Response Time**
- **Description:** Prometheus queries must return within 5 seconds
- **Priority:** High
- **Acceptance Criteria:** 95th percentile query latency < 5s
- **Rationale:** User experience for interactive queries
- **Implementation:** Query optimization, caching, Thanos for historical data

**PERF-002: Anomaly Detection Latency**
- **Description:** Anomaly detection within 30 seconds
- **Priority:** Critical
- **Acceptance Criteria:** End-to-end detection latency < 30s
- **Rationale:** Timely incident response
- **Implementation:** Streaming metrics, efficient ML models

---

## 2. Stakeholder Analysis

### 2.1 Platform Engineers
- **Role:** System Operators
- **Interest:** Automated incident resolution, reduced manual toil
- **Pain Points:** Manual pod restarts, alert fatigue, repetitive tasks
- **Requirements:** FR-001, FR-002, NFR-001, SEC-001
- **Use Cases:** UC-001 (Automated Pod Recovery), UC-002 (Log Analysis)

### 2.2 DevOps Teams
- **Role:** Application Developers
- **Interest:** Observability insights, deployment automation
- **Pain Points:** Lack of visibility, slow troubleshooting
- **Requirements:** FR-004, FR-005, PERF-001
- **Use Cases:** UC-003 (Query Metrics), UC-004 (Dashboard Creation)

### 2.3 Security Teams
- **Role:** Security & Compliance
- **Interest:** Audit trails, access control, compliance
- **Pain Points:** Lack of visibility into automated actions
- **Requirements:** SEC-001, SEC-002, NFR-001
- **Use Cases:** UC-005 (Audit Review)

---

## 3. Goals & Success Metrics

### Goal 1: Reduce Mean Time to Resolution (MTTR)
- **Target:** MTTR < 10 minutes for common issues
- **Baseline:** 45 minutes (manual resolution)
- **Measurement:** Time from detection to resolution
- **Requirements:** FR-001, FR-002, FR-003

### Goal 2: Achieve 99.9% Uptime
- **Target:** 99.9% monthly uptime for critical services
- **Baseline:** 99.5% (manual operations)
- **Measurement:** Monthly uptime percentage
- **Requirements:** FR-001, FR-002, PERF-002

### Goal 3: Reduce Alert Fatigue
- **Target:** 80% reduction in false positive alerts
- **Baseline:** 60% false positive rate
- **Measurement:** Alert accuracy percentage
- **Requirements:** FR-001, PERF-002

### Goal 4: Improve Observability Access
- **Target:** 100% of engineers can query metrics without PromQL knowledge
- **Baseline:** 20% (only experts)
- **Measurement:** User adoption rate
- **Requirements:** FR-004, FR-005

### Goal 5: Ensure Compliance
- **Target:** 100% of actions auditable
- **Baseline:** 50% (manual actions not logged)
- **Measurement:** Audit coverage percentage
- **Requirements:** SEC-002, NFR-001

### Goal 6: Namespace Security
- **Target:** Zero cluster-wide operations
- **Baseline:** N/A (new constraint)
- **Measurement:** RBAC audit
- **Requirements:** NFR-001

---

## 4. Use Cases

### UC-001: Automated Pod Recovery
- **Actor:** Platform Engineer
- **Precondition:** Pod in CrashLoopBackOff state
- **Flow:**
  1. Agent detects CrashLoopBackOff via Prometheus alert
  2. Agent analyzes logs to determine root cause
  3. Agent sends Slack notification with approve/deny buttons
  4. Engineer reviews and approves
  5. Agent restarts pod
  6. Agent verifies pod is running
  7. Agent documents incident in Confluence
- **Postcondition:** Pod running normally, incident documented
- **Requirements:** FR-001, FR-002, FR-003

### UC-002: Log Analysis for Error Investigation
- **Actor:** DevOps Engineer
- **Precondition:** Application errors reported
- **Flow:**
  1. Engineer queries Chat UI: "Show errors in backend service last hour"
  2. Agent translates to LogQL query
  3. Agent executes query against Loki
  4. Agent presents results with context
  5. Engineer drills down into specific errors
- **Postcondition:** Root cause identified
- **Requirements:** FR-004, FR-005

### UC-003: Query Metrics via Natural Language
- **Actor:** DevOps Engineer
- **Precondition:** Need to check service health
- **Flow:**
  1. Engineer asks: "What's the error rate for frontend?"
  2. Agent translates to PromQL
  3. Agent queries Prometheus
  4. Agent presents results with visualization
- **Postcondition:** Metrics retrieved and displayed
- **Requirements:** FR-005, PERF-001

### UC-004: Create Custom Dashboard
- **Actor:** Platform Engineer
- **Precondition:** Need dashboard for new service
- **Flow:**
  1. Engineer requests: "Create dashboard for payment service"
  2. Agent identifies relevant metrics
  3. Agent generates Grafana dashboard JSON
  4. Agent creates dashboard via Grafana API
  5. Agent shares dashboard link
- **Postcondition:** Dashboard created and accessible
- **Requirements:** FR-004, FR-005

---

## 5. Test Cases

### TC-001: Verify Anomaly Detection Latency
- **Requirement:** FR-001, PERF-002
- **Steps:**
  1. Inject anomaly (CPU spike to 95%)
  2. Start timer
  3. Wait for Slack notification
  4. Stop timer
- **Expected:** Notification within 30 seconds
- **Status:** Pending implementation

### TC-002: Verify Approval Timeout Fail-Safe
- **Requirement:** SEC-001
- **Steps:**
  1. Trigger corrective action
  2. Receive Slack approval request
  3. Do not respond
  4. Wait 5 minutes
  5. Verify action was NOT executed
- **Expected:** Action denied, manual steps sent
- **Status:** Pending implementation

### TC-003: Verify Namespace Isolation
- **Requirement:** NFR-001
- **Steps:**
  1. Attempt to list pods in different namespace
  2. Verify operation fails
  3. Attempt to create ClusterRole
  4. Verify operation fails
- **Expected:** All operations outside namespace fail
- **Status:** Pending implementation

### TC-004: Verify Query Response Time
- **Requirement:** PERF-001
- **Steps:**
  1. Execute 100 Prometheus queries
  2. Measure response time for each
  3. Calculate 95th percentile
- **Expected:** 95th percentile < 5 seconds
- **Status:** Pending implementation

### TC-005: Verify Audit Trail
- **Requirement:** SEC-002
- **Steps:**
  1. Execute corrective action
  2. Query Loki for audit logs
  3. Verify all steps logged
- **Expected:** Complete audit trail in Loki
- **Status:** Pending implementation

### TC-006: Verify Confluence Documentation
- **Requirement:** FR-003
- **Steps:**
  1. Complete incident resolution
  2. Wait 1 minute
  3. Check Confluence for incident page
- **Expected:** Page created with all details
- **Status:** Pending implementation

### TC-007: Verify Slack Approval Workflow
- **Requirement:** FR-002
- **Steps:**
  1. Trigger corrective action
  2. Verify Slack notification received
  3. Click "Approve" button
  4. Verify action executed
  5. Verify Confluence documentation
- **Expected:** Complete workflow successful
- **Status:** Pending implementation

### TC-008: Verify Slack Denial Workflow
- **Requirement:** FR-002
- **Steps:**
  1. Trigger corrective action
  2. Verify Slack notification received
  3. Click "Deny" button
  4. Verify action NOT executed
  5. Verify manual steps sent
- **Expected:** Action denied, manual steps provided
- **Status:** Pending implementation

### TC-009: Verify Natural Language Query
- **Requirement:** FR-005
- **Steps:**
  1. Ask: "What's the error rate for backend?"
  2. Verify PromQL generated correctly
  3. Verify results returned
  4. Verify response time < 5s
- **Expected:** Accurate query results
- **Status:** Pending implementation

### TC-010: Verify Multi-Channel Support
- **Requirement:** FR-004
- **Steps:**
  1. Send query via Chat UI
  2. Verify response received
  3. Trigger approval via Slack
  4. Verify both channels work independently
- **Expected:** Both channels functional
- **Status:** Pending implementation

---

## 6. Architectural Decisions

### AD-001: Use LangChain for AI Agent Framework
- **Decision:** Selected LangChain as the framework for building AI agents
- **Rationale:**
  - Provides tool integration out-of-the-box
  - Memory management with vector stores
  - Agent orchestration and routing
  - Active community and ecosystem
- **Alternatives Considered:**
  - Custom framework (too much development time)
  - AutoGPT (less control over agent behavior)
  - Semantic Kernel (less mature ecosystem)
- **Consequences:**
  - Dependency on LangChain ecosystem
  - Faster development time
  - Need to learn LangChain patterns
- **Influenced Requirements:** FR-001, FR-005

### AD-002: Namespace-Scoped RBAC Only
- **Decision:** Use only namespace-scoped Roles, no ClusterRoles
- **Rationale:**
  - Security requirement from OpenShift team
  - Prevents accidental cluster-wide operations
  - Aligns with multi-tenant best practices
- **Alternatives Considered:**
  - ClusterRoles with namespace filtering (rejected for security)
  - Multiple namespaces (rejected for complexity)
- **Consequences:**
  - Cannot perform cluster-wide operations
  - More secure by design
  - Need namespace guard on all operations
- **Influenced Requirements:** NFR-001, SEC-001

### AD-003: Slack for Approvals, Chat UI for Queries
- **Decision:** Separate channels for different use cases
- **Rationale:**
  - Slack for critical actions (approvals, alerts)
  - Chat UI for exploratory queries
  - Different user contexts and workflows
- **Alternatives Considered:**
  - Single interface for everything (rejected for UX)
  - Email for approvals (rejected for latency)
- **Consequences:**
  - Need to maintain two interfaces
  - Better user experience
  - Clear separation of concerns
- **Influenced Requirements:** FR-002, FR-004

### AD-004: 5-Minute Approval Timeout with DENY Default
- **Decision:** Approval requests timeout after 5 minutes, default to DENY
- **Rationale:**
  - Fail-safe mechanism
  - Prevents stale approvals
  - Forces timely decision-making
- **Alternatives Considered:**
  - No timeout (rejected for safety)
  - Longer timeout (rejected for incident response time)
  - Default to APPROVE (rejected for security)
- **Consequences:**
  - Engineers must respond within 5 minutes
  - Manual steps provided on timeout
  - More secure but requires attention
- **Influenced Requirements:** SEC-001, FR-002

### AD-005: Thanos for Long-Term Metrics Storage
- **Decision:** Use Thanos for metrics retention beyond 6 hours
- **Rationale:**
  - Prometheus limited to 6 hours (resource constraints)
  - Need historical data for trend analysis
  - Thanos provides S3-backed storage
- **Alternatives Considered:**
  - Increase Prometheus retention (rejected for cost)
  - Cortex (rejected for complexity)
  - VictoriaMetrics (rejected for ecosystem fit)
- **Consequences:**
  - Need S3/MinIO for storage
  - Query routing based on time range
  - Better long-term analysis capabilities
- **Influenced Requirements:** PERF-001, FR-005

---

## 7. Architecture Design

### 7.1 5-Layer Architecture

**Layer 1: Application Layer**
- **Components:** Backend (FastAPI), Frontend (Next.js), Chat UI (Vite)
- **Purpose:** User-facing applications
- **Technology:** Python, TypeScript, React
- **Deployment:** Kubernetes Deployments with Services

**Layer 2: AI Agents Layer**
- **Components:** Supervisor, Observability, Pod Recovery, Backup/Restore
- **Purpose:** Intelligent automation and decision-making
- **Technology:** LangChain, OpenAI/watsonx.ai, Chroma
- **Deployment:** Kubernetes Deployments with RBAC

**Layer 3: Observability Layer**
- **Components:** Prometheus, Thanos, Loki, Promtail, Grafana, Alertmanager
- **Purpose:** Metrics, logs, visualization, alerting
- **Technology:** Prometheus ecosystem
- **Deployment:** StatefulSets (Prometheus, Loki), DaemonSet (Promtail)

**Layer 4: Data Layer**
- **Components:** PostgreSQL, Chroma Vector Store
- **Purpose:** Persistent data storage
- **Technology:** PostgreSQL, Chroma
- **Deployment:** StatefulSet with PVC (EFS CSI, 10GB)

**Layer 5: Integration Layer**
- **Components:** Slack, Confluence, Kubernetes API
- **Purpose:** External integrations
- **Technology:** REST APIs, WebSockets
- **Deployment:** N/A (external services)

### 7.2 Component Relationships

```
Chat UI ──────────────┐
                      ├──> Backend ──> AI Agents ──> Observability Stack
Slack ────────────────┘                    │
                                           ├──> Kubernetes API
                                           ├──> Confluence API
                                           └──> PostgreSQL
```

### 7.3 Technology Stack

**Backend:**
- Language: Python 3.11+
- Framework: FastAPI
- Database: PostgreSQL
- Container: Docker

**Frontend:**
- Language: TypeScript
- Framework: Next.js (React)
- Styling: TailwindCSS
- Container: Docker

**Chat UI:**
- Language: TypeScript
- Framework: Vite + React
- Styling: TailwindCSS
- Container: Docker

**AI Agents:**
- Framework: LangChain
- LLM: OpenAI GPT-4 or IBM Granite
- Memory: Chroma Vector Store
- Tools: Prometheus, Loki, Kubernetes, Slack, Confluence

**Observability:**
- Metrics: Prometheus + Thanos
- Logs: Loki + Promtail
- Visualization: Grafana
- Alerting: Alertmanager

**Deployment:**
- Platform: OpenShift ROSA (Kubernetes 1.27)
- Package Manager: Helm
- Storage: EFS CSI Driver
- Networking: OpenShift Routes

---

## 8. Key Decisions & Rationale

### Why LangChain?
- Mature ecosystem for AI agents
- Built-in tool integration
- Memory management with vector stores
- Active community support

### Why Namespace Isolation?
- Security requirement from OpenShift team
- Multi-tenant cluster best practices
- Prevents accidental cluster-wide operations

### Why Human-in-the-Loop?
- Safety mechanism for automated actions
- Compliance requirement
- Builds trust in automation

### Why Slack for Approvals?
- Engineers already use Slack
- Interactive buttons for quick decisions
- Real-time notifications

### Why Separate Chat UI?
- Different use case (exploration vs. approval)
- Better user experience
- Reduces Slack noise

### Why Thanos?
- Cost-effective long-term storage
- Seamless integration with Prometheus
- S3-backed storage

---

## 9. Deliverables

✅ Requirements document (5 FR, 1 NFR, 2 SEC, 2 PERF)  
✅ Stakeholder analysis (3 groups)  
✅ Goals & metrics (6 goals)  
✅ Use cases (4 scenarios)  
✅ Test cases (10 tests)  
✅ Architectural decisions (5 decisions)  
✅ 5-layer architecture design  
✅ Technology stack selection  
✅ Component relationship diagrams  

---

## 10. Next Steps (Phase 2)

- Implement AI agents (Supervisor, Observability, Pod Recovery, Backup/Restore)
- Implement backend (FastAPI)
- Implement frontend (Next.js)
- Implement Chat UI (Vite)
- Create Helm charts for all components
- Write deployment scripts
- Create documentation

---

**Phase 1 Status:** ✅ COMPLETE  
**Date Completed:** May 7, 2026  
**Next Phase:** Phase 2 - Code Implementation