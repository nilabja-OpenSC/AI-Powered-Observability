# JSON-LD Schema Collection for AI-Powered Observability Platform

## Overview

This directory contains comprehensive JSON-LD ontologies that provide semantic representation of the AI-Powered Observability Platform project. These schemas enable machine-readable knowledge graphs, semantic queries, and automated reasoning about the system.

## Completed Schemas (9/25)

### Core Schemas ✅

1. **project-requirements-ontology.jsonld**
   - Requirements (Functional, Non-Functional, Security, Performance)
   - Goals, Use Cases, Test Cases
   - Stakeholders, Architectural Decisions
   - Requirement relationships (dependencies, conflicts, verification)

2. **system-architecture-ontology.jsonld**
   - Application Components (Backend, Frontend, Chat UI, AI Agents)
   - Infrastructure Components (Kubernetes, Prometheus, Loki, Grafana)
   - Data Stores (PostgreSQL, Chroma, S3)
   - Communication Channels (REST, WebSocket, PromQL, LogQL)

3. **deployment-topology-ontology.jsonld**
   - Helm Charts for all layers
   - Kubernetes Resources (Deployments, StatefulSets, Services, ConfigMaps)
   - RBAC (ServiceAccounts, Roles, RoleBindings)
   - ServiceMonitors, Routes, PVCs

4. **observability-metrics-ontology.jsonld**
   - Metrics (Counter, Gauge, Histogram, Summary)
   - Alerts (CrashLoopBackOff, HighCPU, HighMemory)
   - Dashboards (Golden Signals, Resource Usage)
   - SLIs/SLOs, Error Budgets

5. **logging-ontology.jsonld**
   - Log Sources, Levels, Streams
   - LogQL Queries and Aggregations
   - Log Patterns (HTTP requests, errors, agent decisions)

6. **incident-management-ontology.jsonld**
   - Incident Lifecycle (Detected → Resolved → Closed)
   - Severity Levels (Critical, High, Medium, Low)
   - Resolution Steps, Postmortems
   - Root Causes, Action Items, Timelines

7. **ai-agent-ontology.jsonld**
   - Agent Types (Supervisor, Specialist)
   - LLM Models (OpenAI GPT-4, IBM Granite)
   - Memory (Chroma Vector Store, Conversation Buffer)
   - Agent Configurations, Prompts, Conversations

8. **agent-workflow-ontology.jsonld**
   - Workflows (Query, Pod Recovery, Backup)
   - Workflow Steps, Decision Points
   - Approval Flows (Human-in-the-Loop)
   - Workflow States, Transitions

9. **tool-registry-ontology.jsonld**
   - Tool Types (Query, Mutation, Notification)
   - Parameters, Permissions, Constraints
   - Rate Limits, Timeouts, Approval Requirements

## Remaining Schemas (16/25)

### Integration Schemas
- slack-integration-ontology.jsonld
- confluence-integration-ontology.jsonld
- api-integration-ontology.jsonld

### Data & Storage Schemas
- data-model-ontology.jsonld
- vector-store-ontology.jsonld
- time-series-ontology.jsonld

### Security & Compliance Schemas
- security-policy-ontology.jsonld
- compliance-ontology.jsonld

### Development Schemas
- cicd-pipeline-ontology.jsonld
- container-image-ontology.jsonld
- test-suite-ontology.jsonld
- quality-metrics-ontology.jsonld

### User & Domain Schemas
- user-management-ontology.jsonld
- access-control-ontology.jsonld
- ecommerce-domain-ontology.jsonld
- observability-domain-ontology.jsonld

## Usage

### SPARQL Queries

Query requirements and their dependencies:
```sparql
PREFIX : <http://ai-observability.nilabja-haldar.dev/ontology#>

SELECT ?req ?dep
WHERE {
  ?req a :Requirement .
  ?req :dependsOn ?dep .
}
```

Trace architectural decisions to requirements:
```sparql
PREFIX : <http://ai-observability.nilabja-haldar.dev/ontology#>

SELECT ?decision ?req
WHERE {
  ?decision a :ArchitecturalDecision .
  ?decision :influences ?req .
}
```

Find all tools requiring approval:
```sparql
PREFIX : <http://ai-observability.nilabja-haldar.dev/tools#>

SELECT ?tool ?timeout
WHERE {
  ?tool a :MutationTool .
  ?tool :approvalRequired true .
  ?tool :approvalTimeout ?timeout .
}
```

### Knowledge Graph Construction

Load schemas into a triple store (e.g., Apache Jena, GraphDB):
```bash
# Load all schemas
for schema in *.jsonld; do
  curl -X POST http://localhost:3030/observability/data \
    -H "Content-Type: application/ld+json" \
    --data-binary @$schema
done
```

### Validation

Validate instances against schemas using SHACL or JSON Schema.

## Schema Relationships

```
Requirements ──influences──> Architecture ──deploysTo──> Deployment
     │                            │                          │
     │                            │                          │
  satisfies                   monitors                   manages
     │                            │                          │
     ↓                            ↓                          ↓
   Goals                   Observability                  Pods
                                 │
                                 │
                            detects/resolves
                                 │
                                 ↓
                             Incidents
                                 │
                                 │
                            documents
                                 │
                                 ↓
                            Postmortems
```

## Benefits

1. **Semantic Interoperability**: Machine-readable relationships between all project aspects
2. **Knowledge Graph**: Build comprehensive knowledge graph of entire system
3. **AI/ML Training**: Use schemas for training AI agents on project structure
4. **Documentation**: Auto-generate documentation from schemas
5. **Validation**: Validate project structure against schemas
6. **Query & Analysis**: SPARQL queries across all project knowledge
7. **Integration**: Easier integration with external tools and systems
8. **Compliance**: Track compliance requirements and implementations
9. **Evolution**: Track system evolution over time
10. **Onboarding**: Help new team members understand system quickly

## Future Work

Complete remaining 16 schemas to provide full semantic coverage of:
- Integration patterns (Slack, Confluence, APIs)
- Data models and storage strategies
- Security policies and compliance tracking
- CI/CD pipelines and container management
- Testing strategies and quality metrics
- User management and access control
- Domain models (e-commerce, observability best practices)

## References

- [JSON-LD Specification](https://www.w3.org/TR/json-ld11/)
- [Schema.org](https://schema.org/)
- [SPARQL Query Language](https://www.w3.org/TR/sparql11-query/)
- [RDF Schema](https://www.w3.org/TR/rdf-schema/)
- [OWL Web Ontology Language](https://www.w3.org/TR/owl2-overview/)

## License

See project LICENSE file.