# Rules Files Update Summary

**Date:** 2026-05-08  
**Task:** Update all rules files with project-specific guidelines from specifications

## Overview

Updated all rules files across different modes (basic, advanced, code, plan) to incorporate project-specific patterns, constraints, and best practices for the AI-Powered Observability Platform.

## Files Updated

### 1. `.bob/rules/basic_rules.md`

**Changes:**
- Converted from generic rules to project-specific guidelines
- Added "Project-Specific Rules" section with:
  - Namespace constraint (`nilabja-haldar-dev`)
  - Execution safety (PLAN_ONLY default, human approval required)
  - Communication channels (Slack vs Chat UI separation)
  - Tech stack preferences (OpenAI/IBM watsonx.ai alternatives)
  - Observability standards (namespace filters, Golden Signals)
  - Slack notification format (Block Kit)
  - File organization structure

**Key Additions:**
- Namespace enforcement rules
- Human-in-the-loop approval workflow
- Chat UI vs Slack separation
- Slack Block Kit formatting requirements

### 2. `.bob/rules-advanced/AGENTS.md`

**Changes:**
- Replaced placeholder content with comprehensive project-specific patterns
- Added 285 lines of detailed implementation guidance

**Sections Added:**
1. **Custom Utilities & Patterns**
   - Slack integration with Block Kit
   - Human-in-the-loop approval pattern
   - Agent tool execution guard decorator
   - Namespace enforcement decorator

2. **Hidden Dependencies**
   - Agent initialization order (critical sequence)
   - Slack webhook configuration requirements
   - Prometheus/Thanos query routing logic

3. **Non-Standard Approaches**
   - Chat UI vs Slack separation pattern
   - Approval state management (in-memory/Redis)
   - PromQL/LogQL generation with namespace filters

4. **Critical Implementation Details**
   - Timeout handling (default to DENY)
   - Confluence documentation requirements
   - Error handling for agent failures

5. **Testing Requirements**
   - Approval workflow testing (approve/deny/timeout paths)
   - Namespace isolation testing

6. **MCP & Browser Tool Usage**
   - MCP server configuration (optional)
   - Browser automation (not used in this project)

7. **IBM watsonx.ai Alternative**
   - Using IBM watsonx.ai instead of OpenAI
   - Using watsonx Orchestrate instead of LangChain

### 3. `.bob/rules-code/AGENTS.md`

**Changes:**
- Replaced placeholder content with coding-specific guidelines
- Added 254 lines of implementation patterns

**Sections Added:**
1. **Custom Utilities & Patterns** (same as advanced mode)
2. **Hidden Dependencies** (same as advanced mode)
3. **Non-Standard Approaches** (same as advanced mode)
4. **Critical Implementation Details** (same as advanced mode)
5. **Testing Requirements** (same as advanced mode)
6. **Code Style Guidelines** (NEW)
   - Import order (standard, third-party, local)
   - Naming conventions (snake_case, PascalCase, UPPER_SNAKE_CASE)
   - Type hints requirements

