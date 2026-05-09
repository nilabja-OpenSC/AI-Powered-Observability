# Advanced Mode Rules - AI-Powered Observability Platform

This file contains advanced coding-specific rules for AI assistants working in Advanced mode.

## Project Overview
- **Language**: Python 3.11+
- **Package Manager**: pip (requirements.txt)
- **Framework**: FastAPI (Backend), Next.js (Frontend)
- **Deployment**: Helm charts on OpenShift ROSA
- **Namespace**: `nilabja-haldar-dev` (ALL operations scoped here)

## Custom Utilities & Patterns

### Slack Integration Patterns
```python
# REQUIRED: Use Slack Block Kit for all notifications
from slack_sdk import WebClient
from slack_sdk.models.blocks import SectionBlock, ActionsBlock, ButtonElement

def send_approval_request(issue_summary, resolution_steps):
    """Send Slack notification with approve/deny buttons"""
    blocks = [
        SectionBlock(text=f"🚨 Issue Detected: {issue_summary}"),
        ActionsBlock(elements=[
            ButtonElement(text="✅ Approve", action_id="approve", style="primary"),
            ButtonElement(text="❌ Deny", action_id="deny", style="danger")
        ])
    ]
    # CRITICAL: Must include callback_id for tracking approval state
    return client.chat_postMessage(channel="#observability-alerts", blocks=blocks)
```

### Human-in-the-Loop Approval Pattern
```python
# REQUIRED: All corrective actions must use this pattern
async def execute_with_approval(action_func, issue_details):
    """Execute action only after human approval"""
    # 1. Send Slack notification
    approval_id = await send_approval_request(issue_details)
    
    # 2. Wait for approval (5 min timeout = DENY)
    decision = await wait_for_approval(approval_id, timeout=300)
    
    # 3. Execute based on decision
    if decision == "APPROVED":
        result = await action_func()
        await send_slack_update(f"✅ Action completed: {result}")
        await create_confluence_report(issue_details, result)
    else:
        await send_manual_steps(issue_details.resolution_steps)
```

### Agent Tool Execution Guard
```python
# REQUIRED: Wrap all mutation operations
from functools import wraps

def require_approval(func):
    """Decorator to enforce human approval for mutations"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not kwargs.get('execute', False):
            return {"mode": "PLAN_ONLY", "plan": func.__doc__}
        
        # Require human approval via Slack
        approval = await request_human_approval(func.__name__, args, kwargs)
        if not approval:
            raise PermissionError("Human approval required but not granted")
        
        return await func(*args, **kwargs)
    return wrapper

@require_approval
async def restart_pod(pod_name: str, namespace: str = "nilabja-haldar-dev"):
    """Restart pod to resolve CrashLoopBackOff"""
    # Implementation
```

### Namespace Enforcement
```python
# REQUIRED: All Kubernetes operations must enforce namespace
ALLOWED_NAMESPACE = "nilabja-haldar-dev"

def enforce_namespace(func):
    """Ensure all k8s operations are namespace-scoped"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        namespace = kwargs.get('namespace', ALLOWED_NAMESPACE)
        if namespace != ALLOWED_NAMESPACE:
            raise ValueError(f"Operations only allowed in {ALLOWED_NAMESPACE}")
        kwargs['namespace'] = namespace
        return func(*args, **kwargs)
    return wrapper
```

## Hidden Dependencies

### Agent Initialization Order
```python
# CRITICAL: Agents must be initialized in this order
# 1. Vector store (Chroma) - for agent memory
# 2. LLM client (OpenAI/watsonx.ai) - for reasoning
# 3. Tool registry - for agent capabilities
# 4. Supervisor agent - for routing
# 5. Specialist agents - for specific tasks

# Example:
vector_store = ChromaVectorStore(persist_directory="./agent_memory")
llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
tools = ToolRegistry([prometheus_query, loki_query, slack_post_with_approval])
supervisor = SupervisorAgent(llm=llm, tools=tools, memory=vector_store)
observability_agent = ObservabilityAgent(llm=llm, tools=tools, memory=vector_store)
```

### Slack Webhook Configuration
```python
# REQUIRED: Slack webhooks must be configured before agent startup
# Environment variables:
# - SLACK_WEBHOOK_URL: For notifications
# - SLACK_BOT_TOKEN: For interactive messages
# - SLACK_SIGNING_SECRET: For verifying Slack requests

# CRITICAL: Interactive messages require a public endpoint for callbacks
# Use ngrok for local development, OpenShift Route for production
```

### Prometheus/Thanos Query Routing
```python
# REQUIRED: Route queries based on time range
def query_metrics(promql: str, time_range: str):
    """Route to Prometheus (recent) or Thanos (historical)"""
    if parse_time_range(time_range) > timedelta(hours=6):
        return thanos_query(promql, time_range)
    else:
        return prometheus_query(promql, time_range)
```

## Non-Standard Approaches

### Chat UI vs Slack Separation
```python
# CRITICAL: Chat UI and Slack have different purposes
class MessageRouter:
    def route_message(self, message: str, source: str):
        if source == "chat_ui":
            # ONLY observability queries allowed
            if self.is_mutation_request(message):
                raise ValueError("Mutations not allowed via Chat UI. Use Slack for approvals.")
            return self.handle_query(message)
        
        elif source == "slack":
            # Issue notifications and approvals
            return self.handle_issue_workflow(message)
```

