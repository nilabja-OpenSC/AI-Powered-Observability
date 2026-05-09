"""
Loki Tool for AI-Powered Observability Platform

Provides Loki log query operations:
- Execute LogQL queries
- Automatic namespace filtering
- Query validation
- Log streaming support
"""

import os
from typing import Dict, Any, Optional, List

import structlog
import requests

from ..namespace_guard import namespace_guard

logger = structlog.get_logger(__name__)


class LokiTool:
    """
    Loki log query tool with namespace enforcement.
    
    Automatically adds namespace filter to all queries.
    """
    
    def __init__(
        self,
        loki_url: Optional[str] = None,
        timeout: int = 30,
        max_lines: int = 1000,
    ):
        """
        Initialize Loki tool.
        
        Args:
            loki_url: Loki URL (default: from LOKI_URL env)
            timeout: Query timeout in seconds
            max_lines: Maximum lines to return
        """
        self.loki_url = loki_url or os.getenv(
            "LOKI_URL",
            "http://loki.nilabja-haldar-dev.svc.cluster.local:3100"
        )
        self.timeout = timeout
        self.max_lines = max_lines
        
        logger.info(
            "loki_tool_initialized",
            loki_url=self.loki_url,
            max_lines=self.max_lines,
        )
    
    def query(
        self,
        logql: str,
        time: Optional[str] = None,
        limit: Optional[int] = None,
        add_namespace_filter: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute instant LogQL query.
        
        Args:
            logql: LogQL query
            time: Query time (RFC3339 or Unix timestamp)
            limit: Max entries to return
            add_namespace_filter: Add namespace filter (default: True)
        
        Returns:
            Query result dict
        """
        # Add namespace filter if requested
        if add_namespace_filter:
            logql = self._add_namespace_filter(logql)
        
        url = f"{self.loki_url}/loki/api/v1/query"
        
        params = {
            "query": logql,
            "limit": limit or self.max_lines,
        }
        if time:
            params["time"] = time
        
        try:
            response = requests.get(
                url,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            
            result = response.json()
            
            logger.info(
                "loki_query_success",
                query_length=len(logql),
                result_type=result.get("data", {}).get("resultType"),
            )
            
            return result
        
        except requests.RequestException as e:
            logger.error(
                "loki_query_error",
                query=logql[:100],
                error=str(e),
            )
            raise
    
    def query_range(
        self,
        logql: str,
        start: str,
        end: str,
        limit: Optional[int] = None,
        step: Optional[str] = None,
        add_namespace_filter: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute range LogQL query.
        
        Args:
            logql: LogQL query
            start: Start time (RFC3339 or Unix timestamp)
            end: End time (RFC3339 or Unix timestamp)
            limit: Max entries to return
            step: Query resolution step (for metric queries)
            add_namespace_filter: Add namespace filter (default: True)
        
        Returns:
            Query result dict
        """
        # Add namespace filter if requested
        if add_namespace_filter:
            logql = self._add_namespace_filter(logql)
        
        url = f"{self.loki_url}/loki/api/v1/query_range"
        
        params = {
            "query": logql,
            "start": start,
            "end": end,
            "limit": limit or self.max_lines,
        }
        if step:
            params["step"] = step
        
        try:
            response = requests.get(
                url,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            
            result = response.json()
            
            logger.info(
                "loki_range_query_success",
                query_length=len(logql),
                result_type=result.get("data", {}).get("resultType"),
            )
            
            return result
        
        except requests.RequestException as e:
            logger.error(
                "loki_range_query_error",
                query=logql[:100],
                error=str(e),
            )
            raise
    
    def query_labels(
        self,
        start: Optional[str] = None,
        end: Optional[str] = None,
    ) -> List[str]:
        """
        Get label names.
        
        Args:
            start: Start time (optional)
            end: End time (optional)
        
        Returns:
            List of label names
        """
        url = f"{self.loki_url}/loki/api/v1/labels"
        
        params = {}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        
        try:
            response = requests.get(
                url,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            
            result = response.json()
            
            return result.get("data", [])
        
        except requests.RequestException as e:
            logger.error(
                "loki_labels_error",
                error=str(e),
            )
            raise
    
    def query_label_values(
        self,
        label: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
    ) -> List[str]:
        """
        Get label values for a specific label.
        
        Args:
            label: Label name
            start: Start time (optional)
            end: End time (optional)
        
        Returns:
            List of label values
        """
        url = f"{self.loki_url}/loki/api/v1/label/{label}/values"
        
        params = {}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        
        try:
            response = requests.get(
                url,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            
            result = response.json()
            
            return result.get("data", [])
        
        except requests.RequestException as e:
            logger.error(
                "loki_label_values_error",
                label=label,
                error=str(e),
            )
            raise
    
    def _add_namespace_filter(self, logql: str) -> str:
        """
        Add namespace filter to LogQL query.
        
        Args:
            logql: Original LogQL query
        
        Returns:
            LogQL query with namespace filter
        """
        namespace = namespace_guard.get_allowed_namespace()
        namespace_filter = f'namespace="{namespace}"'
        
        # Check if query already has namespace filter
        if 'namespace=' in logql:
            logger.warning(
                "logql_already_has_namespace_filter",
                query=logql[:100],
            )
            return logql
        
        # Add namespace filter to log stream selector
        if '{' in logql:
            # Query has existing filters
            logql = logql.replace('{', f'{{{namespace_filter},', 1)
        else:
            # Query has no filters - add after stream selector
            # Example: {app="backend"} → {namespace="...",app="backend"}
            if logql.startswith('{'):
                logql = f'{{{namespace_filter},{logql[1:]}'
            else:
                # No stream selector at all - add one
                logql = f'{{{namespace_filter}}} {logql}'
        
        logger.info(
            "namespace_filter_added_to_logql",
            original_query=logql[:50],
        )
        
        return logql


# Made with Bob