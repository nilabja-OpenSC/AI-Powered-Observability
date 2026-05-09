"""
Health Monitor for Pod Recovery Agent

Monitors pod health across the namespace.
Detects unhealthy pods and provides health status.
"""

from typing import Dict, Any, List
from datetime import datetime

import structlog

from agents.common.llm_client import LLMClient
from agents.common.tools.kubernetes import KubernetesTool

logger = structlog.get_logger(__name__)


class HealthMonitor:
    """
    Monitors pod health in the namespace.
    
    Checks pod status, restarts, and resource usage.
    """
    
    def __init__(
        self,
        k8s_tool: KubernetesTool,
        llm_client: LLMClient,
    ):
        """
        Initialize health monitor.
        
        Args:
            k8s_tool: Kubernetes tool
            llm_client: LLM client for analysis
        """
        self.k8s_tool = k8s_tool
        self.llm_client = llm_client
        
        logger.info("health_monitor_initialized")
    
    async def check_all_pods(
        self,
        namespace: str = "nilabja-haldar-dev",
    ) -> Dict[str, Any]:
        """
        Check health of all pods in namespace.
        
        Args:
            namespace: Kubernetes namespace
        
        Returns:
            Health status dict
        """
        logger.info(
            "checking_all_pods",
            namespace=namespace,
        )
        
        try:
            # List all pods
            pods = self.k8s_tool.list_pods(namespace=namespace)
            
            healthy_pods = []
            unhealthy_pods = []
            
            for pod in pods:
                health_status = self._check_pod_health(pod)
                
                if health_status["healthy"]:
                    healthy_pods.append({
                        "name": pod["name"],
                        "status": health_status["status"],
                    })
                else:
                    unhealthy_pods.append({
                        "name": pod["name"],
                        "status": health_status["status"],
                        "issues": health_status["issues"],
                    })
            
            logger.info(
                "health_check_complete",
                total_pods=len(pods),
                healthy=len(healthy_pods),
                unhealthy=len(unhealthy_pods),
            )
            
            return {
                "total_pods": len(pods),
                "healthy_pods": healthy_pods,
                "unhealthy_pods": unhealthy_pods,
                "timestamp": datetime.utcnow().isoformat(),
            }
        
        except Exception as e:
            logger.error(
                "health_check_error",
                namespace=namespace,
                error=str(e),
            )
            raise
    
    def _check_pod_health(self, pod: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check health of a single pod.
        
        Args:
            pod: Pod info dict
        
        Returns:
            Health status dict
        """
        status = pod.get("status", "Unknown")
        restarts = pod.get("restarts", 0)
        
        issues = []
        healthy = True
        
        # Check pod status
        if status not in ["Running", "Succeeded"]:
            issues.append(f"Pod status is {status}")
            healthy = False
        
        # Check restart count
        if restarts > 5:
            issues.append(f"High restart count: {restarts}")
            healthy = False
        elif restarts > 0:
            issues.append(f"Pod has restarted {restarts} times")
        
        # Check for CrashLoopBackOff
        if "CrashLoopBackOff" in status:
            issues.append("Pod is in CrashLoopBackOff state")
            healthy = False
        
        # Check for ImagePullBackOff
        if "ImagePullBackOff" in status or "ErrImagePull" in status:
            issues.append("Image pull error")
            healthy = False
        
        return {
            "healthy": healthy,
            "status": status,
            "restarts": restarts,
            "issues": issues,
        }
    
    async def check_pod(
        self,
        pod_name: str,
        namespace: str = "nilabja-haldar-dev",
    ) -> Dict[str, Any]:
        """
        Check health of a specific pod.
        
        Args:
            pod_name: Pod name
            namespace: Kubernetes namespace
        
        Returns:
            Health status dict
        """
        logger.info(
            "checking_pod",
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
            
            # Check health
            health_status = self._check_pod_health(pod)
            
            # Get additional details
            details = await self._get_pod_details(pod_name, namespace)
            
            logger.info(
                "pod_health_checked",
                pod_name=pod_name,
                healthy=health_status["healthy"],
            )
            
            return {
                "found": True,
                "pod_name": pod_name,
                "healthy": health_status["healthy"],
                "status": health_status["status"],
                "restarts": health_status["restarts"],
                "issues": health_status["issues"],
                "details": details,
                "timestamp": datetime.utcnow().isoformat(),
            }
        
        except Exception as e:
            logger.error(
                "pod_health_check_error",
                pod_name=pod_name,
                error=str(e),
            )
            raise
    
    async def _get_pod_details(
        self,
        pod_name: str,
        namespace: str,
    ) -> Dict[str, Any]:
        """
        Get additional pod details.
        
        Args:
            pod_name: Pod name
            namespace: Kubernetes namespace
        
        Returns:
            Pod details dict
        """
        try:
            # Get pod logs (last 50 lines)
            logs = self.k8s_tool.get_pod_logs(
                pod_name=pod_name,
                namespace=namespace,
                tail_lines=50,
            )
            
            # Analyze logs for errors
            error_count = logs.count("error") + logs.count("ERROR")
            warning_count = logs.count("warning") + logs.count("WARNING")
            
            return {
                "log_error_count": error_count,
                "log_warning_count": warning_count,
                "has_errors": error_count > 0,
            }
        
        except Exception as e:
            logger.warning(
                "pod_details_error",
                pod_name=pod_name,
                error=str(e),
            )
            return {
                "log_error_count": 0,
                "log_warning_count": 0,
                "has_errors": False,
            }
    
    async def get_unhealthy_pods_summary(
        self,
        namespace: str = "nilabja-haldar-dev",
    ) -> str:
        """
        Get natural language summary of unhealthy pods.
        
        Args:
            namespace: Kubernetes namespace
        
        Returns:
            Summary string
        """
        result = await self.check_all_pods(namespace)
        
        if not result["unhealthy_pods"]:
            return "All pods are healthy."
        
        # Build summary
        summary_lines = [
            f"Found {len(result['unhealthy_pods'])} unhealthy pod(s):",
        ]
        
        for pod in result["unhealthy_pods"]:
            issues_str = ", ".join(pod["issues"])
            summary_lines.append(f"- {pod['name']}: {issues_str}")
        
        return "\n".join(summary_lines)


# Made with Bob