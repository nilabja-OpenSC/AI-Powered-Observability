"""
Approval Workflow for AI-Powered Observability Platform

Implements human-in-the-loop approval via Slack:
- Send approval requests with issue details
- Wait for human decision (approve/deny)
- 5-minute timeout defaults to DENY (fail-safe)
- Track approval state
- Send follow-up notifications
"""

import os
import time
import asyncio
from typing import Dict, Any, Optional, Literal
from enum import Enum
from datetime import datetime, timedelta

import structlog
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = structlog.get_logger(__name__)


class ApprovalDecision(str, Enum):
    """Approval decision states"""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    TIMEOUT = "timeout"


class ApprovalWorkflow:
    """
    Slack-based approval workflow for corrective actions.
    
    CRITICAL: All corrective actions MUST go through this workflow.
    Timeout (5 minutes) defaults to DENY for fail-safe operation.
    """
    
    def __init__(
        self,
        slack_bot_token: Optional[str] = None,
        slack_channel: Optional[str] = None,
        approval_timeout: int = 300,  # 5 minutes
    ):
        """
        Initialize approval workflow.
        
        Args:
            slack_bot_token: Slack bot token (from env if None)
            slack_channel: Slack channel for approvals (from env if None)
            approval_timeout: Timeout in seconds (default: 300 = 5 min)
        """
        self.slack_token = slack_bot_token or os.getenv("SLACK_BOT_TOKEN")
        self.slack_channel = slack_channel or os.getenv("SLACK_CHANNEL", "#observability-alerts")
        self.approval_timeout = approval_timeout
        
        if not self.slack_token:
            raise ValueError("SLACK_BOT_TOKEN not found in environment")
        
        self.client = WebClient(token=self.slack_token)
        
        # In-memory approval state (use Redis in production)
        self.approval_states: Dict[str, Dict[str, Any]] = {}
        
        logger.info(
            "approval_workflow_initialized",
            channel=self.slack_channel,
            timeout=self.approval_timeout,
        )
    
    async def request_approval(
        self,
        action_type: str,
        issue_summary: str,
        affected_resources: list,
        resolution_steps: list,
        severity: Literal["low", "medium", "high", "critical"] = "medium",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ApprovalDecision:
        """
        Request human approval for corrective action.
        
        Args:
            action_type: Type of action (e.g., "pod_restart", "deployment_scale")
            issue_summary: Brief description of the issue
            affected_resources: List of affected resources
            resolution_steps: List of steps to be executed
            severity: Issue severity
            metadata: Additional metadata
        
        Returns:
            ApprovalDecision (APPROVED, DENIED, or TIMEOUT)
        """
        import uuid
        
        approval_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # Store approval state
        self.approval_states[approval_id] = {
            "status": ApprovalDecision.PENDING,
            "action_type": action_type,
            "timestamp": timestamp,
            "metadata": metadata or {},
        }
        
        # Build Slack message with Block Kit
        blocks = self._build_approval_blocks(
            approval_id=approval_id,
            action_type=action_type,
            issue_summary=issue_summary,
            affected_resources=affected_resources,
            resolution_steps=resolution_steps,
            severity=severity,
        )
        
        try:
            # Send Slack message
            response = self.client.chat_postMessage(
                channel=self.slack_channel,
                text=f"Approval Required: {action_type}",
                blocks=blocks,
            )
            
            message_ts = response["ts"]
            self.approval_states[approval_id]["message_ts"] = message_ts
            
            logger.info(
                "approval_request_sent",
                approval_id=approval_id,
                action_type=action_type,
                severity=severity,
                channel=self.slack_channel,
            )
            
            # Wait for approval with timeout
            decision = await self._wait_for_approval(approval_id)
            
            # Update Slack message with decision
            await self._update_approval_message(
                approval_id=approval_id,
                decision=decision,
            )
            
            return decision
        
        except SlackApiError as e:
            logger.error(
                "slack_approval_error",
                approval_id=approval_id,
                error=str(e),
            )
            # Fail-safe: deny on error
            return ApprovalDecision.DENIED
    
    def _build_approval_blocks(
        self,
        approval_id: str,
        action_type: str,
        issue_summary: str,
        affected_resources: list,
        resolution_steps: list,
        severity: str,
    ) -> list:
        """Build Slack Block Kit blocks for approval request"""
        
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
                    "text": f"{severity_emoji} Approval Required: {action_type}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Issue Summary:*\n{issue_summary}",
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
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Proposed Resolution Steps:*\n" + "\n".join([f"{i+1}. {s}" for i, s in enumerate(resolution_steps)]),
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Approval ID:* `{approval_id}`\n*Timeout:* {self.approval_timeout // 60} minutes (defaults to DENY)",
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "✅ Approve",
                        },
                        "style": "primary",
                        "value": approval_id,
                        "action_id": f"approve_{approval_id}",
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "❌ Deny",
                        },
                        "style": "danger",
                        "value": approval_id,
                        "action_id": f"deny_{approval_id}",
                    },
                ],
            },
        ]
        
        return blocks
    
    async def _wait_for_approval(
        self,
        approval_id: str,
    ) -> ApprovalDecision:
        """
        Wait for approval decision with timeout.
        
        Polls approval state every second until:
        - Decision is made (APPROVED/DENIED)
        - Timeout is reached (defaults to DENIED)
        """
        start_time = time.time()
        
        while time.time() - start_time < self.approval_timeout:
            state = self.approval_states.get(approval_id, {})
            status = state.get("status", ApprovalDecision.PENDING)
            
            if status in [ApprovalDecision.APPROVED, ApprovalDecision.DENIED]:
                logger.info(
                    "approval_decision_received",
                    approval_id=approval_id,
                    decision=status,
                    duration=time.time() - start_time,
                )
                return status
            
            await asyncio.sleep(1)
        
        # Timeout reached - default to DENY (fail-safe)
        self.approval_states[approval_id]["status"] = ApprovalDecision.TIMEOUT
        
        logger.warning(
            "approval_timeout",
            approval_id=approval_id,
            timeout=self.approval_timeout,
        )
        
        return ApprovalDecision.TIMEOUT
    
    async def _update_approval_message(
        self,
        approval_id: str,
        decision: ApprovalDecision,
    ):
        """Update Slack message with approval decision"""
        state = self.approval_states.get(approval_id, {})
        message_ts = state.get("message_ts")
        
        if not message_ts:
            return
        
        # Decision emoji and color
        if decision == ApprovalDecision.APPROVED:
            emoji = "✅"
            color = "good"
        elif decision == ApprovalDecision.DENIED:
            emoji = "❌"
            color = "danger"
        else:  # TIMEOUT
            emoji = "⏱️"
            color = "warning"
        
        try:
            self.client.chat_update(
                channel=self.slack_channel,
                ts=message_ts,
                text=f"{emoji} Decision: {decision.upper()}",
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"{emoji} *Decision: {decision.upper()}*\n\nApproval ID: `{approval_id}`",
                        },
                    },
                ],
            )
            
            logger.info(
                "approval_message_updated",
                approval_id=approval_id,
                decision=decision,
            )
        
        except SlackApiError as e:
            logger.error(
                "slack_update_error",
                approval_id=approval_id,
                error=str(e),
            )
    
    def record_decision(
        self,
        approval_id: str,
        decision: Literal["approve", "deny"],
        approver: Optional[str] = None,
    ) -> bool:
        """
        Record approval decision (called by Slack webhook handler).
        
        Args:
            approval_id: Approval ID
            decision: "approve" or "deny"
            approver: User who made the decision
        
        Returns:
            True if recorded successfully
        """
        if approval_id not in self.approval_states:
            logger.warning(
                "approval_not_found",
                approval_id=approval_id,
            )
            return False
        
        decision_enum = ApprovalDecision.APPROVED if decision == "approve" else ApprovalDecision.DENIED
        
        self.approval_states[approval_id].update({
            "status": decision_enum,
            "approver": approver,
            "decision_timestamp": datetime.utcnow().isoformat(),
        })
        
        logger.info(
            "approval_decision_recorded",
            approval_id=approval_id,
            decision=decision_enum,
            approver=approver,
        )
        
        return True
    
    def get_approval_state(self, approval_id: str) -> Optional[Dict[str, Any]]:
        """Get approval state by ID"""
        return self.approval_states.get(approval_id)
    
    def cleanup_old_approvals(self, max_age_hours: int = 24):
        """Clean up old approval states"""
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        to_delete = []
        for approval_id, state in self.approval_states.items():
            timestamp = datetime.fromisoformat(state["timestamp"])
            if timestamp < cutoff:
                to_delete.append(approval_id)
        
        for approval_id in to_delete:
            del self.approval_states[approval_id]
        
        if to_delete:
            logger.info(
                "old_approvals_cleaned",
                count=len(to_delete),
            )


# Made with Bob