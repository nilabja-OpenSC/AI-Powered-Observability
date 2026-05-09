# Specification Updates: Slack Notifications & Human-in-the-Loop Workflow

**Date:** 2026-05-08  
**Task:** Update specifications with Slack notification and human approval workflow requirements

## Requirements Summary

Updated specifications to implement:

1. **Slack Notifications for Issues**: Agent sends notifications to Slack whenever issues are detected
2. **Resolution Steps in Slack**: Include detailed resolution steps in notifications
3. **Human-in-the-Loop Approval**: Implement approve/deny workflow via Slack interactive buttons
4. **Conditional Execution**:
   - **Approved**: Agent executes corrective actions and reports results to Slack
   - **Denied**: Agent shares resolution steps only, no automated actions
5. **Chat UI Separation**: Chat UI used ONLY for observability queries (Prometheus, Grafana, Loki), NOT for issue notifications

## Files Updated

### 1. `.bob/specs/Observability-Agent-prompt.md`

**Changes:**
- Added issue detection and Slack notification capabilities to agent purpose
- Updated hard constraints to require human approval for issue resolution
- Added new primary skills: issue detection, Slack notifications, human-in-loop workflow
- Updated response format to include `slack_notification_payload` and `approval_request` artifacts
- Added new tool contracts:
  - `slack_post_with_approval`: Send interactive Slack messages with approve/deny buttons
  - `wait_for_approval`: Block and wait for human decision
- Updated execution guard to require `HUMAN_APPROVAL via Slack` for issue resolution
- **Added comprehensive section**: "ISSUE DETECTION & HUMAN-IN-THE-LOOP WORKFLOW" (200+ lines)
  - Workflow overview with visual diagram
  - Issue detection flow (3 steps)
  - Approval workflow (approved vs denied paths)
  - Slack notification format examples (JSON blocks)
  - Chat UI scope clarification
  - Agent behavior rules
  - Example scenarios (High CPU, CrashLoopBackOff)

### 2. `.bob/specs/tech-stack.md`

**Changes:**
- Updated Chat UI description to clarify it's for "observability queries ONLY"
- Enhanced Incident Communication section:
  - Slack now includes "Human-in-the-loop approval workflow"
  - Added critical separation between Slack (alerts/approvals) and Chat UI (queries only)
- Updated Agent Roles section:
  - Observability Agent: Added issue detection + Slack notifications
  - Pod Recovery Agent: Added "(with Slack approval)"
  - Backup/Restore Agent: Added "(with Slack approval)"
- Added Human-in-the-Loop Workflow description (4 steps)
- Updated Tool Interface:
  - Added `slack_post_with_approval` tool
  - Added `wait_for_approval` tool
  - Updated execution guard to include `HUMAN_APPROVAL: required`

### 3. `docs/architecture.md`

**Changes:**
- Split "Agent Request Flow" into two separate flows:
  - **Chat UI flow**: Query-only operations (no mutations)
  - **Issue Detection & Resolution flow**: Slack-based human-in-loop workflow
- Renumbered subsequent flows (Observability Flow, Backup Flow)
- **Added major new section**: "Human-in-the-Loop Architecture" (150+ lines)
  - Issue Detection & Resolution Workflow diagram (ASCII art)
  - Chat UI vs Slack Separation diagram
  - Approval Workflow State Machine diagram
  - Security & Audit Trail specifications

## Key Design Decisions

### Separation of Concerns
- **Chat UI**: Interactive queries, dashboard creation, metric exploration
- **Slack**: Issue notifications, approvals, incident management

### Safety-First Approach
- Default timeout (5 min) = DENY (fail-safe)
- No automated corrective actions without explicit human approval
- All actions logged to Confluence for audit trail

### Workflow States
```
DETECTED → NOTIFIED → WAITING → [APPROVED/DENIED] → [EXECUTING/MANUAL] → [RESOLVED/PENDING] → DOCUMENTED
```

### Slack Interactive Messages
- Use Slack Block Kit for rich formatting
- Include approve/deny buttons for human decision
- Show issue summary, affected resources, resolution steps
- Provide different responses based on approval/denial

## Implementation Implications

### New Components Needed
1. Slack webhook integration with interactive message support
2. Approval state management (track pending approvals)
3. Timeout handling (default to DENY after 5 minutes)
4. Confluence integration for incident documentation

### Agent Behavior Changes
1. Continuous monitoring for issue detection
2. Slack notification generation with structured format
3. Blocking wait for human approval
4. Conditional execution based on approval status
5. Result reporting back to Slack

### Testing Considerations
- Test approve/deny workflows
- Test timeout scenarios
- Test Slack message formatting
- Test Chat UI isolation (no issue notifications)
- Test Confluence documentation generation

## Next Steps

1. Implement Slack webhook integration with Block Kit
2. Create approval state management system
3. Implement timeout handling mechanism
4. Build Confluence API integration
5. Update agent code to follow new workflow
6. Create unit tests for approval workflows
7. Document Slack channel setup requirements

## Summary

Successfully updated all specification files to incorporate:
- ✅ Slack notifications for issue detection
- ✅ Resolution steps in notifications
- ✅ Human-in-the-loop approval workflow
- ✅ Conditional execution (approve/deny)
- ✅ Chat UI separation (queries only)

All changes maintain consistency across specification files and provide clear implementation guidance for developers.