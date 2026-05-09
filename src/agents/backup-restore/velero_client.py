"""
Velero Client for Backup/Restore Agent

Interfaces with Velero for backup and restore operations.
Uses kubectl commands to interact with Velero CRDs.
"""

import os
import subprocess
from typing import Dict, Any, List, Optional
from datetime import datetime

import structlog

logger = structlog.get_logger(__name__)


class VeleroClient:
    """
    Client for Velero backup/restore operations.
    
    Uses kubectl to interact with Velero custom resources.
    """
    
    def __init__(
        self,
        namespace: str = "velero",
    ):
        """
        Initialize Velero client.
        
        Args:
            namespace: Velero namespace (default: velero)
        """
        self.namespace = namespace
        self.velero_namespace = namespace
        
        logger.info(
            "velero_client_initialized",
            namespace=namespace,
        )
    
    def create_backup(
        self,
        name: str,
        namespace: str = "nilabja-haldar-dev",
        include_resources: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Create Velero backup.
        
        Args:
            name: Backup name
            namespace: Namespace to backup
            include_resources: Specific resources to include (optional)
        
        Returns:
            Backup result
        """
        logger.info(
            "creating_backup",
            name=name,
            namespace=namespace,
        )
        
        try:
            # Build velero backup command
            cmd = [
                "velero",
                "backup",
                "create",
                name,
                f"--include-namespaces={namespace}",
                "--wait",
            ]
            
            # Add specific resources if provided
            if include_resources:
                resources_str = ",".join(include_resources)
                cmd.append(f"--include-resources={resources_str}")
            
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )
            
            if result.returncode == 0:
                logger.info(
                    "backup_created",
                    name=name,
                )
                
                return {
                    "status": "success",
                    "message": f"Backup {name} created successfully",
                    "output": result.stdout,
                }
            else:
                logger.error(
                    "backup_creation_failed",
                    name=name,
                    error=result.stderr,
                )
                
                raise Exception(f"Backup creation failed: {result.stderr}")
        
        except subprocess.TimeoutExpired:
            logger.error(
                "backup_timeout",
                name=name,
            )
            raise Exception("Backup creation timed out")
        
        except Exception as e:
            logger.error(
                "backup_error",
                name=name,
                error=str(e),
            )
            raise
    
    def restore_backup(
        self,
        backup_name: str,
        namespace: str = "nilabja-haldar-dev",
        restore_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Restore from Velero backup.
        
        Args:
            backup_name: Name of backup to restore
            namespace: Namespace to restore to
            restore_name: Name for restore operation (optional)
        
        Returns:
            Restore result
        """
        if not restore_name:
            restore_name = f"restore-{backup_name}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        
        logger.info(
            "restoring_backup",
            backup_name=backup_name,
            restore_name=restore_name,
        )
        
        try:
            # Build velero restore command
            cmd = [
                "velero",
                "restore",
                "create",
                restore_name,
                f"--from-backup={backup_name}",
                f"--include-namespaces={namespace}",
                "--wait",
            ]
            
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
            )
            
            if result.returncode == 0:
                logger.info(
                    "restore_complete",
                    backup_name=backup_name,
                    restore_name=restore_name,
                )
                
                return {
                    "status": "success",
                    "message": f"Restored from {backup_name} successfully",
                    "restore_name": restore_name,
                    "output": result.stdout,
                }
            else:
                logger.error(
                    "restore_failed",
                    backup_name=backup_name,
                    error=result.stderr,
                )
                
                raise Exception(f"Restore failed: {result.stderr}")
        
        except subprocess.TimeoutExpired:
            logger.error(
                "restore_timeout",
                backup_name=backup_name,
            )
            raise Exception("Restore operation timed out")
        
        except Exception as e:
            logger.error(
                "restore_error",
                backup_name=backup_name,
                error=str(e),
            )
            raise
    
    def list_backups(
        self,
        namespace: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List available backups.
        
        Args:
            namespace: Filter by namespace (optional)
        
        Returns:
            List of backups
        """
        logger.info("listing_backups")
        
        try:
            # Build velero backup get command
            cmd = [
                "velero",
                "backup",
                "get",
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
                
                backups = []
                for item in data.get("items", []):
                    metadata = item.get("metadata", {})
                    status = item.get("status", {})
                    
                    backup = {
                        "name": metadata.get("name", "unknown"),
                        "namespace": metadata.get("namespace", "unknown"),
                        "created": metadata.get("creationTimestamp", "unknown"),
                        "status": status.get("phase", "unknown"),
                        "expiration": status.get("expiration", "never"),
                    }
                    
                    # Filter by namespace if specified
                    if namespace and backup["namespace"] != namespace:
                        continue
                    
                    backups.append(backup)
                
                logger.info(
                    "backups_listed",
                    total=len(backups),
                )
                
                return backups
            else:
                logger.error(
                    "list_backups_failed",
                    error=result.stderr,
                )
                
                # Return empty list on error
                return []
        
        except Exception as e:
            logger.error(
                "list_backups_error",
                error=str(e),
            )
            return []
    
    def get_backup_status(
        self,
        backup_name: str,
    ) -> Dict[str, Any]:
        """
        Get status of a specific backup.
        
        Args:
            backup_name: Backup name
        
        Returns:
            Backup status
        """
        logger.info(
            "getting_backup_status",
            backup_name=backup_name,
        )
        
        try:
            # Build velero backup describe command
            cmd = [
                "velero",
                "backup",
                "describe",
                backup_name,
                "--details",
            ]
            
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "details": result.stdout,
                }
            else:
                return {
                    "status": "error",
                    "message": result.stderr,
                }
        
        except Exception as e:
            logger.error(
                "get_backup_status_error",
                backup_name=backup_name,
                error=str(e),
            )
            return {
                "status": "error",
                "message": str(e),
            }
    
    def delete_backup(
        self,
        backup_name: str,
    ) -> Dict[str, Any]:
        """
        Delete a backup.
        
        Args:
            backup_name: Backup name
        
        Returns:
            Deletion result
        """
        logger.info(
            "deleting_backup",
            backup_name=backup_name,
        )
        
        try:
            # Build velero backup delete command
            cmd = [
                "velero",
                "backup",
                "delete",
                backup_name,
                "--confirm",
            ]
            
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            if result.returncode == 0:
                logger.info(
                    "backup_deleted",
                    backup_name=backup_name,
                )
                
                return {
                    "status": "success",
                    "message": f"Backup {backup_name} deleted successfully",
                }
            else:
                logger.error(
                    "backup_deletion_failed",
                    backup_name=backup_name,
                    error=result.stderr,
                )
                
                raise Exception(f"Backup deletion failed: {result.stderr}")
        
        except Exception as e:
            logger.error(
                "delete_backup_error",
                backup_name=backup_name,
                error=str(e),
            )
            raise


# Made with Bob