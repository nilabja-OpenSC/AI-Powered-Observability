"""
Notification Handler for Observability Agent

Handles Slack notifications for detected issues.
Sends formatted notifications with issue details and resolution steps.
"""

from typing import Dict, Any, List

import structlog

from agents.common.tools.slack import SlackTool

logger = structlog.get_logger(__name__)


class NotificationHandler:
    """
    Handles notifications for detected issues.
    
    Sends Slack notifications with issue details.
    """
    
    def __init__(self, slack_tool: SlackTool):
        """
        Initialize notification handler.
        
        Args:
            slack_tool: Slack tool for sending notifications
        """
        self.slack_tool = slack_tool
        
        logger.info("notification_handler_initialized")
    
    async def send_issue_notification(
        self,
        issue: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Send Slack notification for detected issue.
        
        Args:
            issue: Issue dict with details
        
        Returns:
            Slack API response
        """
        logger.info(
            "sending_issue_notification",
            issue_id=issue["id"],
            severity=issue["severity"],
        )
        
        try:
            # Send issue notification
            response = self.slack_tool.send_issue_notification(
                issue_type=issue["type"],
                severity=issue["severity"],
                summary=issue["summary"],
                affected_resources=issue["affected_resources"],
                details=issue.get("details", {}),
            )
            
            logger.info(
                "issue_notification_sent",
                issue_id=issue["id"],
            )
            
            return response
        
        except Exception as e:
            logger.error(
                "issue_notification_error",
                issue_id=issue["id"],
                error=str(e),
            )
            raise
    
    async def send_resolution_notification(
        self,
        issue_id: str,
        resolution_summary: str,
        resolution_details: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Send Slack notification for issue resolution.
        
        Args:
            issue_id: Issue ID
            resolution_summary: Resolution summary
            resolution_details: Resolution details
        
        Returns:
            Slack API response
        """
        logger.info(
            "sending_resolution_notification",
            issue_id=issue_id,
        )
        
        try:
            # Send success notification
            response = self.slack_tool.send_success_notification(
                action_type=f"Issue Resolved: {issue_id}",
                summary=resolution_summary,
                details=resolution_details,
            )
            
            logger.info(
                "resolution_notification_sent",
                issue_id=issue_id,
            )
            
            return response
        
        except Exception as e:
            logger.error(
                "resolution_notification_error",
                issue_id=issue_id,
                error=str(e),
            )
            raise
    
    async def send_batch_notification(
        self,
        issues: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Send batch notification for multiple issues.
        
        Args:
            issues: List of issues
        
        Returns:
            Slack API response
        """
        if not issues:
            return {}
        
        logger.info(
            "sending_batch_notification",
            issue_count=len(issues),
        )
        
        # Group issues by severity
        critical_issues = [i for i in issues if i["severity"] == "critical"]
        high_issues = [i for i in issues if i["severity"] == "high"]
        medium_issues = [i for i in issues if i["severity"] == "medium"]
        low_issues = [i for i in issues if i["severity"] == "low"]
        
        # Build summary
        summary_lines = []
        if critical_issues:
            summary_lines.append(f"🚨 {len(critical_issues)} critical issue(s)")
        if high_issues:
            summary_lines.append(f"🔴 {len(high_issues)} high severity issue(s)")
        if medium_issues:
            summary_lines.append(f"⚠️ {len(medium_issues)} medium severity issue(s)")
        if low_issues:
            summary_lines.append(f"ℹ️ {len(low_issues)} low severity issue(s)")
        
        summary = "\n".join(summary_lines)
        
        # Get affected resources
        affected_resources = []
        for issue in issues:
            affected_resources.extend(issue["affected_resources"])
        affected_resources = list(set(affected_resources))  # Deduplicate
        
        try:
            # Send batch notification
            response = self.slack_tool.send_issue_notification(
                issue_type="Multiple Issues Detected",
                severity="high" if critical_issues or high_issues else "medium",
                summary=summary,
                affected_resources=affected_resources[:10],  # Limit to 10
                details={
                    "total_issues": len(issues),
                    "critical": len(critical_issues),
                    "high": len(high_issues),
                    "medium": len(medium_issues),
                    "low": len(low_issues),
                },
            )
            
            logger.info(
                "batch_notification_sent",
                issue_count=len(issues),
            )
            
            return response
        
        except Exception as e:
            logger.error(
                "batch_notification_error",
                issue_count=len(issues),
                error=str(e),
            )
            raise


# Made with Bob