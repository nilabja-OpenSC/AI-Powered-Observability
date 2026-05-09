"""
Kubernetes Tool for AI-Powered Observability Platform

Provides Kubernetes operations with namespace enforcement:
- Get/list pods, deployments, statefulsets
- Delete pods (for restart)
- Scale deployments/statefulsets
- Get pod logs
- Get events

ALL operations are namespace-scoped to: nilabja-haldar-dev
"""

import os
from typing import List, Dict, Any, Optional

import structlog
from kubernetes import client, config
from kubernetes.client.rest import ApiException

from ..namespace_guard import namespace_guard, require_namespace

logger = structlog.get_logger(__name__)


class KubernetesTool:
    """
    Kubernetes operations tool with namespace enforcement.
    
    CRITICAL: All operations are scoped to allowed namespace only.
    """
    
    def __init__(self, namespace: Optional[str] = None):
        """
        Initialize Kubernetes tool.
        
        Args:
            namespace: Kubernetes namespace (default: from env or nilabja-haldar-dev)
        """
        self.namespace = namespace or namespace_guard.get_allowed_namespace()
        
        # Load Kubernetes config (in-cluster or kubeconfig)
        try:
            config.load_incluster_config()
            logger.info("kubernetes_config_loaded", mode="in-cluster")
        except config.ConfigException:
            config.load_kube_config()
            logger.info("kubernetes_config_loaded", mode="kubeconfig")
        
        # Initialize API clients
        self.core_v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        
        logger.info(
            "kubernetes_tool_initialized",
            namespace=self.namespace,
        )
    
    @require_namespace
    def list_pods(
        self,
        namespace: Optional[str] = None,
        label_selector: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List pods in namespace.
        
        Args:
            namespace: Namespace (enforced by decorator)
            label_selector: Label selector (e.g., "app=backend")
        
        Returns:
            List of pod dicts
        """
        namespace = namespace or self.namespace
        
        try:
            pods = self.core_v1.list_namespaced_pod(
                namespace=namespace,
                label_selector=label_selector,
            )
            
            result = []
            for pod in pods.items:
                result.append({
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "status": pod.status.phase,
                    "ready": self._is_pod_ready(pod),
                    "restarts": self._get_restart_count(pod),
                    "node": pod.spec.node_name,
                    "created": pod.metadata.creation_timestamp.isoformat(),
                })
            
            logger.info(
                "pods_listed",
                namespace=namespace,
                count=len(result),
            )
            
            return result
        
        except ApiException as e:
            logger.error(
                "list_pods_error",
                namespace=namespace,
                error=str(e),
            )
            raise
    
    @require_namespace
    def get_pod(
        self,
        pod_name: str,
        namespace: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Get pod details.
        
        Args:
            pod_name: Pod name
            namespace: Namespace (enforced by decorator)
        
        Returns:
            Pod dict or None if not found
        """
        namespace = namespace or self.namespace
        
        try:
            pod = self.core_v1.read_namespaced_pod(
                name=pod_name,
                namespace=namespace,
            )
            
            return {
                "name": pod.metadata.name,
                "namespace": pod.metadata.namespace,
                "status": pod.status.phase,
                "ready": self._is_pod_ready(pod),
                "restarts": self._get_restart_count(pod),
                "node": pod.spec.node_name,
                "created": pod.metadata.creation_timestamp.isoformat(),
                "containers": [c.name for c in pod.spec.containers],
            }
        
        except ApiException as e:
            if e.status == 404:
                logger.warning(
                    "pod_not_found",
                    pod_name=pod_name,
                    namespace=namespace,
                )
                return None
            logger.error(
                "get_pod_error",
                pod_name=pod_name,
                namespace=namespace,
                error=str(e),
            )
            raise
    
    @require_namespace
    def delete_pod(
        self,
        pod_name: str,
        namespace: Optional[str] = None,
    ) -> bool:
        """
        Delete pod (for restart).
        
        Args:
            pod_name: Pod name
            namespace: Namespace (enforced by decorator)
        
        Returns:
            True if deleted successfully
        """
        namespace = namespace or self.namespace
        
        try:
            self.core_v1.delete_namespaced_pod(
                name=pod_name,
                namespace=namespace,
            )
            
            logger.info(
                "pod_deleted",
                pod_name=pod_name,
                namespace=namespace,
            )
            
            return True
        
        except ApiException as e:
            logger.error(
                "delete_pod_error",
                pod_name=pod_name,
                namespace=namespace,
                error=str(e),
            )
            raise
    
    @require_namespace
    def get_pod_logs(
        self,
        pod_name: str,
        namespace: Optional[str] = None,
        container: Optional[str] = None,
        tail_lines: int = 100,
    ) -> str:
        """
        Get pod logs.
        
        Args:
            pod_name: Pod name
            namespace: Namespace (enforced by decorator)
            container: Container name (optional)
            tail_lines: Number of lines to tail
        
        Returns:
            Log content
        """
        namespace = namespace or self.namespace
        
        try:
            logs = self.core_v1.read_namespaced_pod_log(
                name=pod_name,
                namespace=namespace,
                container=container,
                tail_lines=tail_lines,
            )
            
            logger.info(
                "pod_logs_retrieved",
                pod_name=pod_name,
                namespace=namespace,
                lines=len(logs.split('\n')),
            )
            
            return logs
        
        except ApiException as e:
            logger.error(
                "get_pod_logs_error",
                pod_name=pod_name,
                namespace=namespace,
                error=str(e),
            )
            raise
    
    @require_namespace
    def scale_deployment(
        self,
        deployment_name: str,
        replicas: int,
        namespace: Optional[str] = None,
    ) -> bool:
        """
        Scale deployment.
        
        Args:
            deployment_name: Deployment name
            replicas: Target replica count
            namespace: Namespace (enforced by decorator)
        
        Returns:
            True if scaled successfully
        """
        namespace = namespace or self.namespace
        
        try:
            # Get current deployment
            deployment = self.apps_v1.read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace,
            )
            
            # Update replicas
            deployment.spec.replicas = replicas
            
            self.apps_v1.patch_namespaced_deployment(
                name=deployment_name,
                namespace=namespace,
                body=deployment,
            )
            
            logger.info(
                "deployment_scaled",
                deployment_name=deployment_name,
                namespace=namespace,
                replicas=replicas,
            )
            
            return True
        
        except ApiException as e:
            logger.error(
                "scale_deployment_error",
                deployment_name=deployment_name,
                namespace=namespace,
                error=str(e),
            )
            raise
    
    @require_namespace
    def get_events(
        self,
        namespace: Optional[str] = None,
        field_selector: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get events in namespace.
        
        Args:
            namespace: Namespace (enforced by decorator)
            field_selector: Field selector (e.g., "type=Warning")
        
        Returns:
            List of event dicts
        """
        namespace = namespace or self.namespace
        
        try:
            events = self.core_v1.list_namespaced_event(
                namespace=namespace,
                field_selector=field_selector,
            )
            
            result = []
            for event in events.items:
                result.append({
                    "type": event.type,
                    "reason": event.reason,
                    "message": event.message,
                    "object": f"{event.involved_object.kind}/{event.involved_object.name}",
                    "count": event.count,
                    "first_timestamp": event.first_timestamp.isoformat() if event.first_timestamp else None,
                    "last_timestamp": event.last_timestamp.isoformat() if event.last_timestamp else None,
                })
            
            logger.info(
                "events_retrieved",
                namespace=namespace,
                count=len(result),
            )
            
            return result
        
        except ApiException as e:
            logger.error(
                "get_events_error",
                namespace=namespace,
                error=str(e),
            )
            raise
    
    def _is_pod_ready(self, pod) -> bool:
        """Check if pod is ready"""
        if not pod.status.conditions:
            return False
        
        for condition in pod.status.conditions:
            if condition.type == "Ready":
                return condition.status == "True"
        
        return False
    
    def _get_restart_count(self, pod) -> int:
        """Get total restart count for pod"""
        if not pod.status.container_statuses:
            return 0
        
        return sum(c.restart_count for c in pod.status.container_statuses)


# Made with Bob