**Key Differences from Advanced Mode:**
- No MCP/Browser tool sections (Code mode doesn't have access)
- Added code style guidelines
- More focused on implementation details

### 4. `.bob/rules-plan/AGENTS.md`

**Changes:**
- Replaced placeholder content with architecture-specific guidelines
- Added 213 lines of architectural patterns and constraints

**Sections Added:**
1. **Hidden Architectural Constraints**
   - Namespace isolation (no cluster-wide access)
   - Human-in-the-loop requirement (affects workflow design)
   - Communication channel separation (Slack vs Chat UI)
   - Storage constraints (single-node PVCs)

2. **Non-Standard Patterns**
   - Agent orchestration pattern (Supervisor → Specialists)
   - Approval workflow state machine
   - Query routing pattern (Prometheus vs Thanos)
   - Dual tech stack support (OpenAI vs IBM watsonx.ai)

3. **Critical Design Decisions**
   - Why Slack for approvals (not Chat UI)
   - Why namespace-scoped (not cluster-wide)
   - Why human-in-the-loop (not fully autonomous)
   - Why separate Chat UI and Slack

4. **Component Interactions**
   - Agent → Observability Stack
   - Agent → Kubernetes
   - Agent → External Services
   - Hidden dependencies

5. **Performance & Scalability Considerations**
   - Agent scalability (single replica constraint)
   - Prometheus/Thanos query performance
   - Slack rate limits
   - Approval timeout impact

6. **Testing & Deployment Architecture**
   - Testing strategy (unit, integration, e2e)
   - Deployment order
   - Rollback strategy

7. **Backwards Compatibility Requirements**
   - API versioning
   - Agent memory migration
   - Helm chart upgrades

8. **Architecture Evolution Path**
   - Phase 1: Manual approval (current)
   - Phase 2: Conditional autonomy (future)
   - Phase 3: Full autonomy with guardrails (future)

## Key Patterns Documented

### 1. Human-in-the-Loop Approval Pattern
```python
async def execute_with_approval(action_func, issue_details):
    approval_id = await send_approval_request(issue_details)
    decision = await wait_for_approval(approval_id, timeout=300)
    if decision == "APPROVED":
        result = await action_func()
        await send_slack_update(f"✅ Action completed: {result}")
        await create_confluence_report(issue_details, result)
    else:
        await send_manual_steps(issue_details.resolution_steps)
```

### 2. Namespace Enforcement Pattern
```python
ALLOWED_NAMESPACE = "nilabja-haldar-dev"

def enforce_namespace(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        namespace = kwargs.get('namespace', ALLOWED_NAMESPACE)
        if namespace != ALLOWED_NAMESPACE:
            raise ValueError(f"Operations only allowed in {ALLOWED_NAMESPACE}")
        kwargs['namespace'] = namespace
        return func(*args, **kwargs)
    return wrapper
```

### 3. Chat UI vs Slack Separation Pattern
```python
class MessageRouter:
    def route_message(self, message: str, source: str):
        if source == "chat_ui":
            if self.is_mutation_request(message):
                raise ValueError("Mutations not allowed via Chat UI. Use Slack for approvals.")
            return self.handle_query(message)
        elif source == "slack":
            return self.handle_issue_workflow(message)
```

### 4. Approval State Machine
```
DETECTED → NOTIFIED → WAITING → [APPROVED/DENIED] → [EXECUTING/MANUAL] → [RESOLVED/PENDING] → DOCUMENTED
```

## Critical Constraints Documented

1. **Namespace Isolation**: All operations in `nilabja-haldar-dev` only
2. **Human Approval Required**: No automated corrective actions without approval
3. **Timeout = DENY**: 5-minute timeout defaults to denial (fail-safe)
4. **Chat UI = Read-Only**: Only observability queries, no mutations
5. **Slack = Approval Gateway**: All issue notifications and approvals via Slack
6. **Confluence = Audit Trail**: All approved actions documented

## Testing Requirements Documented

1. **Approval Workflow Testing**: Test approve, deny, and timeout paths
2. **Namespace Isolation Testing**: Verify operations fail outside allowed namespace
3. **Chat UI Restriction Testing**: Verify mutations rejected from Chat UI
4. **Slack Integration Testing**: Test interactive messages and callbacks
5. **Agent Failure Testing**: Verify graceful degradation and Slack alerts

## Tech Stack Alternatives Documented

### Primary Stack
- LLM: OpenAI GPT-4
- Agent Framework: LangChain
- Vector Store: Chroma

### Alternative Stack (IBM)
- LLM: IBM watsonx.ai (Granite models)
- Agent Framework: IBM watsonx Orchestrate
- Vector Store: IBM watsonx.data

## Benefits of Updated Rules

1. **Consistency**: All modes follow same project-specific patterns
2. **Safety**: Critical constraints documented and enforced
3. **Clarity**: Non-obvious patterns explicitly documented
4. **Maintainability**: Future developers understand architectural decisions
5. **Testing**: Clear testing requirements for all workflows
6. **Flexibility**: Dual tech stack support (OpenAI vs IBM)

## Next Steps for Implementation

1. Follow namespace enforcement patterns in all Kubernetes operations
2. Implement human-in-the-loop approval workflow with Slack
3. Separate Chat UI (queries) from Slack (approvals) in routing logic
4. Add timeout handling with DENY default to all approval requests
5. Document all approved actions to Confluence
6. Test all approval workflow paths (approve, deny, timeout)
7. Verify namespace isolation in all operations

## Summary

Successfully updated all rules files (basic, advanced, code, plan) with comprehensive project-specific guidelines. Each mode now has detailed patterns, constraints, and best practices tailored to the AI-Powered Observability Platform. These rules will guide all future coding and planning activities to ensure consistency, safety, and adherence to architectural decisions.