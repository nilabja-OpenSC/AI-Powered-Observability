"""
Backup Scheduler for Backup/Restore Agent

Schedules automated backups at regular intervals.
Sends notifications on backup completion or failure.
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

import structlog

from agents.backup_restore.velero_client import VeleroClient
from agents.common.tools.slack import SlackTool

logger = structlog.get_logger(__name__)


class BackupScheduler:
    """
    Schedules automated backups.
    
    Runs backups at configured intervals and sends notifications.
    """
    
    def __init__(
        self,
        velero_client: VeleroClient,
        slack_tool: Optional[SlackTool] = None,
        schedule_interval_hours: int = 24,
    ):
        """
        Initialize backup scheduler.
        
        Args:
            velero_client: Velero client
            slack_tool: Slack tool for notifications (optional)
            schedule_interval_hours: Backup interval in hours (default: 24)
        """
        self.velero_client = velero_client
        self.slack_tool = slack_tool
        self.schedule_interval_hours = schedule_interval_hours
        self.is_running = False
        
        logger.info(
            "backup_scheduler_initialized",
            interval_hours=schedule_interval_hours,
        )
    
    async def start(self):
        """Start the backup scheduler."""
        if self.is_running:
            logger.warning("backup_scheduler_already_running")
            return
        
        self.is_running = True
        
        logger.info("backup_scheduler_started")
        
        # Run scheduler loop
        await self._scheduler_loop()
    
    async def stop(self):
        """Stop the backup scheduler."""
        self.is_running = False
        logger.info("backup_scheduler_stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop."""
        while self.is_running:
            try:
                # Run scheduled backup
                await self._run_scheduled_backup()
                
                # Wait for next interval
                await asyncio.sleep(self.schedule_interval_hours * 3600)
            
            except Exception as e:
                logger.error(
                    "scheduler_loop_error",
                    error=str(e),
                )
                
                # Wait before retrying
                await asyncio.sleep(300)  # 5 minutes
    
    async def _run_scheduled_backup(self):
        """Run scheduled backup."""
        backup_name = f"scheduled-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        
        logger.info(
            "running_scheduled_backup",
            backup_name=backup_name,
        )
        
        try:
            # Create backup
            result = self.velero_client.create_backup(
                name=backup_name,
                namespace="nilabja-haldar-dev",
            )
            
            # Send success notification
            if self.slack_tool:
                self.slack_tool.send_success_notification(
                    action_type="Scheduled Backup",
                    summary=f"Backup {backup_name} completed successfully",
                    details={
                        "backup_name": backup_name,
                        "namespace": "nilabja-haldar-dev",
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )
            
            logger.info(
                "scheduled_backup_complete",
                backup_name=backup_name,
            )
        
        except Exception as e:
            logger.error(
                "scheduled_backup_error",
                backup_name=backup_name,
                error=str(e),
            )
            
            # Send error notification
            if self.slack_tool:
                self.slack_tool.send_issue_notification(
                    issue_type="Scheduled Backup Failed",
                    severity="high",
                    summary=f"Backup {backup_name} failed",
                    affected_resources=["namespace/nilabja-haldar-dev"],
                    details={"error": str(e)},
                )
    
    def create_manual_backup(
        self,
        name: Optional[str] = None,
        namespace: str = "nilabja-haldar-dev",
    ) -> Dict[str, Any]:
        """
        Create manual backup (outside of schedule).
        
        Args:
            name: Backup name (optional)
            namespace: Namespace to backup
        
        Returns:
            Backup result
        """
        if not name:
            name = f"manual-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        
        logger.info(
            "creating_manual_backup",
            name=name,
        )
        
        try:
            result = self.velero_client.create_backup(
                name=name,
                namespace=namespace,
            )
            
            # Send notification
            if self.slack_tool:
                self.slack_tool.send_success_notification(
                    action_type="Manual Backup",
                    summary=f"Backup {name} completed successfully",
                    details={
                        "backup_name": name,
                        "namespace": namespace,
                    },
                )
            
            return result
        
        except Exception as e:
            logger.error(
                "manual_backup_error",
                name=name,
                error=str(e),
            )
            
            # Send error notification
            if self.slack_tool:
                self.slack_tool.send_issue_notification(
                    issue_type="Manual Backup Failed",
                    severity="high",
                    summary=f"Backup {name} failed",
                    affected_resources=[f"namespace/{namespace}"],
                    details={"error": str(e)},
                )
            
            raise
    
    def get_backup_schedule(self) -> Dict[str, Any]:
        """
        Get backup schedule information.
        
        Returns:
            Schedule info
        """
        return {
            "enabled": self.is_running,
            "interval_hours": self.schedule_interval_hours,
            "next_backup": self._calculate_next_backup_time(),
        }
    
    def _calculate_next_backup_time(self) -> str:
        """
        Calculate next scheduled backup time.
        
        Returns:
            Next backup time (ISO format)
        """
        if not self.is_running:
            return "Not scheduled"
        
        # Calculate next backup time
        next_time = datetime.utcnow() + timedelta(hours=self.schedule_interval_hours)
        return next_time.isoformat()
    
    def cleanup_old_backups(
        self,
        retention_days: int = 30,
    ) -> Dict[str, Any]:
        """
        Cleanup backups older than retention period.
        
        Args:
            retention_days: Retention period in days
        
        Returns:
            Cleanup result
        """
        logger.info(
            "cleaning_up_old_backups",
            retention_days=retention_days,
        )
        
        try:
            # List all backups
            backups = self.velero_client.list_backups()
            
            # Calculate cutoff date
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            deleted_count = 0
            for backup in backups:
                # Parse creation timestamp
                created_str = backup.get("created", "")
                try:
                    created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                    
                    # Delete if older than retention period
                    if created < cutoff_date:
                        self.velero_client.delete_backup(backup["name"])
                        deleted_count += 1
                        
                        logger.info(
                            "backup_deleted",
                            backup_name=backup["name"],
                            age_days=(datetime.utcnow() - created).days,
                        )
                
                except Exception as e:
                    logger.warning(
                        "backup_date_parse_error",
                        backup_name=backup["name"],
                        error=str(e),
                    )
            
            # Send notification
            if self.slack_tool and deleted_count > 0:
                self.slack_tool.send_success_notification(
                    action_type="Backup Cleanup",
                    summary=f"Deleted {deleted_count} old backup(s)",
                    details={
                        "retention_days": retention_days,
                        "deleted_count": deleted_count,
                    },
                )
            
            logger.info(
                "cleanup_complete",
                deleted_count=deleted_count,
            )
            
            return {
                "status": "success",
                "deleted_count": deleted_count,
                "message": f"Deleted {deleted_count} old backup(s)",
            }
        
        except Exception as e:
            logger.error(
                "cleanup_error",
                error=str(e),
            )
            raise


# Made with Bob