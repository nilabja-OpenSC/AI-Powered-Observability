"""
Common Agent Infrastructure for AI-Powered Observability Platform

This package provides shared utilities and base classes for all AI agents:
- LLM client (OpenAI/Groq)
- Vector store client (Chroma)
- Tool registry and execution
- Approval workflow (Slack)
- Namespace guard (enforce nilabja-haldar-dev)
- Kubernetes client
- Prometheus/Loki clients
- Slack/Confluence clients
"""

from .llm_client import LLMClient
from .vector_store import VectorStoreClient
from .approval_workflow import ApprovalWorkflow
from .namespace_guard import NamespaceGuard

__all__ = [
    "LLMClient",
    "VectorStoreClient",
    "ApprovalWorkflow",
    "NamespaceGuard",
]

__version__ = "1.0.0"

# Made with Bob