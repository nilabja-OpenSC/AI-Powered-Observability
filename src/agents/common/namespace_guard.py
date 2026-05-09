"""
Namespace Guard for AI-Powered Observability Platform

CRITICAL SECURITY COMPONENT: Enforces namespace isolation.

ALL operations MUST be scoped to: nilabja-haldar-dev

This guard prevents:
- Cluster-wide operations
- Cross-namespace access
- Accidental resource modification in other namespaces
"""

import os
from typing import Optional
from functools import wraps

import structlog

logger = structlog.get_logger(__name__)


class NamespaceViolationError(Exception):
    """Raised when operation violates namespace constraint"""
    pass


class NamespaceGuard:
    """
    Enforces namespace isolation for all agent operations.
    
    CRITICAL: ALL Kubernetes operations MUST go through this guard.
    """
    
    def __init__(self, allowed_namespace: Optional[str] = None):
        """
        Initialize namespace guard.
        
        Args:
            allowed_namespace: Allowed namespace (default: from KUBERNETES_NAMESPACE env)
        """
        self.allowed_namespace = allowed_namespace or os.getenv(
            "KUBERNETES_NAMESPACE",
            "nilabja-haldar-dev"
        )
        
        logger.info(
            "namespace_guard_initialized",
            allowed_namespace=self.allowed_namespace,
        )
    
    def validate_namespace(self, namespace: str) -> bool:
        """
        Validate that namespace matches allowed namespace.
        
        Args:
            namespace: Namespace to validate
        
        Returns:
            True if valid
        
        Raises:
            NamespaceViolationError: If namespace doesn't match
        """
        if namespace != self.allowed_namespace:
            logger.error(
                "namespace_violation",
                requested=namespace,
                allowed=self.allowed_namespace,
            )
            raise NamespaceViolationError(
                f"Operation not allowed in namespace '{namespace}'. "
                f"Only '{self.allowed_namespace}' is permitted."
            )
        
        return True
    
    def enforce_namespace(self, func):
        """
        Decorator to enforce namespace on function calls.
        
        Usage:
            @namespace_guard.enforce_namespace
            def delete_pod(pod_name: str, namespace: str):
                # Function implementation
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract namespace from kwargs
            namespace = kwargs.get('namespace')
            
            # If not in kwargs, check args (assume second arg is namespace)
            if namespace is None and len(args) > 1:
                namespace = args[1]
            
            # If still not found, use default
            if namespace is None:
                namespace = self.allowed_namespace
                kwargs['namespace'] = namespace
            
            # Validate namespace
            self.validate_namespace(namespace)
            
            # Execute function
            return func(*args, **kwargs)
        
        return wrapper
    
    def get_allowed_namespace(self) -> str:
        """Get the allowed namespace"""
        return self.allowed_namespace
    
    def add_namespace_filter(self, query: str) -> str:
        """
        Add namespace filter to PromQL/LogQL query.
        
        Args:
            query: Original query
        
        Returns:
            Query with namespace filter added
        """
        namespace_filter = f'namespace="{self.allowed_namespace}"'
        
        # Check if query already has namespace filter
        if 'namespace=' in query:
            logger.warning(
                "query_already_has_namespace_filter",
                query=query[:100],
            )
            return query
        
        # Add namespace filter to query
        if '{' in query:
            # Query has existing filters
            query = query.replace('{', f'{{{namespace_filter},', 1)
        else:
            # Query has no filters
            metric_name = query.split('[')[0].split('(')[0].strip()
            query = query.replace(metric_name, f'{metric_name}{{{namespace_filter}}}', 1)
        
        logger.info(
            "namespace_filter_added",
            original_query=query[:50],
        )
        
        return query
    
    def validate_resource_namespace(self, resource: dict) -> bool:
        """
        Validate that Kubernetes resource is in allowed namespace.
        
        Args:
            resource: Kubernetes resource dict
        
        Returns:
            True if valid
        
        Raises:
            NamespaceViolationError: If resource is in wrong namespace
        """
        metadata = resource.get('metadata', {})
        namespace = metadata.get('namespace')
        
        if namespace and namespace != self.allowed_namespace:
            resource_name = metadata.get('name', 'unknown')
            resource_kind = resource.get('kind', 'unknown')
            
            logger.error(
                "resource_namespace_violation",
                resource_kind=resource_kind,
                resource_name=resource_name,
                resource_namespace=namespace,
                allowed_namespace=self.allowed_namespace,
            )
            
            raise NamespaceViolationError(
                f"{resource_kind} '{resource_name}' is in namespace '{namespace}'. "
                f"Only resources in '{self.allowed_namespace}' are permitted."
            )
        
        return True
    
    def validate_resource_list(self, resources: list) -> bool:
        """
        Validate that all resources in list are in allowed namespace.
        
        Args:
            resources: List of Kubernetes resource dicts
        
        Returns:
            True if all valid
        
        Raises:
            NamespaceViolationError: If any resource is in wrong namespace
        """
        for resource in resources:
            self.validate_resource_namespace(resource)
        
        return True


# Global namespace guard instance
namespace_guard = NamespaceGuard()


# Convenience decorator
def require_namespace(func):
    """
    Convenience decorator for namespace enforcement.
    
    Usage:
        from common.namespace_guard import require_namespace
        
        @require_namespace
        def delete_pod(pod_name: str, namespace: str):
            # Function implementation
    """
    return namespace_guard.enforce_namespace(func)


# Made with Bob