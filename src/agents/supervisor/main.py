"""
Supervisor Agent - AI-Powered Observability Platform

Main FastAPI server for the Supervisor Agent.
Routes user queries to specialist agents based on intent classification.

Port: 8080
Endpoints:
- POST /query - Process user query (REST)
- WebSocket /ws - Real-time query processing
- GET /health - Health check
"""

import os
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

import structlog
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents.common.llm_client import LLMClient
from agents.common.vector_store import VectorStore
from agents.supervisor.intent_classifier import IntentClassifier
from agents.supervisor.query_router import QueryRouter

logger = structlog.get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Supervisor Agent",
    description="Routes user queries to specialist agents",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
llm_client: Optional[LLMClient] = None
vector_store: Optional[VectorStore] = None
intent_classifier: Optional[IntentClassifier] = None
query_router: Optional[QueryRouter] = None


class QueryRequest(BaseModel):
    """Query request model"""
    query: str
    user_id: Optional[str] = "anonymous"
    session_id: Optional[str] = None


class QueryResponse(BaseModel):
    """Query response model"""
    response: str
    intent: str
    routed_to: str
    timestamp: str
    session_id: str


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    global llm_client, vector_store, intent_classifier, query_router
    
    logger.info("supervisor_agent_starting")
    
    # Initialize LLM client
    llm_client = LLMClient()
    
    # Initialize vector store
    vector_store = VectorStore(
        persist_directory="./supervisor_memory",
        collection_name="supervisor_conversations",
    )
    
    # Initialize intent classifier
    intent_classifier = IntentClassifier(llm_client=llm_client)
    
    # Initialize query router
    query_router = QueryRouter(
        llm_client=llm_client,
        vector_store=vector_store,
    )
    
    logger.info("supervisor_agent_started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("supervisor_agent_shutting_down")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "supervisor-agent",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest) -> QueryResponse:
    """
    Process user query via REST API.
    
    Args:
        request: Query request
    
    Returns:
        Query response with intent and routing info
    """
    if not intent_classifier or not query_router:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    logger.info(
        "query_received",
        query=request.query,
        user_id=request.user_id,
    )
    
    try:
        # Classify intent
        intent = await intent_classifier.classify(request.query)
        
        logger.info(
            "intent_classified",
            query=request.query,
            intent=intent,
        )
        
        # Route to specialist agent
        response = await query_router.route(
            query=request.query,
            intent=intent,
            user_id=request.user_id,
            session_id=request.session_id,
        )
        
        logger.info(
            "query_processed",
            intent=intent,
            routed_to=response["routed_to"],
        )
        
        return QueryResponse(
            response=response["response"],
            intent=intent,
            routed_to=response["routed_to"],
            timestamp=datetime.utcnow().isoformat(),
            session_id=response["session_id"],
        )
    
    except Exception as e:
        logger.error(
            "query_processing_error",
            query=request.query,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time query processing.
    
    Allows streaming responses and interactive conversations.
    """
    await websocket.accept()
    
    session_id = f"ws-{datetime.utcnow().timestamp()}"
    user_id = "websocket-user"
    
    logger.info(
        "websocket_connected",
        session_id=session_id,
    )
    
    try:
        while True:
            # Receive query
            data = await websocket.receive_json()
            query = data.get("query", "")
            
            if not query:
                await websocket.send_json({
                    "error": "Empty query",
                })
                continue
            
            logger.info(
                "websocket_query_received",
                query=query,
                session_id=session_id,
            )
            
            # Classify intent
            intent = await intent_classifier.classify(query)
            
            # Send intent classification
            await websocket.send_json({
                "type": "intent",
                "intent": intent,
            })
            
            # Route to specialist agent
            response = await query_router.route(
                query=query,
                intent=intent,
                user_id=user_id,
                session_id=session_id,
            )
            
            # Send response
            await websocket.send_json({
                "type": "response",
                "response": response["response"],
                "routed_to": response["routed_to"],
                "timestamp": datetime.utcnow().isoformat(),
            })
            
            logger.info(
                "websocket_query_processed",
                intent=intent,
                routed_to=response["routed_to"],
            )
    
    except WebSocketDisconnect:
        logger.info(
            "websocket_disconnected",
            session_id=session_id,
        )
    
    except Exception as e:
        logger.error(
            "websocket_error",
            session_id=session_id,
            error=str(e),
        )
        await websocket.close()


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8080"))
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
    )


# Made with Bob