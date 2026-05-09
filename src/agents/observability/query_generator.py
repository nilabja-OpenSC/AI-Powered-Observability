"""
Query Generator for Observability Agent

Generates PromQL and LogQL queries from natural language.
Formats query results into natural language responses.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta

import structlog

from agents.common.llm_client import LLMClient
from agents.common.namespace_guard import NamespaceGuard

logger = structlog.get_logger(__name__)

# Initialize namespace guard
namespace_guard = NamespaceGuard()


class QueryGenerator:
    """
    Generates PromQL/LogQL queries from natural language.
    
    Uses LLM to understand user intent and generate appropriate queries.
    """
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize query generator.
        
        Args:
            llm_client: LLM client for query generation
        """
        self.llm_client = llm_client
        
        # Query examples for few-shot prompting
        self.examples = [
            {
                "query": "Show me CPU usage for backend pods",
                "type": "prometheus",
                "promql": 'rate(container_cpu_usage_seconds_total{namespace="nilabja-haldar-dev",pod=~"backend-.*"}[5m])',
                "time_range": "5m",
            },
            {
                "query": "What's the memory usage of frontend pods?",
                "type": "prometheus",
                "promql": 'container_memory_usage_bytes{namespace="nilabja-haldar-dev",pod=~"frontend-.*"}',
                "time_range": "5m",
            },
            {
                "query": "Show HTTP request rate for backend service",
                "type": "prometheus",
                "promql": 'rate(http_requests_total{namespace="nilabja-haldar-dev",service="backend"}[5m])',
                "time_range": "5m",
            },
            {
                "query": "Show error logs from backend pods",
                "type": "loki",
                "logql": '{namespace="nilabja-haldar-dev",app="backend"} |= "error" or "ERROR"',
                "time_range": "5m",
            },
            {
                "query": "Get logs from frontend pods in the last hour",
                "type": "loki",
                "logql": '{namespace="nilabja-haldar-dev",app="frontend"}',
                "time_range": "1h",
            },
        ]
        
        logger.info("query_generator_initialized")
    
    async def generate(
        self,
        query: str,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate PromQL or LogQL query from natural language.
        
        Args:
            query: Natural language query
            context: Conversation context (optional)
        
        Returns:
            Dict with type, query, time_range
        """
        # Build few-shot prompt
        examples_text = "\n\n".join([
            f"Query: {ex['query']}\nType: {ex['type']}\n{ex['type'].upper()}: {ex[ex['type']]}\nTime Range: {ex['time_range']}"
            for ex in self.examples
        ])
        
        prompt = f"""You are an expert in Prometheus (PromQL) and Loki (LogQL) queries.

Generate a query for the following natural language request.

IMPORTANT: ALL queries MUST include namespace="nilabja-haldar-dev" filter.

Examples:
{examples_text}

Context:
{context if context else "No previous context"}

User Query: {query}

Generate the query in this format:
Type: [prometheus or loki]
Query: [PromQL or LogQL query]
Time Range: [e.g., 5m, 1h, 24h]"""
        
        try:
            # Generate query
            response = self.llm_client.generate(
                prompt=prompt,
                max_tokens=300,
                temperature=0.0,  # Deterministic query generation
            )
            
            # Parse response
            lines = response.strip().split("\n")
            query_type = None
            generated_query = None
            time_range = "5m"
            
            for line in lines:
                if line.startswith("Type:"):
                    query_type = line.split(":", 1)[1].strip().lower()
                elif line.startswith("Query:"):
                    generated_query = line.split(":", 1)[1].strip()
                elif line.startswith("Time Range:"):
                    time_range = line.split(":", 1)[1].strip()
            
            # Validate query type
            if query_type not in ["prometheus", "loki"]:
                query_type = "prometheus"  # Default to Prometheus
            
            # Ensure namespace filter is present
            if generated_query:
                generated_query = namespace_guard.add_namespace_filter(
                    generated_query,
                    query_type,
                )
            
            logger.info(
                "query_generated",
                query=query,
                type=query_type,
                generated_query=generated_query,
            )
            
            return {
                "type": query_type,
                "query": generated_query,
                "time_range": time_range,
            }
        
        except Exception as e:
            logger.error(
                "query_generation_error",
                query=query,
                error=str(e),
            )
            # Return default query on error
            return {
                "type": "prometheus",
                "query": f'up{{namespace="nilabja-haldar-dev"}}',
                "time_range": "5m",
            }
    
    async def format_response(
        self,
        query: str,
        query_type: str,
        data: Optional[Dict[str, Any]],
    ) -> str:
        """
        Format query results into natural language response.
        
        Args:
            query: Original user query
            query_type: Type of query (prometheus/loki)
            data: Query results
        
        Returns:
            Natural language response
        """
        if not data:
            return "No data found for your query."
        
        # Build prompt for response formatting
        prompt = f"""You are a helpful assistant explaining observability data.

User Query: {query}
Query Type: {query_type}

Data:
{str(data)[:1000]}  # Limit data size

Provide a clear, concise explanation of the data in natural language.
Focus on key insights and trends.
If there are issues or anomalies, highlight them."""
        
        try:
            response = self.llm_client.generate(
                prompt=prompt,
                max_tokens=500,
                temperature=0.7,
            )
            
            return response
        
        except Exception as e:
            logger.error(
                "response_formatting_error",
                query=query,
                error=str(e),
            )
            return f"Query executed successfully. Data: {str(data)[:200]}..."
    
    def parse_time_range(self, time_range: str) -> timedelta:
        """
        Parse time range string to timedelta.
        
        Args:
            time_range: Time range string (e.g., "5m", "1h", "24h")
        
        Returns:
            timedelta object
        """
        unit = time_range[-1]
        value = int(time_range[:-1])
        
        if unit == "s":
            return timedelta(seconds=value)
        elif unit == "m":
            return timedelta(minutes=value)
        elif unit == "h":
            return timedelta(hours=value)
        elif unit == "d":
            return timedelta(days=value)
        else:
            return timedelta(minutes=5)  # Default to 5 minutes


# Made with Bob