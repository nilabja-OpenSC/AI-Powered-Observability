"""
Issue Detector for Observability Agent

Detects issues from metrics and logs:
- High CPU/memory usage
- Error rate spikes
- Pod crashes (CrashLoopBackOff)
- Slow response times
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

import structlog

from agents.common.llm_client import LLMClient
from agents.common.tools.prometheus import PrometheusTool
from agents.common.tools.loki import LokiTool

logger = structlog.get_logger(__name__)


class IssueDetector:
    """
    Detects issues from observability data.
    
    Analyzes metrics and logs to identify problems.
    """
    
    def __init__(
        self,
        llm_client: LLMClient,
        prometheus_tool: PrometheusTool,
        loki_tool: LokiTool,
    ):
        """
        Initialize issue detector.
        
        Args:
            llm_client: LLM client for analysis
            prometheus_tool: Prometheus query tool
            loki_tool: Loki query tool
        """
        self.llm_client = llm_client
        self.prometheus_tool = prometheus_tool
        self.loki_tool = loki_tool
        
        # Issue detection queries
        self.detection_queries = {
            "high_cpu": {
                "query": 'rate(container_cpu_usage_seconds_total{namespace="nilabja-haldar-dev"}[5m]) > 0.8',
                "severity": "high",
                "description": "High CPU usage detected",
            },
            "high_memory": {
                "query": 'container_memory_usage_bytes{namespace="nilabja-haldar-dev"} / container_spec_memory_limit_bytes{namespace="nilabja-haldar-dev"} > 0.9',
                "severity": "high",
                "description": "High memory usage detected",
            },
            "pod_crashes": {
                "query": 'kube_pod_container_status_restarts_total{namespace="nilabja-haldar-dev"} > 5',
                "severity": "critical",
                "description": "Pod restart count exceeded threshold",
            },
            "error_rate": {
                "query": 'rate(http_requests_total{namespace="nilabja-haldar-dev",status=~"5.."}[5m]) > 0.1',
                "severity": "high",
                "description": "High error rate detected",
            },
            "slow_response": {
                "query": 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{namespace="nilabja-haldar-dev"}[5m])) > 1',
                "severity": "medium",
                "description": "Slow response times detected",
            },
        }
        
        logger.info("issue_detector_initialized")
    
    async def detect(
        self,
        time_range: str = "5m",
        severity_threshold: str = "medium",
    ) -> List[Dict[str, Any]]:
        """
        Detect issues from metrics and logs.
        
        Args:
            time_range: Time range to analyze
            severity_threshold: Minimum severity to report (low, medium, high, critical)
        
        Returns:
            List of detected issues
        """
        logger.info(
            "issue_detection_started",
            time_range=time_range,
            severity_threshold=severity_threshold,
        )
        
        issues = []
        
        # Run detection queries
        for issue_type, config in self.detection_queries.items():
            # Skip if below severity threshold
            if not self._meets_severity_threshold(
                config["severity"],
                severity_threshold,
            ):
                continue
            
            try:
                # Execute Prometheus query
                result = self.prometheus_tool.query(config["query"])
                
                if result and result.get("data", {}).get("result"):
                    # Issue detected
                    for metric in result["data"]["result"]:
                        issue = await self._create_issue(
                            issue_type=issue_type,
                            severity=config["severity"],
                            description=config["description"],
                            metric=metric,
                            time_range=time_range,
                        )
                        issues.append(issue)
            
            except Exception as e:
                logger.error(
                    "issue_detection_query_error",
                    issue_type=issue_type,
                    error=str(e),
                )
        
        # Analyze logs for errors
        log_issues = await self._detect_log_issues(time_range)
        issues.extend(log_issues)
        
        logger.info(
            "issue_detection_complete",
            issues_found=len(issues),
        )
        
        return issues
    
    async def _create_issue(
        self,
        issue_type: str,
        severity: str,
        description: str,
        metric: Dict[str, Any],
        time_range: str,
    ) -> Dict[str, Any]:
        """
        Create issue object with details.
        
        Args:
            issue_type: Type of issue
            severity: Severity level
            description: Issue description
            metric: Prometheus metric data
            time_range: Time range analyzed
        
        Returns:
            Issue dict
        """
        # Extract affected resource
        labels = metric.get("metric", {})
        pod = labels.get("pod", "unknown")
        container = labels.get("container", "unknown")
        
        # Get metric value
        value = metric.get("value", [None, None])[1]
        
        # Generate resolution steps using LLM
        resolution_steps = await self._generate_resolution_steps(
            issue_type=issue_type,
            severity=severity,
            description=description,
            affected_resource=f"{pod}/{container}",
            value=value,
        )
        
        return {
            "id": f"{issue_type}-{pod}-{datetime.utcnow().timestamp()}",
            "type": issue_type,
            "severity": severity,
            "summary": description,
            "affected_resources": [f"pod/{pod}", f"container/{container}"],
            "details": {
                "pod": pod,
                "container": container,
                "value": value,
                "time_range": time_range,
                "labels": labels,
            },
            "resolution_steps": resolution_steps,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def _generate_resolution_steps(
        self,
        issue_type: str,
        severity: str,
        description: str,
        affected_resource: str,
        value: Optional[str],
    ) -> List[str]:
        """
        Generate resolution steps using LLM.
        
        Args:
            issue_type: Type of issue
            severity: Severity level
            description: Issue description
            affected_resource: Affected resource
            value: Metric value
        
        Returns:
            List of resolution steps
        """
        prompt = f"""You are an expert in Kubernetes troubleshooting.

