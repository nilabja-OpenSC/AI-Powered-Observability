"""
Backup/Restore Agent - AI-Powered Observability Platform

Main FastAPI server for the Backup/Restore Agent.
Handles backup and restore operations using Velero and Argo Workflows.

Port: 8083
Endpoints:
- POST /query - Process backup/restore query
- POST /backup - Create backup
- POST /restore - Restore from backup
- GET /backups - List available backups
- GET /health - Health check
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime

import structlog
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents.common.llm_client import LLMClient
from agents.common.vector_store import VectorStore
from agents.common.tools.slack import SlackTool
from agents.common.approval_workflow import ApprovalWorkflow
from agents.backup_restore.velero_client import VeleroClient
from agents.backup_restore.argo_client import ArgoClient
from agents.backup_restore.backup_scheduler import BackupScheduler

logger = structlog.get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Backup/Restore Agent",
    description="Handles backup and restore operations",
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
slack_tool: Optional[SlackTool] = None
approval_workflow: Optional[ApprovalWorkflow] = None
velero_client: Optional[VeleroClient] = None
argo_client: Optional[ArgoClient] = None
backup_scheduler: Optional[BackupScheduler] = None


class QueryRequest(BaseModel):
    """Query request model"""
    query: str
    context: Optional[str] = None


class QueryResponse(BaseModel):
    """Query response model"""
    response: str
    action_taken: Optional[str] = None
    timestamp: str


class BackupRequest(BaseModel):
    """Backup request model"""
    name: Optional[str] = None
    namespace: str = "nilabja-haldar-dev"
    include_resources: Optional[List[str]] = None
    execute: bool = False


class BackupResponse(BaseModel):
    """Backup response model"""
    backup_name: str
    status: str
    message: str
    timestamp: str


class RestoreRequest(BaseModel):
    """Restore request model"""
    backup_name: str
    namespace: str = "nilabja-haldar-dev"
    execute: bool = False


class RestoreResponse(BaseModel):
    """Restore response model"""
    backup_name: str
    status: str
    message: str
    timestamp: str


class BackupListResponse(BaseModel):
    """Backup list response model"""
    backups: List[Dict[str, Any]]
    total: int
    timestamp: str


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    global llm_client, vector_store, slack_tool, approval_workflow
    global velero_client, argo_client, backup_scheduler
    
    logger.info("backup_restore_agent_starting")
    
    # Initialize LLM client
    llm_client = LLMClient()
    
    # Initialize vector store
    vector_store = VectorStore(
        persist_directory="./backup_restore_memory",
        collection_name="backup_restore_queries",
    )
    
    # Initialize tools
    slack_tool = SlackTool()
    approval_workflow = ApprovalWorkflow()
    
    # Initialize clients
    velero_client = VeleroClient()
    argo_client = ArgoClient()
    
    # Initialize scheduler
    backup_scheduler = BackupScheduler(
        velero_client=velero_client,
        slack_tool=slack_tool,
    )
    
    logger.info("backup_restore_agent_started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("backup_restore_agent_shutting_down")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "backup-restore-agent",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest) -> QueryResponse:
    """
    Process backup/restore query.
    
    Handles queries about:
    - Listing backups
    - Creating backups
    - Restoring from backups
    
    Args:
        request: Query request
    
    Returns:
        Query response
    """
    if not velero_client:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    logger.info(
        "query_received",
        query=request.query,
    )
    
    try:
        # Analyze query to determine action
        action = await _analyze_query(request.query)
        
        if action == "list_backups":
            # List available backups
            backups = velero_client.list_backups()
            response = f"Found {len(backups)} backup(s). Use /backups endpoint for details."
        
        elif action == "create_backup":
            response = "To create a backup, use the /backup endpoint with execute=True."
        
        elif action == "restore":
            response = "To restore from a backup, use the /restore endpoint with the backup name."
        
        else:
            response = "I can help with listing backups, creating backups, and restoring from backups."
        
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


@app.post("/backup", response_model=BackupResponse)
async def create_backup(request: BackupRequest) -> BackupResponse:
    """
    Create backup using Velero.
    
    IMPORTANT: Requires human approval via Slack.
    Set execute=True to request approval and execute.
    
    Args:
        request: Backup request
    
    Returns:
        Backup result
    """
    if not velero_client or not approval_workflow:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    # Generate backup name if not provided
    backup_name = request.name or f"backup-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
    
    logger.info(
        "backup_requested",
        backup_name=backup_name,
        execute=request.execute,
    )
    
    # If not executing, return plan
    if not request.execute:
        return BackupResponse(
            backup_name=backup_name,
            status="plan",
            message="To execute, set execute=True and approval will be requested",
            timestamp=datetime.utcnow().isoformat(),
        )
    
    try:
        # Request approval
        issue_details = {
            "id": f"backup-{backup_name}",
            "summary": f"Create backup: {backup_name}",
            "severity": "medium",
            "affected_resources": [f"namespace/{request.namespace}"],
            "resolution_steps": [
                f"Backup name: {backup_name}",
                f"Namespace: {request.namespace}",
                f"Resources: {request.include_resources or 'all'}",
            ],
        }
        
        approval = await approval_workflow.request_approval(
            issue_summary=issue_details["summary"],
            affected_resources=issue_details["affected_resources"],
            resolution_steps=issue_details["resolution_steps"],
        )
        
        if approval != "APPROVED":
            return BackupResponse(
                backup_name=backup_name,
                status="denied",
                message="Backup not approved",
                timestamp=datetime.utcnow().isoformat(),
            )
        
        # Create backup
        result = velero_client.create_backup(
            name=backup_name,
            namespace=request.namespace,
            include_resources=request.include_resources,
        )
        
        # Send success notification
        if slack_tool:
            slack_tool.send_success_notification(
                action_type=f"Backup created: {backup_name}",
                summary=f"Backup {backup_name} created successfully",
                details={"namespace": request.namespace},
            )
        
        logger.info(
            "backup_created",
            backup_name=backup_name,
        )
        
        return BackupResponse(
            backup_name=backup_name,
            status="success",
            message=result["message"],
            timestamp=datetime.utcnow().isoformat(),
        )
    
    except Exception as e:
        logger.error(
            "backup_error",
            backup_name=backup_name,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/restore", response_model=RestoreResponse)
async def restore_backup(request: RestoreRequest) -> RestoreResponse:
    """
    Restore from backup using Velero.
    
    IMPORTANT: Requires human approval via Slack.
    Set execute=True to request approval and execute.
    
    Args:
        request: Restore request
    
    Returns:
        Restore result
    """
    if not velero_client or not approval_workflow:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    logger.info(
        "restore_requested",
        backup_name=request.backup_name,
        execute=request.execute,
    )
    
    # If not executing, return plan
    if not request.execute:
        return RestoreResponse(
            backup_name=request.backup_name,
            status="plan",
            message="To execute, set execute=True and approval will be requested",
            timestamp=datetime.utcnow().isoformat(),
        )
    
    try:
        # Request approval
        issue_details = {
            "id": f"restore-{request.backup_name}",
            "summary": f"Restore from backup: {request.backup_name}",
            "severity": "high",
            "affected_resources": [f"namespace/{request.namespace}"],
            "resolution_steps": [
                f"Backup: {request.backup_name}",
                f"Namespace: {request.namespace}",
                "WARNING: This will overwrite existing resources",
            ],
        }
        
        approval = await approval_workflow.request_approval(
            issue_summary=issue_details["summary"],
            affected_resources=issue_details["affected_resources"],
            resolution_steps=issue_details["resolution_steps"],
        )
        
        if approval != "APPROVED":
            return RestoreResponse(
                backup_name=request.backup_name,
                status="denied",
                message="Restore not approved",
                timestamp=datetime.utcnow().isoformat(),
            )
        
        # Restore backup
        result = velero_client.restore_backup(
            backup_name=request.backup_name,
            namespace=request.namespace,
        )
        
        # Send success notification
        if slack_tool:
            slack_tool.send_success_notification(
                action_type=f"Restore from backup: {request.backup_name}",
                summary=f"Restored from {request.backup_name} successfully",
                details={"namespace": request.namespace},
            )
        
        logger.info(
            "restore_complete",
            backup_name=request.backup_name,
        )
        
        return RestoreResponse(
            backup_name=request.backup_name,
            status="success",
            message=result["message"],
            timestamp=datetime.utcnow().isoformat(),
        )
    
    except Exception as e:
        logger.error(
            "restore_error",
            backup_name=request.backup_name,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/backups", response_model=BackupListResponse)
async def list_backups() -> BackupListResponse:
    """
    List available backups.
    
    Returns:
        List of backups
    """
    if not velero_client:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    logger.info("listing_backups")
    
    try:
        backups = velero_client.list_backups()
        
        logger.info(
            "backups_listed",
            total=len(backups),
        )
        
        return BackupListResponse(
            backups=backups,
            total=len(backups),
            timestamp=datetime.utcnow().isoformat(),
        )
    
    except Exception as e:
        logger.error(
            "list_backups_error",
            error=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))


async def _analyze_query(query: str) -> str:
    """
    Analyze query to determine action.
    
    Args:
        query: User query
    
    Returns:
        Action type (list_backups, create_backup, restore)
    """
    query_lower = query.lower()
    
    if "list" in query_lower or "show" in query_lower or "available" in query_lower:
        return "list_backups"
    elif "create" in query_lower or "backup" in query_lower:
        return "create_backup"
    elif "restore" in query_lower:
        return "restore"
    else:
        return "unknown"


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8083"))
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
    )


# Made with Bob