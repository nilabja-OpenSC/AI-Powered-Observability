"""
Intent Classifier for Supervisor Agent

Classifies user queries into intents to route to appropriate specialist agents.

Intents:
- observability_query: Metrics, logs, dashboards (route to Observability Agent)
- pod_recovery: Pod issues, restarts, diagnostics (route to Pod Recovery Agent)
- backup_restore: Backup/restore operations (route to Backup/Restore Agent)
- general: General questions, help (handle locally)
"""

from typing import Dict, Any, Optional
from enum import Enum

import structlog

from agents.common.llm_client import LLMClient

logger = structlog.get_logger(__name__)


class Intent(str, Enum):
    """Query intent types"""
    OBSERVABILITY_QUERY = "observability_query"
    POD_RECOVERY = "pod_recovery"
    BACKUP_RESTORE = "backup_restore"
    GENERAL = "general"


class IntentClassifier:
    """
    Classifies user queries into intents using LLM.
    
    Uses few-shot prompting to classify queries accurately.
    """
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize intent classifier.
        
        Args:
            llm_client: LLM client for classification
        """
        self.llm_client = llm_client
        
        # Few-shot examples for intent classification
        self.examples = [
            {
                "query": "Show me CPU usage for backend pods",
                "intent": Intent.OBSERVABILITY_QUERY,
                "reasoning": "Query about metrics (CPU usage)",
            },
            {
                "query": "What are the error logs from frontend service?",
                "intent": Intent.OBSERVABILITY_QUERY,
                "reasoning": "Query about logs",
            },
            {
                "query": "Create a dashboard for HTTP request latency",
                "intent": Intent.OBSERVABILITY_QUERY,
                "reasoning": "Dashboard creation request",
            },
            {
                "query": "Why is the backend pod crashing?",
                "intent": Intent.POD_RECOVERY,
                "reasoning": "Pod issue diagnosis",
            },
            {
                "query": "Restart the frontend deployment",
                "intent": Intent.POD_RECOVERY,
                "reasoning": "Pod restart action",
            },
            {
                "query": "Check pod health status",
                "intent": Intent.POD_RECOVERY,
                "reasoning": "Pod health check",
            },
            {
                "query": "Backup the PostgreSQL database",
                "intent": Intent.BACKUP_RESTORE,
                "reasoning": "Backup operation",
            },
            {
                "query": "Restore from yesterday's backup",
                "intent": Intent.BACKUP_RESTORE,
                "reasoning": "Restore operation",
            },
            {
                "query": "List available backups",
                "intent": Intent.BACKUP_RESTORE,
                "reasoning": "Backup listing",
            },
            {
                "query": "What can you help me with?",
                "intent": Intent.GENERAL,
                "reasoning": "General help request",
            },
            {
                "query": "Explain how the observability platform works",
                "intent": Intent.GENERAL,
                "reasoning": "General explanation",
            },
        ]
        
        logger.info("intent_classifier_initialized")
    
    async def classify(self, query: str) -> str:
        """
        Classify user query into intent.
        
        Args:
            query: User query
        
        Returns:
            Intent string (observability_query, pod_recovery, backup_restore, general)
        """
        # Build few-shot prompt
        examples_text = "\n\n".join([
            f"Query: {ex['query']}\nIntent: {ex['intent'].value}\nReasoning: {ex['reasoning']}"
            for ex in self.examples
        ])
        
        prompt = f"""You are an intent classifier for an AI-powered observability platform.

Classify the following user query into one of these intents:
- observability_query: Queries about metrics, logs, dashboards, alerts
- pod_recovery: Queries about pod issues, restarts, diagnostics, health checks
- backup_restore: Queries about backup/restore operations
- general: General questions, help requests, explanations

Examples:
{examples_text}

Now classify this query:
Query: {query}
Intent:"""
        
        try:
            # Get classification from LLM
            response = await self.llm_client.generate(
                prompt=prompt,
                max_tokens=50,
                temperature=0.0,  # Deterministic classification
            )
            
            # Extract intent from response
            intent_text = response.strip().lower()
            
            # Map to Intent enum
            if "observability" in intent_text or "metric" in intent_text or "log" in intent_text or "dashboard" in intent_text:
                intent = Intent.OBSERVABILITY_QUERY
            elif "pod" in intent_text or "recovery" in intent_text or "restart" in intent_text:
                intent = Intent.POD_RECOVERY
            elif "backup" in intent_text or "restore" in intent_text:
                intent = Intent.BACKUP_RESTORE
            else:
                intent = Intent.GENERAL
            
            logger.info(
                "intent_classified",
                query=query,
                intent=intent.value,
                raw_response=intent_text,
            )
            
            return intent.value
        
        except Exception as e:
            logger.error(
                "intent_classification_error",
                query=query,
                error=str(e),
            )
            # Default to general on error
            return Intent.GENERAL.value
    
    def get_intent_description(self, intent: str) -> str:
        """
        Get human-readable description of intent.
        
        Args:
            intent: Intent string
        
        Returns:
            Description of intent
        """
        descriptions = {
            Intent.OBSERVABILITY_QUERY.value: "Observability query (metrics, logs, dashboards)",
            Intent.POD_RECOVERY.value: "Pod recovery (diagnostics, restarts, health checks)",
            Intent.BACKUP_RESTORE.value: "Backup/restore operations",
            Intent.GENERAL.value: "General question or help request",
        }
        
        return descriptions.get(intent, "Unknown intent")


# Made with Bob