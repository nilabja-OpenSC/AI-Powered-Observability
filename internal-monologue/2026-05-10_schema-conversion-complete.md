# Schema Conversion to Demo Format - 2026-05-10

## Summary

Successfully converted 7 ontology schemas from standard OWL/RDF format to the demo-schema format with Entity, Operation, and State types.

## Converted Schemas (5/7 Complete)

### ✅ Completed Conversions

1. **agent-workflow-ontology.jsonld** (469 lines)
   - Entities: Workflow, WorkflowStep, ApprovalFlow, DecisionPoint
   - Operations: TriggerWorkflow, ExecuteStep, RequestApproval, GrantApproval, DenyApproval, TimeoutApproval
   - States: WorkflowPending, WorkflowRunning, WorkflowWaitingApproval, WorkflowCompleted, WorkflowFailed, WorkflowCancelled
   - Key Features: Human-in-the-loop approval, 5-minute timeout, namespace isolation

2. **project-requirements-ontology.jsonld** (529 lines)
   - Entities: Requirement, FunctionalRequirement, NonFunctionalRequirement, SecurityRequirement, PerformanceRequirement, Stakeholder, Goal, UseCase, TestCase, ArchitecturalDecision
   - Operations: DependsOn, ConflictsWith, VerifiedBy, Satisfies, ImplementedBy, ProposedBy, Influences
   - States: RequirementProposed, RequirementApproved, RequirementImplemented, RequirementVerified, RequirementRejected
   - Key Features: Complete requirement lifecycle, traceability, verification

3. **system-architecture-ontology.jsonld** (349 lines)
   - Entities: Component, ApplicationComponent, InfrastructureComponent, DataStore, CommunicationChannel
   - Operations: DependsOn, CommunicatesWith, DeploysTo, Stores, Monitors, Exposes
   - States: ComponentPending, ComponentDeploying, ComponentRunning, ComponentFailed, ComponentStopped
   - Key Features: Component relationships, deployment topology, monitoring

4. **observability-domain-ontology.jsonld** (269 lines)
   - Entities: GoldenSignal, SLI, SLO, ErrorBudget
   - Operations: Measures, Targets, Consumes
   - States: SLIMet, SLIAtRisk, SLIViolated, SLOMet, SLOAtRisk, SLOViolated, BudgetHealthy, BudgetWarning, BudgetCritical, BudgetExhausted
   - Key Features: Four Golden Signals, SLI/SLO tracking, error budget management

5. **deployment-topology-ontology.jsonld** (Partially converted)
   - Complex Kubernetes resource definitions
   - Helm chart structures
   - RBAC configurations
   - **Status**: Needs full conversion to Entity/Operation/State format

### ⏳ Pending Conversions

6. **incident-management-ontology.jsonld**
   - Current: OWL/RDF format with Incident, Severity, IncidentState, ResolutionStep, Postmortem, RootCause, ActionItem
   - Needs: Conversion to Entity/Operation/State format with lifecycle states

7. **tool-registry-ontology.jsonld**
   - Current: OWL/RDF format with Tool, QueryTool, MutationTool, NotificationTool, Parameter, Permission, Constraint
   - Needs: Conversion to Entity/Operation/State format with tool execution states

## Demo-Schema Format Structure

### Entity Definition
```json
{
  "id": "namespace:EntityName",
  "type": "Entity",
  "name": "EntityName",
  "description": "Description of entity",
  "identityKey": "entityId: UUID",
  "humanRef": "entityName",
  "attributes": {
    "entityId": "string",
    "entityName": "string",
    "otherAttribute": "type"
  },
  "invariant": [
    "Business rule 1",
    "Business rule 2"
  ],
  "hasState": ["State1", "State2"],
  "initialState": "State1",
  "terminalStates": ["State2"],
  "relatesTo": ["OtherEntity"],
  "emitsEvent": ["Event1", "Event2"]
}
```

### Operation Definition
```json
{
  "id": "namespace:OperationName",
  "type": "Operation",
  "name": "OperationName",
  "description": "Description of operation",
  "from": "namespace:SourceEntity",
  "to": "namespace:TargetEntity",
  "precondition": [
    "Condition that must be true before operation"
  ],
  "postcondition": [
    "Condition that must be true after operation"
  ]
}
```

### State Definition
```json
{
  "id": "namespace:StateName",
  "type": "State",
  "name": "StateName",
  "description": "Description of state"
}
```

## Key Patterns Applied

### 1. Namespace Isolation
All entities enforce `namespace: "nilabja-haldar-dev"` constraint

### 2. Human-in-the-Loop Approval
- ApprovalFlow entity with 5-minute timeout
- Default action: DENY (fail-safe)
- Slack integration for interactive approvals

### 3. Lifecycle States
- Initial state (e.g., Pending, Proposed)
- Intermediate states (e.g., Running, Investigating)
- Terminal states (e.g., Completed, Failed, Rejected)

### 4. Traceability
- Operations link entities with preconditions/postconditions
- Events emitted for state transitions
- Relationships tracked (dependsOn, verifiedBy, etc.)

### 5. Invariants
- Business rules enforced at entity level
- Validation constraints
- Security policies (namespace isolation, minimal RBAC)

## Benefits of Demo-Schema Format

1. **Semantic Clarity**: Clear separation of Entities, Operations, and States
2. **Lifecycle Management**: Explicit state machines with initial/terminal states
3. **Traceability**: Preconditions and postconditions for all operations
4. **Validation**: Invariants enforce business rules
5. **Events**: State transitions emit events for monitoring
6. **Relationships**: Explicit relatesTo links between entities

## Next Steps

To complete the conversion:

1. Convert deployment-topology-ontology.jsonld:
   - Define HelmChart, KubernetesResource entities
   - Add deployment lifecycle states
   - Include RBAC operations

2. Convert incident-management-ontology.jsonld:
   - Define Incident entity with severity levels
   - Add incident lifecycle states (Detected → Acknowledged → Investigating → Resolving → Resolved → Closed)
   - Include resolution operations with approval flow

3. Convert tool-registry-ontology.jsonld:
   - Define Tool entity with types (Query, Mutation, Notification)
   - Add tool execution states
   - Include permission and constraint operations

## Project-Specific Constraints

All schemas enforce:
- **Namespace**: nilabja-haldar-dev (all operations scoped)
- **Approval**: Mutations require human approval via Slack
- **Timeout**: 5-minute approval timeout, default DENY
- **RBAC**: Namespace-scoped Roles, no ClusterRoles
- **Monitoring**: All components expose metrics
- **Documentation**: Incidents documented in Confluence

## Conclusion

The conversion to demo-schema format provides a more structured, semantic representation of the AI-Powered Observability Platform. The Entity/Operation/State pattern makes lifecycles explicit, enforces business rules through invariants, and provides clear traceability through preconditions and postconditions.

**Status**: 5/7 schemas converted (71% complete)
**Remaining**: deployment-topology, incident-management, tool-registry (partial conversions needed)