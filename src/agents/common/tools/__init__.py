"""
Tool Registry for AI-Powered Observability Platform

Provides tools that agents can use:
- Kubernetes operations (get, list, delete pods, scale deployments)
- Prometheus queries (metrics)
- Loki queries (logs)
- Slack notifications
- Confluence documentation
"""

from .kubernetes import KubernetesTool
from .prometheus import PrometheusTool
from .loki import LokiTool
from .slack import SlackTool
from .confluence import ConfluenceTool

__all__ = [
    "KubernetesTool",
    "PrometheusTool",
    "LokiTool",
    "SlackTool",
    "ConfluenceTool",
]

# Made with Bob