"""
Confluence Tool for AI-Powered Observability Platform

Provides Confluence documentation operations:
- Create incident pages
- Update incident pages
- Create postmortem reports
- Link related incidents
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime

import structlog
from atlassian import Confluence

logger = structlog.get_logger(__name__)


class ConfluenceTool:
    """
    Confluence documentation tool for incident tracking.
    
    Used for:
    - Creating incident pages
    - Documenting resolutions
    - Postmortem reports
    """
    
    def __init__(
        self,
        url: Optional[str] = None,
        username: Optional[str] = None,
        api_token: Optional[str] = None,
        space_key: Optional[str] = None,
    ):
        """
        Initialize Confluence tool.
        
        Args:
            url: Confluence URL (default: from CONFLUENCE_URL env)
            username: Confluence username (default: from CONFLUENCE_USERNAME env)
            api_token: Confluence API token (default: from CONFLUENCE_API_TOKEN env)
            space_key: Space key (default: from CONFLUENCE_SPACE env)
        """
        self.url = url or os.getenv("CONFLUENCE_URL")
        self.username = username or os.getenv("CONFLUENCE_USERNAME")
        self.api_token = api_token or os.getenv("CONFLUENCE_API_TOKEN")
        self.space_key = space_key or os.getenv("CONFLUENCE_SPACE", "OBSERVABILITY")
        
        if self.url and self.username and self.api_token:
            self.client = Confluence(
                url=self.url,
                username=self.username,
                password=self.api_token,
            )
        else:
            self.client = None
            logger.warning("confluence_credentials_not_found")
        
        logger.info(
            "confluence_tool_initialized",
            has_credentials=bool(self.client),
            space_key=self.space_key,
        )
    
    def create_incident_page(
        self,
        incident_id: str,
        issue_type: str,
        severity: str,
        summary: str,
        affected_resources: List[str],
        detection_time: datetime,
        details: Optional[Dict[str, Any]] = None,
        parent_page_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create incident documentation page.
        
        Args:
            incident_id: Unique incident ID
            issue_type: Type of issue
            severity: Severity level
            summary: Issue summary
            affected_resources: List of affected resources
            detection_time: When issue was detected
            details: Additional details (optional)
            parent_page_id: Parent page ID (optional)
        
        Returns:
            Created page info
        """
        if not self.client:
            raise ValueError("Confluence credentials not configured")
        
        # Format affected resources
        resources_html = "<ul>" + "".join([f"<li>{r}</li>" for r in affected_resources]) + "</ul>"
        
        # Format details
        details_html = ""
        if details:
            details_html = "<h3>Additional Details</h3><ul>" + "".join([
                f"<li><strong>{k}:</strong> {v}</li>" for k, v in details.items()
            ]) + "</ul>"
        
        # Create page content
        content = f"""
        <h1>Incident: {incident_id}</h1>
        
        <ac:structured-macro ac:name="info">
            <ac:rich-text-body>
                <p><strong>Status:</strong> INVESTIGATING</p>
                <p><strong>Detected:</strong> {detection_time.isoformat()}</p>
                <p><strong>Severity:</strong> {severity.upper()}</p>
            </ac:rich-text-body>
        </ac:structured-macro>
        
        <h2>Issue Summary</h2>
        <p>{summary}</p>
        
        <h2>Issue Type</h2>
        <p>{issue_type}</p>
        
        <h2>Affected Resources</h2>
        {resources_html}
        
        {details_html}
        
        <h2>Timeline</h2>
        <table>
            <tr>
                <th>Time</th>
                <th>Event</th>
            </tr>
            <tr>
                <td>{detection_time.strftime('%Y-%m-%d %H:%M:%S UTC')}</td>
                <td>Issue detected</td>
            </tr>
        </table>
        
        <h2>Resolution Steps</h2>
        <p><em>To be updated...</em></p>
        
        <h2>Outcome</h2>
        <p><em>To be updated...</em></p>
        """
        
        try:
            page = self.client.create_page(
                space=self.space_key,
                title=f"Incident-{incident_id}",
                body=content,
                parent_id=parent_page_id,
            )
            
            logger.info(
                "confluence_incident_page_created",
                incident_id=incident_id,
                page_id=page["id"],
            )
            
            return page
        
        except Exception as e:
            logger.error(
                "confluence_page_creation_error",
                incident_id=incident_id,
                error=str(e),
            )
            raise
    
    def update_incident_resolution(
        self,
        page_id: str,
        resolution_steps: List[str],
        outcome: str,
        approver: str,
        completion_time: datetime,
    ) -> Dict[str, Any]:
        """
        Update incident page with resolution details.
        
        Args:
            page_id: Confluence page ID
            resolution_steps: Steps taken to resolve
            outcome: Resolution outcome
            approver: Who approved the action
            completion_time: When resolution completed
        
        Returns:
            Updated page info
        """
        if not self.client:
            raise ValueError("Confluence credentials not configured")
        
        # Get existing page
        page = self.client.get_page_by_id(page_id, expand="body.storage,version")
        
        # Format resolution steps
        steps_html = "<ol>" + "".join([f"<li>{s}</li>" for s in resolution_steps]) + "</ol>"
        
        # Update resolution section
        resolution_content = f"""
        <h2>Resolution Steps</h2>
        {steps_html}
        
        <h2>Outcome</h2>
        <p>{outcome}</p>
        
        <ac:structured-macro ac:name="info">
            <ac:rich-text-body>
                <p><strong>Approved By:</strong> {approver}</p>
                <p><strong>Completed:</strong> {completion_time.isoformat()}</p>
            </ac:rich-text-body>
        </ac:structured-macro>
        """
        
        # Replace placeholder sections
        updated_content = page["body"]["storage"]["value"]
        updated_content = updated_content.replace(
            "<h2>Resolution Steps</h2>\n        <p><em>To be updated...</em></p>",
            resolution_content
        )
        
        # Update status to RESOLVED
        updated_content = updated_content.replace(
            "<p><strong>Status:</strong> INVESTIGATING</p>",
            "<p><strong>Status:</strong> RESOLVED</p>"
        )
        
        try:
            updated_page = self.client.update_page(
                page_id=page_id,
                title=page["title"],
                body=updated_content,
                version_comment="Resolution documented",
            )
            
            logger.info(
                "confluence_incident_updated",
                page_id=page_id,
            )
            
            return updated_page
        
        except Exception as e:
            logger.error(
                "confluence_page_update_error",
                page_id=page_id,
                error=str(e),
            )
            raise
    
    def create_postmortem(
        self,
        incident_id: str,
        incident_page_id: str,
        root_cause: str,
        impact: str,
        lessons_learned: List[str],
        action_items: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        """
        Create postmortem report.
        
        Args:
            incident_id: Incident ID
            incident_page_id: Link to incident page
            root_cause: Root cause analysis
            impact: Impact description
            lessons_learned: Lessons learned
            action_items: Action items (owner, description, due_date)
        
        Returns:
            Created postmortem page info
        """
        if not self.client:
            raise ValueError("Confluence credentials not configured")
        
        # Format lessons learned
        lessons_html = "<ul>" + "".join([f"<li>{l}</li>" for l in lessons_learned]) + "</ul>"
        
        # Format action items
        action_items_html = "<table><tr><th>Owner</th><th>Action</th><th>Due Date</th></tr>"
        for item in action_items:
            action_items_html += f"""
            <tr>
                <td>{item.get('owner', 'TBD')}</td>
                <td>{item.get('description', '')}</td>
                <td>{item.get('due_date', 'TBD')}</td>
            </tr>
            """
        action_items_html += "</table>"
        
        # Create postmortem content
        content = f"""
        <h1>Postmortem: {incident_id}</h1>
        
        <p><strong>Related Incident:</strong> <ac:link><ri:page ri:content-title="Incident-{incident_id}" /></ac:link></p>
        
        <h2>Root Cause</h2>
        <p>{root_cause}</p>
        
        <h2>Impact</h2>
        <p>{impact}</p>
        
        <h2>Lessons Learned</h2>
        {lessons_html}
        
        <h2>Action Items</h2>
        {action_items_html}
        """
        
        try:
            page = self.client.create_page(
                space=self.space_key,
                title=f"Postmortem-{incident_id}",
                body=content,
            )
            
            logger.info(
                "confluence_postmortem_created",
                incident_id=incident_id,
                page_id=page["id"],
            )
            
            return page
        
        except Exception as e:
            logger.error(
                "confluence_postmortem_error",
                incident_id=incident_id,
                error=str(e),
            )
            raise


# Made with Bob