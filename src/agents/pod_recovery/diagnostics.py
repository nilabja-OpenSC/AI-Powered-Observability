"""
Diagnostics for Pod Recovery Agent

Performs deep diagnostics on pods to identify root causes of issues.
Analyzes logs, events, resource usage, and configuration.
"""

from typing import Dict, Any, List
from datetime import datetime

import structlog

from agents.common.llm_client import LLMClient
from agents.common.tools.kubernetes import KubernetesTool

logger = structlog.get_logger(__name__)


class Diagnostics:
    """
    Performs pod diagnostics to identify issues.
    
    Uses LLM to analyze logs and events for root cause.
    """
    
    def __init__(
        self,
        k8s_tool: KubernetesTool,
        llm_client: LLMClient,
    ):
        """
        Initialize diagnostics.
        
        Args:
            k8s_tool: Kubernetes tool
            llm_client: LLM client for analysis
        """
        self.k8s_tool = k8s_tool
        self.llm_client = llm_client
        
        logger.info("diagnostics_initialized")
    
    async def diagnose(
        self,
        pod_name: str,
        namespace: str = "nilabja-haldar-dev",
    ) -> Dict[str, Any]:
        """
        Diagnose pod issues.
        
        Args:
            pod_name: Pod name
            namespace: Kubernetes namespace
        
        Returns:
            Diagnosis results
        """
        logger.info(
            "diagnosis_started",
            pod_name=pod_name,
            namespace=namespace,
        )
        
        try:
            # Get pod info
            pods = self.k8s_tool.list_pods(namespace=namespace)
            pod = next((p for p in pods if p["name"] == pod_name), None)
            
            if not pod:
                return {
                    "found": False,
                    "message": f"Pod {pod_name} not found",
                }
            
            # Collect diagnostic data
            logs = await self._get_logs(pod_name, namespace)
            events = await self._get_events(pod_name, namespace)
            status = pod.get("status", "Unknown")
            restarts = pod.get("restarts", 0)
            
            # Analyze issues
            issues = await self._analyze_issues(
                pod_name=pod_name,
                status=status,
                restarts=restarts,
                logs=logs,
                events=events,
            )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                pod_name=pod_name,
                issues=issues,
            )
            
            logger.info(
                "diagnosis_complete",
                pod_name=pod_name,
                issues_found=len(issues),
            )
            
            return {
                "found": True,
                "pod_name": pod_name,
                "status": status,
                "restarts": restarts,
                "issues": issues,
                "recommendations": recommendations,
                "timestamp": datetime.utcnow().isoformat(),
            }
        
        except Exception as e:
            logger.error(
                "diagnosis_error",
                pod_name=pod_name,
                error=str(e),
            )
            raise
    
    async def _get_logs(
        self,
        pod_name: str,
        namespace: str,
    ) -> str:
        """
        Get pod logs.
        
        Args:
            pod_name: Pod name
            namespace: Kubernetes namespace
        
        Returns:
            Pod logs
        """
        try:
            logs = self.k8s_tool.get_pod_logs(
                pod_name=pod_name,
                namespace=namespace,
                tail_lines=100,
            )
            return logs
        except Exception as e:
            logger.warning(
                "log_retrieval_error",
                pod_name=pod_name,
                error=str(e),
            )
            return ""
    
    async def _get_events(
        self,
        pod_name: str,
        namespace: str,
    ) -> List[str]:
        """
        Get pod events.
        
        Args:
            pod_name: Pod name
            namespace: Kubernetes namespace
        
        Returns:
            List of event messages
        """
        # Note: This is a simplified version
        # In production, would use k8s API to get actual events
        return [
            "Pod events would be retrieved from Kubernetes API",
        ]
    
    async def _analyze_issues(
        self,
        pod_name: str,
        status: str,
        restarts: int,
        logs: str,
        events: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Analyze pod issues using LLM.
        
        Args:
            pod_name: Pod name
            status: Pod status
            restarts: Restart count
            logs: Pod logs
            events: Pod events
        
        Returns:
            List of issues
        """
        issues = []
        
        # Check status-based issues
        if status == "CrashLoopBackOff":
            issues.append({
                "type": "crash_loop",
                "severity": "critical",
                "description": "Pod is in CrashLoopBackOff state",
                "details": "Container is crashing repeatedly",
            })
        
        elif status in ["ImagePullBackOff", "ErrImagePull"]:
            issues.append({
                "type": "image_pull_error",
                "severity": "high",
                "description": "Cannot pull container image",
                "details": "Check image name and registry credentials",
            })
        
        elif status == "Pending":
            issues.append({
                "type": "pending",
                "severity": "medium",
                "description": "Pod is stuck in Pending state",
                "details": "May be waiting for resources or node scheduling",
            })
        
        # Check restart count
        if restarts > 10:
            issues.append({
                "type": "high_restarts",
                "severity": "high",
                "description": f"High restart count: {restarts}",
                "details": "Pod is restarting frequently",
            })
        
        # Analyze logs for errors
        if logs:
            log_issues = await self._analyze_logs(logs)
            issues.extend(log_issues)
        
        return issues
    
    async def _analyze_logs(self, logs: str) -> List[Dict[str, Any]]:
        """
        Analyze logs for issues using LLM.
        
        Args:
            logs: Pod logs
        
        Returns:
            List of log-based issues
        """
        # Count error patterns
        error_count = logs.lower().count("error")
        exception_count = logs.lower().count("exception")
        fatal_count = logs.lower().count("fatal")
        
        issues = []
        
        if error_count > 5:
            issues.append({
                "type": "log_errors",
                "severity": "medium",
                "description": f"High error count in logs: {error_count}",
                "details": "Multiple errors detected in application logs",
            })
        
        if exception_count > 0:
            issues.append({
                "type": "exceptions",
                "severity": "high",
                "description": f"Exceptions found in logs: {exception_count}",
                "details": "Application is throwing exceptions",
            })
        
        if fatal_count > 0:
            issues.append({
                "type": "fatal_errors",
                "severity": "critical",
                "description": f"Fatal errors in logs: {fatal_count}",
                "details": "Application encountered fatal errors",
            })
        
        # Use LLM for deeper analysis if significant issues
        if error_count > 10 or exception_count > 3:
            llm_analysis = await self._llm_log_analysis(logs[:2000])  # Limit log size
            if llm_analysis:
                issues.append(llm_analysis)
        
        return issues
    
    async def _llm_log_analysis(self, logs: str) -> Dict[str, Any]:
        """
        Use LLM to analyze logs.
        
        Args:
            logs: Pod logs (truncated)
        
        Returns:
            Issue dict or None
        """
        prompt = f"""Analyze these application logs and identify the root cause of issues.

Logs:
{logs}

Provide:
1. Root cause (1-2 sentences)
2. Severity (low, medium, high, critical)

Format:
Root Cause: [description]
Severity: [level]"""
        
        try:
            response = self.llm_client.generate(
                prompt=prompt,
                max_tokens=200,
                temperature=0.3,
            )
            
            # Parse response
            lines = response.strip().split("\n")
            root_cause = ""
            severity = "medium"
            
            for line in lines:
                if line.startswith("Root Cause:"):
                    root_cause = line.split(":", 1)[1].strip()
                elif line.startswith("Severity:"):
                    severity = line.split(":", 1)[1].strip().lower()
            
            if root_cause:
                return {
                    "type": "llm_analysis",
                    "severity": severity,
                    "description": "LLM-identified issue",
                    "details": root_cause,
                }
        
        except Exception as e:
            logger.warning(
                "llm_log_analysis_error",
                error=str(e),
            )
        
        return None
    
    async def _generate_recommendations(
        self,
        pod_name: str,
        issues: List[Dict[str, Any]],
    ) -> List[str]:
        """
        Generate recommendations based on issues.
        
        Args:
            pod_name: Pod name
            issues: List of issues
        
        Returns:
            List of recommendations
        """
        if not issues:
            return ["No issues detected. Pod appears healthy."]
        
        recommendations = []
        
        # Generate recommendations based on issue types
        issue_types = [issue["type"] for issue in issues]
        
        if "crash_loop" in issue_types:
            recommendations.extend([
                "Check application logs for crash reason",
                "Verify environment variables and configuration",
                "Consider increasing resource limits",
                "Review recent code changes",
            ])
        
        if "image_pull_error" in issue_types:
            recommendations.extend([
                "Verify image name and tag",
                "Check registry credentials",
                "Ensure image exists in registry",
            ])
        
        if "high_restarts" in issue_types:
            recommendations.extend([
                "Investigate why pod is restarting",
                "Check liveness/readiness probes",
                "Review resource limits",
            ])
        
        if "log_errors" in issue_types or "exceptions" in issue_types:
            recommendations.extend([
                "Review application logs for error details",
                "Check for missing dependencies",
                "Verify database/service connections",
            ])
        
        # Use LLM for additional recommendations
        if len(issues) > 2:
            llm_recommendations = await self._llm_recommendations(pod_name, issues)
            if llm_recommendations:
                recommendations.extend(llm_recommendations)
        
        return recommendations[:10]  # Limit to 10 recommendations
    
    async def _llm_recommendations(
        self,
        pod_name: str,
        issues: List[Dict[str, Any]],
    ) -> List[str]:
        """
        Generate recommendations using LLM.
        
        Args:
            pod_name: Pod name
            issues: List of issues
        
        Returns:
            List of recommendations
        """
        issues_summary = "\n".join([
            f"- {issue['type']}: {issue['description']}"
            for issue in issues
        ])
        
        prompt = f"""You are a Kubernetes expert. Provide 3-5 specific recommendations to fix these pod issues.

Pod: {pod_name}
Issues:
{issues_summary}

Recommendations:"""
        
        try:
            response = self.llm_client.generate(
                prompt=prompt,
                max_tokens=300,
                temperature=0.7,
            )
            
            # Parse recommendations
            recommendations = []
            for line in response.strip().split("\n"):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith("-")):
                    rec = line.lstrip("0123456789.-) ")
                    if rec:
                        recommendations.append(rec)
            
            return recommendations
        
        except Exception as e:
            logger.warning(
                "llm_recommendations_error",
                error=str(e),
            )
            return []


# Made with Bob