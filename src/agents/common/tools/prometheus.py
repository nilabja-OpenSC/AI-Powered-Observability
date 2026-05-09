"""
Prometheus Tool for AI-Powered Observability Platform

Provides Prometheus/Thanos query operations:
- Execute PromQL queries
- Route to Prometheus (recent) or Thanos (historical)
- Automatic namespace filtering
- Query validation
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

import structlog
import requests

from ..namespace_guard import namespace_guard

logger = structlog.get_logger(__name__)


class PrometheusTool:
    """
    Prometheus/Thanos query tool with namespace enforcement.
    
    Automatically routes queries:
    - Prometheus: queries <6 hours (recent data)
    - Thanos: queries >6 hours (historical data)
    """
    
    def __init__(
        self,
        prometheus_url: Optional[str] = None,
        thanos_url: Optional[str] = None,
        thanos_threshold_hours: int = 6,
        timeout: int = 30,
    ):
        """
        Initialize Prometheus tool.
        
        Args:
            prometheus_url: Prometheus URL (default: from PROMETHEUS_URL env)
            thanos_url: Thanos URL (default: from THANOS_URL env)
            thanos_threshold_hours: Use Thanos for queries > this (default: 6)
            timeout: Query timeout in seconds
        """
        self.prometheus_url = prometheus_url or os.getenv(
            "PROMETHEUS_URL",
            "http://prometheus.nilabja-haldar-dev.svc.cluster.local:9090"
        )
        self.thanos_url = thanos_url or os.getenv(
            "THANOS_URL",
            "http://thanos-query.nilabja-haldar-dev.svc.cluster.local:9090"
        )
        self.thanos_threshold_hours = thanos_threshold_hours
        self.timeout = timeout
        
        logger.info(
            "prometheus_tool_initialized",
            prometheus_url=self.prometheus_url,
            thanos_url=self.thanos_url,
            thanos_threshold_hours=self.thanos_threshold_hours,
        )
    
    def query(
        self,
        promql: str,
        time: Optional[str] = None,
        add_namespace_filter: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute instant PromQL query.
        
        Args:
            promql: PromQL query
            time: Query time (RFC3339 or Unix timestamp)
            add_namespace_filter: Add namespace filter (default: True)
        
        Returns:
            Query result dict
        """
        # Add namespace filter if requested
        if add_namespace_filter:
            promql = namespace_guard.add_namespace_filter(promql)
        
        # Use Prometheus for instant queries
        url = f"{self.prometheus_url}/api/v1/query"
        
        params = {"query": promql}
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
                "prometheus_query_success",
                query_length=len(promql),
                result_type=result.get("data", {}).get("resultType"),
            )
            
            return result
        
        except requests.RequestException as e:
            logger.error(
                "prometheus_query_error",
                query=promql[:100],
                error=str(e),
            )
            raise
    
    def query_range(
        self,
        promql: str,
        start: str,
        end: str,
        step: str = "15s",
        add_namespace_filter: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute range PromQL query.
        
        Args:
            promql: PromQL query
            start: Start time (RFC3339 or Unix timestamp)
            end: End time (RFC3339 or Unix timestamp)
            step: Query resolution step (e.g., "15s", "1m")
            add_namespace_filter: Add namespace filter (default: True)
        
        Returns:
            Query result dict
        """
        # Add namespace filter if requested
        if add_namespace_filter:
            promql = namespace_guard.add_namespace_filter(promql)
        
        # Determine if we should use Thanos based on time range
        use_thanos = self._should_use_thanos(start, end)
        
        base_url = self.thanos_url if use_thanos else self.prometheus_url
        url = f"{base_url}/api/v1/query_range"
        
        params = {
            "query": promql,
            "start": start,
            "end": end,
            "step": step,
        }
        
        try:
            response = requests.get(
                url,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            
            result = response.json()
            
            logger.info(
                "prometheus_range_query_success",
                query_length=len(promql),
                data_source="thanos" if use_thanos else "prometheus",
                result_type=result.get("data", {}).get("resultType"),
            )
            
            return result
        
        except requests.RequestException as e:
            logger.error(
                "prometheus_range_query_error",
                query=promql[:100],
                data_source="thanos" if use_thanos else "prometheus",
                error=str(e),
            )
            raise
    
    def query_labels(
        self,
        label: Optional[str] = None,
        match: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Get label names or values.
        
        Args:
            label: Label name (if None, returns all label names)
            match: Series selectors to filter (optional)
        
        Returns:
            List of label names or values
        """
        if label:
            url = f"{self.prometheus_url}/api/v1/label/{label}/values"
        else:
            url = f"{self.prometheus_url}/api/v1/labels"
        
        params = {}
        if match:
            params["match[]"] = match
        
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
                "prometheus_labels_error",
                label=label,
                error=str(e),
            )
            raise
    
    def query_series(
        self,
        match: List[str],
        start: Optional[str] = None,
        end: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """
        Get time series matching selectors.
        
        Args:
            match: Series selectors (e.g., ["up", "process_start_time_seconds"])
            start: Start time (optional)
            end: End time (optional)
        
        Returns:
            List of series label sets
        """
        url = f"{self.prometheus_url}/api/v1/series"
        
        params = {"match[]": match}
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
                "prometheus_series_error",
                match=match,
                error=str(e),
            )
            raise
    
    def _should_use_thanos(self, start: str, end: str) -> bool:
        """
        Determine if query should use Thanos based on time range.
        
        Args:
            start: Start time
            end: End time
        
        Returns:
            True if should use Thanos
        """
        try:
            # Parse timestamps (handle both RFC3339 and Unix timestamps)
            if isinstance(start, str) and start.isdigit():
                start_dt = datetime.fromtimestamp(int(start))
            else:
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
            
            if isinstance(end, str) and end.isdigit():
                end_dt = datetime.fromtimestamp(int(end))
            else:
                end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
            
            # Calculate time range
            time_range = end_dt - start_dt
            
            # Use Thanos if range > threshold
            threshold = timedelta(hours=self.thanos_threshold_hours)
            
            return time_range > threshold
        
        except Exception as e:
            logger.warning(
                "time_range_parse_error",
                start=start,
                end=end,
                error=str(e),
            )
            # Default to Prometheus on error
            return False


# Made with Bob