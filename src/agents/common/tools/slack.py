"""
Slack Tool for AI-Powered Observability Platform

Provides Slack notification operations:
- Send messages with Block Kit formatting
- Send approval requests (handled by ApprovalWorkflow)
- Send issue notifications
- Send status updates
"""

import os
from typing import Dict, Any, Optional, List

import structlog
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = structlog.get_logger(__name__)


class SlackTool:
    """
    Slack notification tool for agent communications.
    
    Used for:
    - Issue notifications
    - Status updates
    - Manual steps (when approval denied)
    """
    
    def __init__(
        self,
        bot_token: Optional[str] = None,
        webhook_url: Optional[str] = None,
        default_channel: Optional[str] = None,
    ):
        """
        Initialize Slack tool.
        
        Args:
            bot_token: Slack bot token (default: from SLACK_BOT_TOKEN env)
            webhook_url: Slack webhook URL (default: from SLACK_WEBHOOK_URL env)
            default_channel: Default channel (default: from SLACK_CHANNEL env)
        """
        self.bot_token = bot_token or os.getenv("SLACK_BOT_TOKEN")
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
        self.default_channel = default_channel or os.getenv(
            "SLACK_CHANNEL",
            "#observability-alerts"
        )
        
        if self.bot_token:
            self.client = WebClient(token=self.bot_token)
        else:
            self.client = None
            logger.warning("slack_bot_token_not_found")
        
        logger.info(
            "slack_tool_initialized",
            has_bot_token=bool(self.bot_token),
            has_webhook=bool(self.webhook_url),
            default_channel=self.default_channel,
        )
    
    def send_message(
        self,
        text: str,
        channel: Optional[str] = None,
        blocks: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Send Slack message.
        
        Args:
            text: Message text (fallback if blocks not supported)
            channel: Channel to send to (default: default_channel)
            blocks: Block Kit blocks (optional)
        
        Returns:
            Slack API response
        """
        if not self.client:
            raise ValueError("Slack bot token not configured")
        
        channel = channel or self.default_channel
        
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=text,
                blocks=blocks,
            )
            
            logger.info(
                "slack_message_sent",
                channel=channel,
                has_blocks=bool(blocks),
            )
            
            return response.data
        
        except SlackApiError as e:
            logger.error(
                "slack_message_error",
                channel=channel,
                error=str(e),
            )
            raise
    
    def send_issue_notification(
        self,
        issue_type: str,
        severity: str,
        summary: str,
        affected_resources: List[str],
        details: Optional[Dict[str, Any]] = None,
        channel: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send issue notification with formatted blocks.
        
        Args:
            issue_type: Type of issue (e.g., "CrashLoopBackOff")
            severity: Severity level (low, medium, high, critical)
            summary: Issue summary
            affected_resources: List of affected resources
            details: Additional details (optional)
            channel: Channel to send to (default: default_channel)
        
        Returns:
            Slack API response
        """
        # Severity emoji
        severity_emoji = {
            "low": "ℹ️",
            "medium": "⚠️",
            "high": "🔴",
            "critical": "🚨",
        }.get(severity, "⚠️")
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{severity_emoji} Issue Detected: {issue_type}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Summary:*\n{summary}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Severity:* {severity.upper()}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Affected Resources:*\n" + "\n".join([f"• {r}" for r in affected_resources]),
                },
            },
        ]
        
        # Add details if provided
        if details:
            details_text = "\n".join([f"*{k}:* {v}" for k, v in details.items()])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Details:*\n{details_text}",
                },
            })
        
        return self.send_message(
            text=f"{severity_emoji} Issue: {issue_type} - {summary}",
            channel=channel,
            blocks=blocks,
        )
    
    def send_manual_steps(
        self,
        action_type: str,
        steps: List[str],
        reason: str = "Approval denied or timed out",
        channel: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send manual steps when approval is denied.
        
        Args:
            action_type: Type of action that was denied
            steps: Manual steps to perform
            reason: Reason for manual steps
            channel: Channel to send to (default: default_channel)
        
        Returns:
            Slack API response
        """
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📋 Manual Steps Required: {action_type}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Reason:* {reason}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Manual Steps:*\n" + "\n".join([f"{i+1}. {s}" for i, s in enumerate(steps)]),
                },
            },
        ]
        
        return self.send_message(
            text=f"Manual steps required for {action_type}",
            channel=channel,
            blocks=blocks,
        )
    
    def send_success_notification(
        self,
        action_type: str,
        summary: str,
        details: Optional[Dict[str, Any]] = None,
        channel: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send success notification.
        
        Args:
            action_type: Type of action completed
            summary: Success summary
            details: Additional details (optional)
            channel: Channel to send to (default: default_channel)
        
        Returns:
            Slack API response
        """
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"✅ Success: {action_type}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Summary:*\n{summary}",
                },
            },
        ]
        
        # Add details if provided
        if details:
            details_text = "\n".join([f"*{k}:* {v}" for k, v in details.items()])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Details:*\n{details_text}",
                },
            })
        
        return self.send_message(
            text=f"✅ {action_type}: {summary}",
            channel=channel,
            blocks=blocks,
        )


# Made with Bob