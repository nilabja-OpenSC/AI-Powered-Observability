"""
Recovery Actions for Pod Recovery Agent

Executes recovery actions on pods with human approval.
Actions: restart, scale, delete (with recreation).

CRITICAL: All actions require human approval via Slack.
"""

from typing import Dict, Any, Optional
from datetime import datetime

import structlog

from agents.common.tools.kubernetes import KubernetesTool
from agents.common.tools.slack import SlackTool
from agents.common.approval_workflow import ApprovalWorkflow
from agents.common.tools.confluence import ConfluenceTool

logger = structlog.get_logger(__name__)


class RecoveryActions:
    """
    Executes recovery actions on pods.
    
    All actions require human approval via Slack.
    """
    
    def __init__(
        self,
        k8s_tool: KubernetesTool,
        approval_workflow: ApprovalWorkflow,
        slack_tool: SlackTool,
        confluence_tool: Optional[ConfluenceTool] = None,
    ):
        """
        Initialize recovery actions.
        
        Args:
            k8s_tool: Kubernetes tool
            approval_workflow: Approval workflow
            slack_tool: Slack tool
            confluence_tool: Confluence tool (optional)
        """
        self.k8s_tool = k8s_tool
        self.approval_workflow = approval_workflow
        self.slack_tool = slack_tool
        self.confluence_tool = confluence_tool
        
        logger.info("recovery_actions_initialized")
    
    async def execute(
        self,
        pod_name: str,
        action: str,
        namespace: str = "nilabja-haldar-dev",
        execute: bool = False,
    ) -> Dict[str, Any]:
        """
        Execute recovery action.
        
        Args:
            pod_name: Pod name
            action: Action type (restart, scale, delete)
            namespace: Kubernetes namespace
            execute: Whether to execute (requires approval)
        
        Returns:
            Action result
        """
        logger.info(
            "recovery_action_requested",
            pod_name=pod_name,
            action=action,
            execute=execute,
        )
        
        # If not executing, return plan
        if not execute:
            return await self._plan_action(pod_name, action, namespace)
        
        # Request approval
        issue_details = {
            "id": f"recovery-{pod_name}-{datetime.utcnow().timestamp()}",
            "summary": f"Execute {action} on pod {pod_name}",
            "severity": "high",
            "affected_resources": [f"pod/{pod_name}"],
            "resolution_steps": [
                f"Action: {action}",
                f"Pod: {pod_name}",
                f"Namespace: {namespace}",
            ],
        }
        
        approval = await self.approval_workflow.request_approval(issue_details)
        
        if approval != "APPROVED":
            # Send manual steps
            await self.slack_tool.send_manual_steps(
                action_type=f"{action} pod {pod_name}",
                steps=await self._get_manual_steps(action, pod_name, namespace),
                reason="Approval denied or timed out",
            )
            
            return {
                "status": "denied",
                "message": "Action not approved",
                "manual_steps": await self._get_manual_steps(action, pod_name, namespace),
            }
        
        # Execute action
        try:
            if action == "restart":
                result = await self._restart_pod(pod_name, namespace)
            elif action == "scale":
                result = await self._scale_deployment(pod_name, namespace)
            elif action == "delete":
                result = await self._delete_pod(pod_name, namespace)
            else:
                raise ValueError(f"Unknown action: {action}")
            
            # Send success notification
            await self.slack_tool.send_success_notification(
                action_type=f"{action} pod {pod_name}",
                summary=result["message"],
                details=result.get("details", {}),
            )
            
            # Document in Confluence if available
            if self.confluence_tool:
                await self._document_action(
                    pod_name=pod_name,
                    action=action,
                    result=result,
                    issue_details=issue_details,
                )
            
            logger.info(
                "recovery_action_executed",
                pod_name=pod_name,
                action=action,
                status="success",
            )
            
            return {
                "status": "success",
                "action": action,
                "result": result,
            }
        
        except Exception as e:
            logger.error(
                "recovery_action_error",
                pod_name=pod_name,
                action=action,
                error=str(e),
            )
            
            # Send error notification
            await self.slack_tool.send_issue_notification(
                issue_type=f"Recovery Action Failed: {action}",
                severity="high",
                summary=f"Failed to {action} pod {pod_name}",
                affected_resources=[f"pod/{pod_name}"],
                details={"error": str(e)},
            )
            
            return {
                "status": "error",
                "message": str(e),
            }
    
    async def _plan_action(
        self,
        pod_name: str,
        action: str,
        namespace: str,
    ) -> Dict[str, Any]:
        """
        Plan action without executing.
        
        Args:
            pod_name: Pod name
            action: Action type
            namespace: Kubernetes namespace
        
        Returns:
            Action plan
        """
        steps = await self._get_manual_steps(action, pod_name, namespace)
        
        return {
            "status": "plan",
            "action": action,
            "pod_name": pod_name,
            "namespace": namespace,
            "steps": steps,
            "message": f"To execute, set execute=True and approval will be requested",
        }
    
    async def _restart_pod(
        self,
        pod_name: str,
        namespace: str,
    ) -> Dict[str, Any]:
        """
        Restart pod by deleting it (will be recreated by deployment).
        
        Args:
            pod_name: Pod name
            namespace: Kubernetes namespace
        
        Returns:
            Result dict
        """
        logger.info(
            "restarting_pod",
            pod_name=pod_name,
            namespace=namespace,
        )
        
        # Delete pod (will be recreated)
        self.k8s_tool.delete_pod(
            pod_name=pod_name,
            namespace=namespace,
        )
        
        return {
            "message": f"Pod {pod_name} restarted successfully",
            "details": {
                "action": "delete_pod",
                "note": "Pod will be recreated by deployment controller",
            },
        }
    
    async def _scale_deployment(
        self,
        pod_name: str,
        namespace: str,
        replicas: int = 2,
    ) -> Dict[str, Any]:
        """
        Scale deployment (extract deployment name from pod).
        
        Args:
            pod_name: Pod name
            namespace: Kubernetes namespace
            replicas: Target replica count
        
        Returns:
            Result dict
        """
        # Extract deployment name from pod name
        # Pod names are typically: deployment-name-xxxxx-yyyyy
        deployment_name = "-".join(pod_name.split("-")[:-2])
        
        logger.info(
            "scaling_deployment",
            deployment_name=deployment_name,
            replicas=replicas,
            namespace=namespace,
        )
        
        self.k8s_tool.scale_deployment(
            deployment_name=deployment_name,
            replicas=replicas,
            namespace=namespace,
        )
        
        return {
            "message": f"Deployment {deployment_name} scaled to {replicas} replicas",
            "details": {
                "deployment": deployment_name,
                "replicas": replicas,
            },
        }
    
    async def _delete_pod(
        self,
        pod_name: str,
        namespace: str,
    ) -> Dict[str, Any]:
        """
        Delete pod (will be recreated by deployment).
        
        Args:
            pod_name: Pod name
            namespace: Kubernetes namespace
        
        Returns:
            Result dict
        """
        logger.info(
            "deleting_pod",
            pod_name=pod_name,
            namespace=namespace,
        )
        
        self.k8s_tool.delete_pod(
            pod_name=pod_name,
            namespace=namespace,
        )
        
        return {
            "message": f"Pod {pod_name} deleted successfully",
            "details": {
                "action": "delete_pod",
                "note": "Pod will be recreated by deployment controller",
            },
        }
    
    async def _get_manual_steps(
        self,
        action: str,
        pod_name: str,
        namespace: str,
    ) -> list:
        """
        Get manual steps for action.
        
        Args:
            action: Action type
            pod_name: Pod name
            namespace: Kubernetes namespace
        
        Returns:
            List of manual steps
        """
        if action == "restart":
            return [
                f"kubectl delete pod {pod_name} -n {namespace}",
                "Wait for pod to be recreated",
                f"kubectl get pods -n {namespace} -w",
            ]
        
        elif action == "scale":
            deployment_name = "-".join(pod_name.split("-")[:-2])
            return [
                f"kubectl scale deployment {deployment_name} --replicas=2 -n {namespace}",
                f"kubectl get pods -n {namespace} -w",
            ]
        
        elif action == "delete":
            return [
                f"kubectl delete pod {pod_name} -n {namespace}",
                "Pod will be recreated by deployment controller",
                f"kubectl get pods -n {namespace} -w",
            ]
        
        else:
            return [
                f"Unknown action: {action}",
                "Please specify: restart, scale, or delete",
            ]
    
    async def _document_action(
        self,
        pod_name: str,
        action: str,
        result: Dict[str, Any],
        issue_details: Dict[str, Any],
    ):
        """
        Document action in Confluence.
        
        Args:
            pod_name: Pod name
            action: Action type
            result: Action result
            issue_details: Issue details
        """
        if not self.confluence_tool:
            return
        
        try:
            # Create incident page
            page = await self.confluence_tool.create_incident_page(
                incident_id=issue_details["id"],
                issue_type=f"Pod Recovery: {action}",
                severity=issue_details["severity"],
                summary=issue_details["summary"],
                affected_resources=issue_details["affected_resources"],
                detection_time=datetime.utcnow(),
                details={
                    "action": action,
                    "pod_name": pod_name,
                },
            )
            
            # Update with resolution
            await self.confluence_tool.update_incident_resolution(
                page_id=page["id"],
                resolution_steps=issue_details["resolution_steps"],
                outcome=result["message"],
                approver="Slack approval",
                completion_time=datetime.utcnow(),
            )
            
            logger.info(
                "action_documented",
                pod_name=pod_name,
                page_id=page["id"],
            )
        
        except Exception as e:
            logger.warning(
                "documentation_error",
                pod_name=pod_name,
                error=str(e),
            )


# Made with Bob