Issue Type: {issue_type}
Severity: {severity}
Description: {description}
Affected Resource: {affected_resource}
Current Value: {value}

Provide 3-5 specific resolution steps to address this issue.
Focus on actionable steps that can be automated or performed manually.

Resolution Steps:"""
        
        try:
            response = self.llm_client.generate(
                prompt=prompt,
                max_tokens=300,
                temperature=0.7,
            )
            
            # Parse steps from response
            steps = []
            for line in response.strip().split("\n"):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith("-")):
                    # Remove numbering/bullets
                    step = line.lstrip("0123456789.-) ")
                    if step:
                        steps.append(step)
            
            return steps if steps else [
                "Investigate the issue manually",
                "Check pod logs for errors",
                "Review resource limits and requests",
            ]
        
        except Exception as e:
            logger.error(
                "resolution_steps_generation_error",
                issue_type=issue_type,
                error=str(e),
            )
            return [
                "Investigate the issue manually",
                "Check pod logs for errors",
                "Review resource limits and requests",
            ]
    
    async def _detect_log_issues(
        self,
        time_range: str,
    ) -> List[Dict[str, Any]]:
        """
        Detect issues from logs.
        
        Args:
            time_range: Time range to analyze
        
        Returns:
            List of log-based issues
        """
        issues = []
        
        try:
            # Query for error logs
            logql = '{namespace="nilabja-haldar-dev"} |= "error" or "ERROR" or "exception" or "Exception"'
            result = self.loki_tool.query(logql)
            
            if result and result.get("data", {}).get("result"):
                # Analyze error patterns
                error_count = len(result["data"]["result"])
                
                if error_count > 10:  # Threshold for error spike
                    issue = {
                        "id": f"error-logs-{datetime.utcnow().timestamp()}",
                        "type": "error_logs",
                        "severity": "medium",
                        "summary": f"High error log volume detected ({error_count} errors)",
                        "affected_resources": ["logs"],
                        "details": {
                            "error_count": error_count,
                            "time_range": time_range,
                        },
                        "resolution_steps": [
                            "Review error logs for patterns",
                            "Identify root cause of errors",
                            "Apply fixes or rollback if needed",
                        ],
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                    issues.append(issue)
        
        except Exception as e:
            logger.error(
                "log_issue_detection_error",
                error=str(e),
            )
        
        return issues
    
    def _meets_severity_threshold(
        self,
        severity: str,
        threshold: str,
    ) -> bool:
        """
        Check if severity meets threshold.
        
        Args:
            severity: Issue severity
            threshold: Minimum severity threshold
        
        Returns:
            True if meets threshold
        """
        severity_levels = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4,
        }
        
        return severity_levels.get(severity, 0) >= severity_levels.get(threshold, 0)


# Made with Bob