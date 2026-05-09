"""
Observability Agent - AI-Powered Observability Platform

Main FastAPI server for the Observability Agent.
Handles queries about metrics, logs, and dashboards.

Port: 8081
Endpoints:
- POST /query - Process observability query
- POST /detect-issues - Detect issues from metrics/logs
- POST /create-dashboard - Create Grafana dashboard
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
from agents.common.tools.prometheus import PrometheusTool
from agents.common.tools.loki import LokiTool
from agents.common.tools.slack import SlackTool
from agents.observability.query_generator import QueryGenerator
from agents.observability.issue_detector import IssueDetector
from agents.observability.notification_handler import NotificationHandler
from agents.observability.dashboard_generator import DashboardGenerator

logger = structlog.get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Observability Agent",
    description="Handles metrics, logs, and dashboard queries",
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
prometheus_tool: Optional[PrometheusTool] = None
loki_tool: Optional[LokiTool] = None
slack_tool: Optional[SlackTool] = None
query_generator: Optional[QueryGenerator] = None
issue_detector: Optional[IssueDetector] = None
notification_handler: Optional[NotificationHandler] = None
dashboard_generator: Optional[DashboardGenerator] = None


class QueryRequest(BaseModel):
    """Query request model"""
    query: str
    context: Optional[str] = None


class QueryResponse(BaseModel):
    """Query response model"""
    response: str
    query_type: str
    data: Optional[Dict[str, Any]] = None
    timestamp: str


class IssueDetectionRequest(BaseModel):
    """Issue detection request model"""
    time_range: str = "5m"
    severity_threshold: str = "medium"


class IssueDetectionResponse(BaseModel):
    """Issue detection response model"""
    issues: list
    timestamp: str


class DashboardRequest(BaseModel):
    """Dashboard creation request model"""
    title: str
    description: Optional[str] = None
    panels: list


class DashboardResponse(BaseModel):
    """Dashboard creation response model"""
    dashboard_url: str
    dashboard_id: str
    timestamp: str


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    global llm_client, vector_store, prometheus_tool, loki_tool, slack_tool
    global query_generator, issue_detector, notification_handler, dashboard_generator
    
    logger.info("observability_agent_starting")
    
    # Initialize LLM client
    llm_client = LLMClient()
    
    # Initialize vector store
    vector_store = VectorStore(
        persist_directory="./observability_memory",
        collection_name="observability_queries",
    )
    
    # Initialize tools
    prometheus_tool = PrometheusTool()
    loki_tool = LokiTool()
    slack_tool = SlackTool()
    
    # Initialize components
    query_generator = QueryGenerator(llm_client=llm_client)
    
    issue_detector = IssueDetector(
        llm_client=llm_client,
        prometheus_tool=prometheus_tool,
        loki_tool=loki_tool,
    )
    
    notification_handler = NotificationHandler(
        slack_tool=slack_tool,
    )
    
    dashboard_generator = DashboardGenerator(
        llm_client=llm_client,
    )
    
    logger.info("observability_agent_started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("observability_agent_shutting_down")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "observability-agent",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest) -> QueryResponse:
    """
    Process observability query.
    
    Handles queries about:
    - Metrics (CPU, memory, HTTP requests, etc.)
    - Logs (error logs, application logs, etc.)
    - Dashboards (create, view, etc.)
    
    Args:
        request: Query request
    
    Returns:
        Query response with data
    """
    if not query_generator or not prometheus_tool or not loki_tool:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    logger.info(
        "query_received",
        query=request.query,
    )
    
    try:
        # Generate PromQL/LogQL query
        query_result = await query_generator.generate(
            query=request.query,
            context=request.context,
        )
        
        query_type = query_result["type"]
        
        # Execute query based on type
        if query_type == "prometheus":
            data = prometheus_tool.query(
                promql=query_result["query"],
                time_range=query_result.get("time_range", "5m"),
            )
        elif query_type == "loki":
            data = loki_tool.query(
                logql=query_result["query"],
                time_range=query_result.get("time_range", "5m"),
            )
        else:
            data = None
        
        # Generate natural language response
        response = await query_generator.format_response(
            query=request.query,
            query_type=query_type,
            data=data,
        )
        
        logger.info(
            "query_processed",
            query_type=query_type,
        )
        
        return QueryResponse(
            response=response,
            query_type=query_type,
            data=data,
            timestamp=datetime.utcnow().isoformat(),
        )
    
    except Exception as e:
        logger.error(
            "query_processing_error",
            query=request.query,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/detect-issues", response_model=IssueDetectionResponse)
async def detect_issues(request: IssueDetectionRequest) -> IssueDetectionResponse:
    """
    Detect issues from metrics and logs.
    
    Analyzes:
    - High CPU/memory usage
    - Error rate spikes
    - Pod crashes (CrashLoopBackOff)
    - Slow response times
    
    Args:
        request: Issue detection request
    
    Returns:
        List of detected issues
    """
    if not issue_detector:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    logger.info(
        "issue_detection_started",
        time_range=request.time_range,
    )
    
    try:
        # Detect issues
        issues = await issue_detector.detect(
            time_range=request.time_range,
            severity_threshold=request.severity_threshold,
        )
        
        # Send notifications for critical issues
        if notification_handler:
            for issue in issues:
                if issue["severity"] in ["high", "critical"]:
                    await notification_handler.send_issue_notification(issue)
        
        logger.info(
            "issue_detection_complete",
            issues_found=len(issues),
        )
        
        return IssueDetectionResponse(
            issues=issues,
            timestamp=datetime.utcnow().isoformat(),
        )
    
    except Exception as e:
        logger.error(
            "issue_detection_error",
            error=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/create-dashboard", response_model=DashboardResponse)
async def create_dashboard(request: DashboardRequest) -> DashboardResponse:
    """
    Create Grafana dashboard.
    
    Args:
        request: Dashboard creation request
    
    Returns:
        Dashboard URL and ID
    """
    if not dashboard_generator:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    logger.info(
        "dashboard_creation_started",
        title=request.title,
    )
    
    try:
        # Create dashboard
        dashboard = await dashboard_generator.create(
            title=request.title,
            description=request.description,
            panels=request.panels,
        )
        
        logger.info(
            "dashboard_created",
            dashboard_id=dashboard["id"],
        )
        
        return DashboardResponse(
            dashboard_url=dashboard["url"],
            dashboard_id=dashboard["id"],
            timestamp=datetime.utcnow().isoformat(),
        )
    
    except Exception as e:
        logger.error(
            "dashboard_creation_error",
            error=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8081"))
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
    )


# Made with Bob