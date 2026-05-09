"""
Query Router for Supervisor Agent

Routes user queries to appropriate specialist agents based on intent.

Specialist Agents:
- Observability Agent (port 8081): Metrics, logs, dashboards
- Pod Recovery Agent (port 8082): Pod diagnostics, restarts
- Backup/Restore Agent (port 8083): Backup/restore operations
"""

import os
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

import structlog
import httpx

from agents.common.llm_client import LLMClient
from agents.common.vector_store import VectorStore

logger = structlog.get_logger(__name__)


class QueryRouter:
    """
    Routes queries to specialist agents based on intent.
    
    Maintains conversation context using vector store.
    """
    
    def __init__(
        self,
        llm_client: LLMClient,
        vector_store: VectorStore,
    ):
        """
        Initialize query router.
        
        Args:
            llm_client: LLM client for generating responses
            vector_store: Vector store for conversation memory
        """
        self.llm_client = llm_client
        self.vector_store = vector_store
        
        # Specialist agent endpoints
        self.agent_endpoints = {
            "observability_query": os.getenv(
                "OBSERVABILITY_AGENT_URL",
                "http://observability-agent:8081"
            ),
            "pod_recovery": os.getenv(
                "POD_RECOVERY_AGENT_URL",
                "http://pod-recovery-agent:8082"
            ),
            "backup_restore": os.getenv(
                "BACKUP_RESTORE_AGENT_URL",
                "http://backup-restore-agent:8083"
            ),
        }
        
        logger.info(
            "query_router_initialized",
            agent_endpoints=self.agent_endpoints,
        )
    
    async def route(
        self,
        query: str,
        intent: str,
        user_id: str,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Route query to appropriate specialist agent.
        
        Args:
            query: User query
            intent: Classified intent
            user_id: User ID
            session_id: Session ID (optional)
        
        Returns:
            Response dict with response, routed_to, session_id
        """
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        logger.info(
            "routing_query",
            query=query,
            intent=intent,
            session_id=session_id,
        )
        
        # Retrieve conversation context
        context = await self._get_context(session_id)
        
        # Route based on intent
        if intent == "general":
            response = await self._handle_general_query(query, context)
            routed_to = "supervisor"
        else:
            response = await self._route_to_specialist(
                query=query,
                intent=intent,
                context=context,
            )
            routed_to = intent
        
        # Store conversation in vector store
        await self._store_conversation(
            session_id=session_id,
            user_id=user_id,
            query=query,
            response=response,
            intent=intent,
        )
        
        logger.info(
            "query_routed",
            intent=intent,
            routed_to=routed_to,
            session_id=session_id,
        )
        
        return {
            "response": response,
            "routed_to": routed_to,
            "session_id": session_id,
        }
    
    async def _get_context(self, session_id: str) -> str:
        """
        Retrieve conversation context from vector store.
        
        Args:
            session_id: Session ID
        
        Returns:
            Context string
        """
        try:
            # Query vector store for recent conversation
            results = self.vector_store.query(
                query_text=f"session:{session_id}",
                n_results=5,
            )
            
            if results and results["documents"]:
                context = "\n".join(results["documents"][0])
                return context
            
            return ""
        
        except Exception as e:
            logger.warning(
                "context_retrieval_error",
                session_id=session_id,
                error=str(e),
            )
            return ""
    
    async def _store_conversation(
        self,
        session_id: str,
        user_id: str,
        query: str,
        response: str,
        intent: str,
    ):
        """
        Store conversation in vector store.
        
        Args:
            session_id: Session ID
            user_id: User ID
            query: User query
            response: Agent response
            intent: Query intent
        """
        try:
            conversation_text = f"User: {query}\nAssistant: {response}"
            
            self.vector_store.add_documents(
                documents=[conversation_text],
                metadatas=[{
                    "session_id": session_id,
                    "user_id": user_id,
                    "intent": intent,
                    "timestamp": datetime.utcnow().isoformat(),
                }],
            )
            
            logger.debug(
                "conversation_stored",
                session_id=session_id,
            )
        
        except Exception as e:
            logger.warning(
                "conversation_storage_error",
                session_id=session_id,
                error=str(e),
            )
    
    async def _handle_general_query(
        self,
        query: str,
        context: str,
    ) -> str:
        """
        Handle general queries locally.
        
        Args:
            query: User query
            context: Conversation context
        
        Returns:
            Response string
        """
        prompt = f"""You are a helpful assistant for an AI-powered observability platform.

The platform provides:
- Observability: Metrics (Prometheus/Thanos), logs (Loki), dashboards (Grafana)
- Pod Recovery: Automated pod diagnostics and recovery
- Backup/Restore: Velero-based backup and restore operations

All operations are scoped to namespace: nilabja-haldar-dev

Context:
{context if context else "No previous conversation"}

User Query: {query}

Provide a helpful response:"""
        
        try:
            response = self.llm_client.generate(
                prompt=prompt,
                max_tokens=500,
                temperature=0.7,
            )
            
            return response
        
        except Exception as e:
            logger.error(
                "general_query_error",
                query=query,
                error=str(e),
            )
            return "I apologize, but I encountered an error processing your request. Please try again."
    
    async def _route_to_specialist(
        self,
        query: str,
        intent: str,
        context: str,
    ) -> str:
        """
        Route query to specialist agent.
        
        Args:
            query: User query
            intent: Query intent
            context: Conversation context
        
        Returns:
            Response from specialist agent
        """
        endpoint = self.agent_endpoints.get(intent)
        
        if not endpoint:
            logger.error(
                "unknown_intent",
                intent=intent,
            )
            return f"I don't know how to handle queries of type: {intent}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{endpoint}/query",
                    json={
                        "query": query,
                        "context": context,
                    },
                )
                
                response.raise_for_status()
                
                result = response.json()
                return result.get("response", "No response from specialist agent")
        
        except httpx.TimeoutException:
            logger.error(
                "specialist_agent_timeout",
                intent=intent,
                endpoint=endpoint,
            )
            return "The specialist agent is taking too long to respond. Please try again."
        
        except httpx.HTTPError as e:
            logger.error(
                "specialist_agent_error",
                intent=intent,
                endpoint=endpoint,
                error=str(e),
            )
            return f"Error communicating with specialist agent: {str(e)}"
        
        except Exception as e:
            logger.error(
                "routing_error",
                intent=intent,
                error=str(e),
            )
            return "An unexpected error occurred while routing your query."


# Made with Bob