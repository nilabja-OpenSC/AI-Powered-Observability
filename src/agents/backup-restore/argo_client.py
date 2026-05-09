"""
Argo Workflows Client for Backup/Restore Agent

Interfaces with Argo Workflows for automated backup/restore workflows.
Uses kubectl to interact with Argo Workflow CRDs.
"""

import os
import subprocess
from typing import Dict, Any, List, Optional
from datetime import datetime

import structlog

logger = structlog.get_logger(__name__)


class ArgoClient:
    """
    Client for Argo Workflows operations.
    
    Uses kubectl to interact with Argo Workflow custom resources.
    """
    
    def __init__(
        self,
        namespace: str = "argo",
    ):
        """
        Initialize Argo client.
        
        Args:
            namespace: Argo namespace (default: argo)
        """
        self.namespace = namespace
        
        logger.info(
            "argo_client_initialized",
            namespace=namespace,
        )
    
    def submit_workflow(
        self,
        workflow_name: str,
        parameters: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Submit Argo workflow.
        
        Args:
            workflow_name: Workflow template name
            parameters: Workflow parameters (optional)
        
        Returns:
            Workflow submission result
        """
        logger.info(
            "submitting_workflow",
            workflow_name=workflow_name,
        )
        
        try:
            # Build argo submit command
            cmd = [
                "argo",
                "submit",
                "--from",
                f"workflowtemplate/{workflow_name}",
                "-n",
                self.namespace,
                "--wait",
            ]
            
            # Add parameters if provided
            if parameters:
                for key, value in parameters.items():
                    cmd.extend(["-p", f"{key}={value}"])
            
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
            )
            
            if result.returncode == 0:
                # Extract workflow name from output
                workflow_id = self._extract_workflow_id(result.stdout)
                
                logger.info(
                    "workflow_submitted",
                    workflow_name=workflow_name,
                    workflow_id=workflow_id,
                )
                
                return {
                    "status": "success",
                    "workflow_id": workflow_id,
                    "message": f"Workflow {workflow_name} submitted successfully",
                    "output": result.stdout,
                }
            else:
                logger.error(
                    "workflow_submission_failed",
                    workflow_name=workflow_name,
                    error=result.stderr,
                )
                
                raise Exception(f"Workflow submission failed: {result.stderr}")
        
        except subprocess.TimeoutExpired:
            logger.error(
                "workflow_timeout",
                workflow_name=workflow_name,
            )
            raise Exception("Workflow submission timed out")
        
        except Exception as e:
            logger.error(
                "workflow_error",
                workflow_name=workflow_name,
                error=str(e),
            )
            raise
    
    def get_workflow_status(
        self,
        workflow_id: str,
    ) -> Dict[str, Any]:
        """
        Get workflow status.
        
        Args:
            workflow_id: Workflow ID
        
        Returns:
            Workflow status
        """
        logger.info(
            "getting_workflow_status",
            workflow_id=workflow_id,
        )
        
        try:
            # Build argo get command
            cmd = [
                "argo",
                "get",
                workflow_id,
                "-n",
                self.namespace,
                "--output=json",
            ]
            
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            if result.returncode == 0:
                # Parse JSON output
                import json
                data = json.loads(result.stdout)
                
                status = data.get("status", {})
                
                return {
                    "status": "success",
                    "phase": status.get("phase", "unknown"),
                    "started_at": status.get("startedAt", "unknown"),
                    "finished_at": status.get("finishedAt", "unknown"),
                    "message": status.get("message", ""),
                }
            else:
                logger.error(
                    "get_workflow_status_failed",
                    workflow_id=workflow_id,
                    error=result.stderr,
                )
                
                return {
                    "status": "error",
                    "message": result.stderr,
                }
        
        except Exception as e:
            logger.error(
                "get_workflow_status_error",
                workflow_id=workflow_id,
                error=str(e),
            )
            return {
                "status": "error",
                "message": str(e),
            }
    
    def list_workflows(
        self,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        List recent workflows.
        
        Args:
            limit: Maximum number of workflows to return
        
        Returns:
            List of workflows
        """
        logger.info("listing_workflows")
        
        try:
            # Build argo list command
            cmd = [
                "argo",
                "list",
                "-n",
                self.namespace,
                "--output=json",
            ]
            
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            if result.returncode == 0:
                # Parse JSON output
                import json
                data = json.loads(result.stdout)
                
                workflows = []
                for item in data.get("items", [])[:limit]:
                    metadata = item.get("metadata", {})
                    status = item.get("status", {})
                    
                    workflow = {
                        "name": metadata.get("name", "unknown"),
                        "namespace": metadata.get("namespace", "unknown"),
                        "created": metadata.get("creationTimestamp", "unknown"),
                        "phase": status.get("phase", "unknown"),
                        "started_at": status.get("startedAt", "unknown"),
                        "finished_at": status.get("finishedAt", "unknown"),
                    }
                    
                    workflows.append(workflow)
                
                logger.info(
                    "workflows_listed",
                    total=len(workflows),
                )
                
                return workflows
            else:
                logger.error(
                    "list_workflows_failed",
                    error=result.stderr,
                )
                
                return []
        
        except Exception as e:
            logger.error(
                "list_workflows_error",
                error=str(e),
            )
            return []
    
    def create_backup_workflow(
        self,
        backup_name: str,
        namespace: str = "nilabja-haldar-dev",
    ) -> Dict[str, Any]:
        """
        Create backup workflow.
        
        Args:
            backup_name: Backup name
            namespace: Namespace to backup
        
        Returns:
            Workflow submission result
        """
        logger.info(
            "creating_backup_workflow",
            backup_name=backup_name,
        )
        
        # Submit backup workflow with parameters
        return self.submit_workflow(
            workflow_name="backup-workflow",
            parameters={
                "backup-name": backup_name,
                "namespace": namespace,
            },
        )
    
    def create_restore_workflow(
        self,
        backup_name: str,
        namespace: str = "nilabja-haldar-dev",
    ) -> Dict[str, Any]:
        """
        Create restore workflow.
        
        Args:
            backup_name: Backup name to restore from
            namespace: Namespace to restore to
        
        Returns:
            Workflow submission result
        """
        logger.info(
            "creating_restore_workflow",
            backup_name=backup_name,
        )
        
        # Submit restore workflow with parameters
        return self.submit_workflow(
            workflow_name="restore-workflow",
            parameters={
                "backup-name": backup_name,
                "namespace": namespace,
            },
        )
    
    def _extract_workflow_id(self, output: str) -> str:
        """
        Extract workflow ID from argo submit output.
        
        Args:
            output: Command output
        
        Returns:
            Workflow ID
        """
        # Output format: "Name: workflow-name-xxxxx"
        for line in output.split("\n"):
            if line.startswith("Name:"):
                return line.split(":", 1)[1].strip()
        
        return "unknown"


# Made with Bob