### Approval State Management
```python
# REQUIRED: Track approval requests in-memory or Redis
approval_states = {}  # {callback_id: {"status": "PENDING", "timestamp": ...}}

async def wait_for_approval(callback_id: str, timeout: int = 300):
    """Wait for human decision with timeout"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if callback_id in approval_states:
            status = approval_states[callback_id]["status"]
            if status in ["APPROVED", "DENIED"]:
                return status
        await asyncio.sleep(1)
    
    # Timeout = DENY (fail-safe)
    return "DENIED"
```

### PromQL/LogQL Generation
```python
# REQUIRED: Always include namespace filter
def generate_promql(metric: str, filters: dict):
    """Generate PromQL with mandatory namespace filter"""
    filters["namespace"] = "nilabja-haldar-dev"
    filter_str = ",".join([f'{k}="{v}"' for k, v in filters.items()])
    return f'{metric}{{{filter_str}}}'

# Example:
# generate_promql("http_requests_total", {"app": "backend"})
# Returns: http_requests_total{namespace="nilabja-haldar-dev",app="backend"}
```

## Critical Implementation Details

### Timeout Handling
```python
# CRITICAL: All approval requests MUST have timeout with DENY default
# Never assume approval - always fail-safe to DENY
async def request_approval_with_timeout(issue: dict, timeout: int = 300):
    try:
        return await asyncio.wait_for(
            request_approval(issue),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        logger.warning(f"Approval timeout for {issue['id']}, defaulting to DENY")
        return "DENIED"
```

### Confluence Documentation
```python
# REQUIRED: All approved actions must be documented
async def document_incident(issue: dict, resolution: dict):
    """Create Confluence page for incident"""
    page_content = f"""
    # Incident: {issue['summary']}
    
    **Detected:** {issue['timestamp']}
    **Severity:** {issue['severity']}
    **Affected Resources:** {issue['resources']}
    
    ## Resolution Steps Taken
    {resolution['steps']}
    
    ## Outcome
    {resolution['result']}
    
    **Approved By:** {resolution['approver']}
    **Completed:** {resolution['timestamp']}
    """
    return await confluence_client.create_page(
        space="OBSERVABILITY",
        title=f"Incident-{issue['id']}",
        body=page_content
    )
```

### Error Handling for Agent Failures
```python
# REQUIRED: Agent failures must not crash the system
class AgentExecutionError(Exception):
    """Raised when agent execution fails"""
    pass

async def safe_agent_execution(agent_func, *args, **kwargs):
    """Execute agent with error handling and Slack notification"""
    try:
        return await agent_func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        await send_slack_alert(
            f"⚠️ Agent Failure: {agent_func.__name__}",
            str(e)
        )
        raise AgentExecutionError(f"Agent failed: {e}")
```

## Testing Requirements

### Approval Workflow Testing
```python
# REQUIRED: Test both approval and denial paths
@pytest.mark.asyncio
async def test_approval_workflow():
    # Test approval path
    with mock_slack_approval("APPROVED"):
        result = await execute_with_approval(restart_pod, issue_details)
        assert result["status"] == "success"
    
    # Test denial path
    with mock_slack_approval("DENIED"):
        result = await execute_with_approval(restart_pod, issue_details)
        assert result["status"] == "manual_steps_sent"
    
    # Test timeout (should default to DENY)
    with mock_slack_timeout():
        result = await execute_with_approval(restart_pod, issue_details)
        assert result["status"] == "denied_by_timeout"
```

### Namespace Isolation Testing
```python
# REQUIRED: Verify namespace enforcement
def test_namespace_enforcement():
    with pytest.raises(ValueError):
        restart_pod("test-pod", namespace="default")  # Should fail
    
    # Should succeed
    restart_pod("test-pod", namespace="nilabja-haldar-dev")
```

## MCP & Browser Tool Usage

### MCP Server Configuration
```python
# OPTIONAL: MCP servers for extended capabilities
# Not required for core functionality but can enhance agent capabilities

# Example MCP server for Prometheus queries
mcp_servers = {
    "prometheus": {
        "url": "http://prometheus-mcp-server:8080",
        "tools": ["query", "query_range", "labels"]
    }
}
```

### Browser Automation (Not Used)
```
# NOTE: Browser automation is NOT used in this project
# All interactions are via APIs (Prometheus, Grafana, Loki, Slack)
```

## IBM watsonx.ai Alternative

### Using IBM watsonx.ai instead of OpenAI
```python
# Alternative LLM configuration
from ibm_watson_machine_learning.foundation_models import Model

llm = Model(
    model_id="ibm/granite-13b-chat-v2",
    credentials={
        "apikey": os.getenv("IBM_CLOUD_API_KEY"),
        "url": "https://us-south.ml.cloud.ibm.com"
    },
    project_id=os.getenv("IBM_PROJECT_ID")
)

# Use same interface as OpenAI
response = llm.generate_text(
    prompt="Analyze this Prometheus metric...",
    params={"max_new_tokens": 500, "temperature": 0.7}
)
```

### Using watsonx Orchestrate instead of LangChain
```python
# Alternative agent framework
from ibm_watsonx_orchestrate import Agent, Skill

agent = Agent(
    name="ObservabilityAgent",
    model="ibm/granite-13b-chat-v2",
    skills=[
        Skill("prometheus_query"),
        Skill("slack_notification"),
        Skill("approval_workflow")  # Native support for human-in-the-loop
    ]
)
```

---

**Note**: This file documents project-specific patterns discovered from specifications. Standard Python practices are assumed. Advanced mode has access to MCP and Browser tools (though browser tools are not used in this project).