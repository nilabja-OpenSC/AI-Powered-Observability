"""
Pod Recovery Agent - AI-Powered Observability Platform

Main FastAPI server for the Pod Recovery Agent.
Handles pod health monitoring, diagnostics, and recovery actions.

Port: 8082
Endpoints:
- POST /query - Process pod recovery query
- POST /diagnose - Diagnose pod issues
- POST /recover - Execute recovery action (requires approval)
- GET /health - Health check
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime

import structlog
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents.common.llm_client import LLMClient
from agents.common.vector_store import VectorStore
from agents.common.tools.kubernetes import KubernetesTool
from agents.common.tools.slack import SlackTool
from agents.common.approval_workflow import ApprovalWorkflow
from agents.pod_recovery.health_monitor import HealthMonitor
from agents.pod_recovery.diagnostics import Diagnostics
from agents.pod_recovery.recovery_actions import RecoveryActions

logger = structlog.get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Pod Recovery Agent",
    description="Handles pod diagnostics and recovery",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
llm_client: Optional[LLMClient] = None
vector_store: Optional[VectorStore] = None
k8s_tool: Optional[KubernetesTool] = None
slack_tool: Optional[SlackTool] = None
approval_workflow: Optional[ApprovalWorkflow] = None
health_monitor: Optional[HealthMonitor] = None
diagnostics: Optional[Diagnostics] = None
recovery_actions: Optional[RecoveryActions] = None


class QueryRequest(BaseModel):
    """Query request model"""
    query: str
    context: Optional[str] = None


class QueryResponse(BaseModel):
    """Query response model"""
    response: str
    action_taken: Optional[str] = None
    timestamp: str


class DiagnoseRequest(BaseModel):
    """Diagnose request model"""
    pod_name: str
    namespace: str = "nilabja-haldar-dev"


class DiagnoseResponse(BaseModel):
    """Diagnose response model"""
    pod_name: str
    status: str
    issues: list
    recommendations: list
    timestamp: str


class RecoverRequest(BaseModel):
    """Recover request model"""
    pod_name: str
    action: str
    namespace: str = "nilabja-haldar-dev"
    execute: bool = False


class RecoverResponse(BaseModel):
    """Recover response model"""
    pod_name: str
    action: str
    status: str
    result: Optional[Dict[str, Any]] = None
    timestamp: str


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    global llm_client, vector_store, k8s_tool, slack_tool, approval_workflow
    global health_monitor, diagnostics, recovery_actions
    
    logger.info("pod_recovery_agent_starting")
    
    # Initialize LLM client
    llm_client = LLMClient()
    
    # Initialize vector store
    vector_store = VectorStore(
        persist_directory="./pod_recovery_memory",
        collection_name="pod_recovery_queries",
    )
    
    # Initialize tools
    k8s_tool = KubernetesTool()
    slack_tool = SlackTool()
    approval_workflow = ApprovalWorkflow(slack_tool=slack_tool)
    
    # Initialize components
    health_monitor = HealthMonitor(
        k8s_tool=k8s_tool,
        llm_client=llm_client,
    )
    
    diagnostics = Diagnostics(
        k8s_tool=k8s_tool,
        llm_client=llm_client,
    )
    
    recovery_actions = RecoveryActions(
        k8s_tool=k8s_tool,
        approval_workflow=approval_workflow,
        slack_tool=slack_tool,
    )
    
    logger.info("pod_recovery_agent_started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("pod_recovery_agent_shutting_down")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "pod-recovery-agent",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest) -> QueryResponse:
    """
    Process pod recovery query.
    
    Handles queries about:
    - Pod health status
    - Pod diagnostics
    - Recovery actions
    
    Args:
        request: Query request
    
    Returns:
        Query response
    """
    if not health_monitor or not diagnostics:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    logger.info(
        "query_received",
        query=request.query,
    )
    
    try:
        # Analyze query to determine action
        action = await _analyze_query(request.query)
        
        if action == "health_check":
            # Check pod health
            result = await health_monitor.check_all_pods()
            response = f"Health check complete. Found {len(result['unhealthy_pods'])} unhealthy pods."
        
        elif action == "diagnose":
            # Extract pod name from query
            pod_name = await _extract_pod_name(request.query)
            if pod_name:
                result = await diagnostics.diagnose(pod_name)
                response = f"Diagnosis complete for {pod_name}. Found {len(result['issues'])} issues."
            else:
                response = "Please specify a pod name for diagnosis."
        
        else:
            response = "I can help with pod health checks, diagnostics, and recovery actions."
        
        logger.info(
            "query_processed",
            action=action,
        )
        
        return QueryResponse(
            response=response,
            action_taken=action,
            timestamp=datetime.utcnow().isoformat(),
        )
    
    except Exception as e:
        logger.error(
            "query_processing_error",
            query=request.query,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/diagnose", response_model=DiagnoseResponse)
async def diagnose_pod(request: DiagnoseRequest) -> DiagnoseResponse:
    """
    Diagnose pod issues.
    
    Analyzes:
    - Pod status and events
    - Container logs
    - Resource usage
    - Recent restarts
    
    Args:
        request: Diagnose request
    
    Returns:
        Diagnosis results
    """
    if not diagnostics:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    logger.info(
        "diagnosis_started",
        pod_name=request.pod_name,
    )
    
    try:
        # Run diagnostics
        result = await diagnostics.diagnose(
            pod_name=request.pod_name,
            namespace=request.namespace,
        )
        
        logger.info(
            "diagnosis_complete",
            pod_name=request.pod_name,
            issues_found=len(result["issues"]),
        )
        
        return DiagnoseResponse(
            pod_name=request.pod_name,
            status=result["status"],
            issues=result["issues"],
            recommendations=result["recommendations"],
            timestamp=datetime.utcnow().isoformat(),
        )
    
    except Exception as e:
        logger.error(
            "diagnosis_error",
            pod_name=request.pod_name,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recover", response_model=RecoverResponse)
async def recover_pod(request: RecoverRequest) -> RecoverResponse:
    """
    Execute recovery action.
    
    Actions:
    - restart: Restart pod
    - scale: Scale deployment
    - delete: Delete pod (will be recreated)
    
    IMPORTANT: Requires human approval via Slack.
    Set execute=True to request approval and execute.
    
    Args:
        request: Recover request
    
    Returns:
        Recovery result
    """
    if not recovery_actions:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    logger.info(
        "recovery_action_requested",
        pod_name=request.pod_name,
        action=request.action,
        execute=request.execute,
    )
    
    try:
        # Execute recovery action
        result = await recovery_actions.execute(
            pod_name=request.pod_name,
            action=request.action,
            namespace=request.namespace,
            execute=request.execute,
        )
        
        logger.info(
            "recovery_action_complete",
            pod_name=request.pod_name,
            action=request.action,
            status=result["status"],
        )
        
        return RecoverResponse(
            pod_name=request.pod_name,
            action=request.action,
            status=result["status"],
            result=result.get("result"),
            timestamp=datetime.utcnow().isoformat(),
        )
    
    except Exception as e:
        logger.error(
            "recovery_action_error",
            pod_name=request.pod_name,
            action=request.action,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))


async def _analyze_query(query: str) -> str:
    """
    Analyze query to determine action.
    
    Args:
        query: User query
    
    Returns:
        Action type (health_check, diagnose, recover)
    """
    query_lower = query.lower()
    
    if "health" in query_lower or "status" in query_lower:
        return "health_check"
    elif "diagnose" in query_lower or "why" in query_lower or "issue" in query_lower:
        return "diagnose"
    elif "restart" in query_lower or "recover" in query_lower or "fix" in query_lower:
        return "recover"
    else:
        return "unknown"


async def _extract_pod_name(query: str) -> Optional[str]:
    """
    Extract pod name from query.
    
    Args:
        query: User query
    
    Returns:
        Pod name if found
    """
    # Simple extraction - look for words that might be pod names
    words = query.split()
    for word in words:
        if "-" in word and len(word) > 5:
            return word
    return None


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8082"))
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
    )


# Made with Bob