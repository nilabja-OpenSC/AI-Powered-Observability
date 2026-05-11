# Software Requirements Ontology - Revised to Match Demo Format

**Timestamp**: 2026-05-10T17:42:00Z

## Key Differences Explained

### 1. **Structural Approach**
- **Original schema**: Traditional OWL/RDF ontology with `owl:Class`, `rdfs:subClassOf`, `owl:ObjectProperty`
- **Demo format**: Entity-Operation-State model with explicit state machines

### 2. **Entity Definition**
- **Original**: Used `@type: "owl:Class"` with nested property definitions
- **Demo**: Uses `"type": "Entity"` with flat `attributes` object containing simple type strings

### 3. **Identity & References**
- **Original**: Complex URIs and `@id` references
- **Demo**: 
  - `identityKey`: Technical UUID for system identity
  - `humanRef`: Human-readable reference field (e.g., requirementCode, stakeholderName)

### 4. **Relationships**
- **Original**: `owl:ObjectProperty` with `rdfs:domain` and `rdfs:range`
- **Demo**: `"type": "Operation"` with:
  - `from`: Source entity
  - `to`: Target entity
  - `precondition`: Array of conditions that must be true before operation
  - `postcondition`: Array of conditions that must be true after operation

### 5. **State Management**
- **Original**: No explicit state machine modeling
- **Demo**: Explicit state lifecycle with:
  - `hasState`: Array of possible states
  - `initialState`: Starting state
  - `terminalStates`: End states
  - `emitsEvent`: Events triggered by state transitions
  - Separate State entities defined

### 6. **Invariants**
- **Original**: Not explicitly modeled
- **Demo**: `invariant` array defining business rules and constraints that must always hold

### 7. **Attributes Type System**
- **Original**: XSD types (`xsd:string`, `xsd:dateTime`)
- **Demo**: Simple type strings (`string`, `dateTime`, `string|null` for nullable)

## Revised Schema Structure

### Entities (9 total)
1. **Requirement** - Base requirement entity with state machine
2. **FunctionalRequirement** - Behavior/function requirements
3. **NonFunctionalRequirement** - Quality attributes
4. **SecurityRequirement** - Security and compliance
5. **PerformanceRequirement** - Performance characteristics
6. **Stakeholder** - People/groups with interest
7. **Goal** - High-level objectives
8. **UseCase** - Usage scenarios
9. **TestCase** - Verification tests with state machine

### Operations (13 total)
1. **RequestedBy** - Stakeholder requests requirement
2. **OwnedBy** - Stakeholder owns requirement
3. **ApprovedBy** - Stakeholder approves requirement (triggers state change)
4. **Satisfies** - Requirement satisfies goal
5. **Implements** - Requirement implements use case
6. **DependsOn** - Requirement depends on another
7. **ConflictsWith** - Requirements conflict
8. **Refines** - Requirement refines another
9. **DerivedFrom** - Requirement derived from source
10. **VerifiedBy** - Requirement verified by test
11. **Covers** - Use case covers requirement
12. **Includes** - Use case includes another
13. **Extends** - Use case extends another

### States (10 total)
**Requirement States:**
- RequirementDraft (initial)
- RequirementApproved
- RequirementImplemented
- RequirementVerified (terminal)
- RequirementDeprecated (terminal)

**Test States:**
- TestPending (initial)
- TestPassed (terminal)
- TestFailed
- TestBlocked
- TestSkipped (terminal)

## Why This Format?

The demo format is designed for:
1. **State Machine Modeling**: Explicit lifecycle management with state transitions
2. **Operational Semantics**: Operations define preconditions/postconditions (contract-based)
3. **Business Rules**: Invariants capture domain constraints
4. **Human Readability**: Simpler structure, clearer semantics
5. **Tooling Support**: Easier to generate code, validate, and visualize
6. **Event-Driven**: State changes emit events for reactive systems

## File Location
`context-studio-lab/software-requirements-ontology.jsonld`

## Compliance with Demo Format
✅ Uses Entity-Operation-State structure
✅ Flat attributes with simple types
✅ identityKey (UUID) and humanRef defined
✅ State machines with initial/terminal states
✅ Operations with preconditions/postconditions
✅ Invariants for business rules
✅ relatesTo for entity relationships
✅ emitsEvent for state transitions