"""
Dashboard Generator for Observability Agent

Generates Grafana dashboards from natural language descriptions.
Creates panels with appropriate queries and visualizations.
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime

import structlog
import httpx

from agents.common.llm_client import LLMClient

logger = structlog.get_logger(__name__)


class DashboardGenerator:
    """
    Generates Grafana dashboards.
    
    Uses LLM to understand dashboard requirements and generate JSON.
    """
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize dashboard generator.
        
        Args:
            llm_client: LLM client for dashboard generation
        """
        self.llm_client = llm_client
        
        # Grafana configuration
        self.grafana_url = os.getenv("GRAFANA_URL", "http://grafana:3000")
        self.grafana_api_key = os.getenv("GRAFANA_API_KEY", "")
        
        logger.info(
            "dashboard_generator_initialized",
            grafana_url=self.grafana_url,
        )
    
    async def create(
        self,
        title: str,
        description: Optional[str] = None,
        panels: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Create Grafana dashboard.
        
        Args:
            title: Dashboard title
            description: Dashboard description (optional)
            panels: Panel configurations (optional, will generate if not provided)
        
        Returns:
            Dashboard info with URL and ID
        """
        logger.info(
            "dashboard_creation_started",
            title=title,
        )
        
        # Generate panels if not provided
        if not panels:
            panels = await self._generate_panels(title, description)
        
        # Build dashboard JSON
        dashboard_json = self._build_dashboard_json(
            title=title,
            description=description,
            panels=panels,
        )
        
        # Create dashboard in Grafana
        try:
            dashboard_info = await self._create_in_grafana(dashboard_json)
            
            logger.info(
                "dashboard_created",
                title=title,
                dashboard_id=dashboard_info["id"],
            )
            
            return dashboard_info
        
        except Exception as e:
            logger.error(
                "dashboard_creation_error",
                title=title,
                error=str(e),
            )
            raise
    
    async def _generate_panels(
        self,
        title: str,
        description: Optional[str],
    ) -> List[Dict[str, Any]]:
        """
        Generate panel configurations using LLM.
        
        Args:
            title: Dashboard title
            description: Dashboard description
        
        Returns:
            List of panel configurations
        """
        prompt = f"""You are an expert in Grafana dashboard design.

Generate panel configurations for a Grafana dashboard.

Dashboard Title: {title}
Description: {description or "No description provided"}

Generate 3-5 panels that would be useful for this dashboard.
For each panel, specify:
- Title
- Type (graph, stat, table, heatmap)
- PromQL query (must include namespace="nilabja-haldar-dev")
- Description

Format:
Panel 1:
Title: [panel title]
Type: [panel type]
Query: [PromQL query]
Description: [panel description]

Panel 2:
...
"""
        
        try:
            response = self.llm_client.generate(
                prompt=prompt,
                max_tokens=800,
                temperature=0.7,
            )
            
            # Parse panels from response
            panels = self._parse_panels(response)
            
            return panels
        
        except Exception as e:
            logger.error(
                "panel_generation_error",
                title=title,
                error=str(e),
            )
            # Return default panels
            return self._get_default_panels()
    
    def _parse_panels(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse panel configurations from LLM response.
        
        Args:
            response: LLM response
        
        Returns:
            List of panel configurations
        """
        panels = []
        current_panel = {}
        
        for line in response.strip().split("\n"):
            line = line.strip()
            
            if line.startswith("Panel"):
                if current_panel:
                    panels.append(current_panel)
                current_panel = {}
            elif line.startswith("Title:"):
                current_panel["title"] = line.split(":", 1)[1].strip()
            elif line.startswith("Type:"):
                current_panel["type"] = line.split(":", 1)[1].strip().lower()
            elif line.startswith("Query:"):
                current_panel["query"] = line.split(":", 1)[1].strip()
            elif line.startswith("Description:"):
                current_panel["description"] = line.split(":", 1)[1].strip()
        
        # Add last panel
        if current_panel:
            panels.append(current_panel)
        
        return panels if panels else self._get_default_panels()
    
    def _get_default_panels(self) -> List[Dict[str, Any]]:
        """
        Get default panel configurations.
        
        Returns:
            List of default panels
        """
        return [
            {
                "title": "CPU Usage",
                "type": "graph",
                "query": 'rate(container_cpu_usage_seconds_total{namespace="nilabja-haldar-dev"}[5m])',
                "description": "CPU usage rate by pod",
            },
            {
                "title": "Memory Usage",
                "type": "graph",
                "query": 'container_memory_usage_bytes{namespace="nilabja-haldar-dev"}',
                "description": "Memory usage by pod",
            },
            {
                "title": "HTTP Request Rate",
                "type": "graph",
                "query": 'rate(http_requests_total{namespace="nilabja-haldar-dev"}[5m])',
                "description": "HTTP request rate by service",
            },
        ]
    
    def _build_dashboard_json(
        self,
        title: str,
        description: Optional[str],
        panels: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Build Grafana dashboard JSON.
        
        Args:
            title: Dashboard title
            description: Dashboard description
            panels: Panel configurations
        
        Returns:
            Dashboard JSON
        """
        # Build panels
        grafana_panels = []
        for i, panel in enumerate(panels):
            grafana_panel = {
                "id": i + 1,
                "title": panel.get("title", f"Panel {i+1}"),
                "type": panel.get("type", "graph"),
                "gridPos": {
                    "x": (i % 2) * 12,
                    "y": (i // 2) * 8,
                    "w": 12,
                    "h": 8,
                },
                "targets": [
                    {
                        "expr": panel.get("query", "up"),
                        "refId": "A",
                    }
                ],
                "description": panel.get("description", ""),
            }
            grafana_panels.append(grafana_panel)
        
        # Build dashboard
        dashboard = {
            "dashboard": {
                "title": title,
                "description": description or "",
                "tags": ["ai-generated", "nilabja-haldar-dev"],
                "timezone": "utc",
                "panels": grafana_panels,
                "schemaVersion": 36,
                "version": 1,
                "refresh": "30s",
            },
            "overwrite": False,
        }
        
        return dashboard
    
    async def _create_in_grafana(
        self,
        dashboard_json: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create dashboard in Grafana via API.
        
        Args:
            dashboard_json: Dashboard JSON
        
        Returns:
            Dashboard info with URL and ID
        """
        if not self.grafana_api_key:
            logger.warning("grafana_api_key_not_configured")
            # Return mock response for testing
            return {
                "id": "mock-dashboard-id",
                "url": f"{self.grafana_url}/d/mock-dashboard-id",
                "status": "success",
            }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.grafana_url}/api/dashboards/db",
                    json=dashboard_json,
                    headers={
                        "Authorization": f"Bearer {self.grafana_api_key}",
                        "Content-Type": "application/json",
                    },
                )
                
                response.raise_for_status()
                
                result = response.json()
                
                return {
                    "id": result.get("uid", "unknown"),
                    "url": f"{self.grafana_url}{result.get('url', '')}",
                    "status": result.get("status", "success"),
                }
        
        except httpx.HTTPError as e:
            logger.error(
                "grafana_api_error",
                error=str(e),
            )
            raise
        
        except Exception as e:
            logger.error(
                "dashboard_creation_error",
                error=str(e),
            )
            raise


# Made with Bob