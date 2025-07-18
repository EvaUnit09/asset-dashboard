"""
APScheduler-based sync scheduler for asset management system.
This module provides in-application scheduling functionality.
"""

import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from .sync import sync_all

logger = logging.getLogger(__name__)

class SyncScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_listener(self._job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        self._setup_sync_jobs()
        
    def _setup_sync_jobs(self):
        """Set up scheduled sync jobs with configurable frequency."""
        # Reduced frequency: only 2 times daily (8am and 8pm) to reduce CPU load
        times = ["08:00", "20:00"]
        
        for time in times:
            hour, minute = map(int, time.split(':'))
            trigger = CronTrigger(hour=hour, minute=minute)
            
            self.scheduler.add_job(
                func=self._sync_with_logging,
                trigger=trigger,
                id=f"sync_{time.replace(':', '')}",
                name=f"Full Sync (Assets + Users) {time}",
                replace_existing=True,
                max_instances=1,  # Prevent overlapping syncs
                misfire_grace_time=300  # 5 minutes grace period
            )
            
        logger.info("Scheduled full sync jobs (assets + users) set up for 8:00 AM and 8:00 PM")
    
    def _sync_with_logging(self):
        """Wrapper function for sync with proper logging and error handling."""
        try:
            logger.info("Starting scheduled full sync (assets + users)...")
            start_time = datetime.now()
            
            # Add memory and performance monitoring
            import psutil
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            sync_all()
            
            end_time = datetime.now()
            duration = end_time - start_time
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_used = final_memory - initial_memory
            
            logger.info(f"Full sync completed successfully in {duration.total_seconds():.2f} seconds")
            logger.info(f"Memory usage: {memory_used:.1f} MB increase")
            
        except Exception as e:
            logger.error(f"Full sync failed with error: {str(e)}", exc_info=True)
            # Don't re-raise to prevent scheduler from stopping
            return
    
    def _job_listener(self, event):
        """Listen for job execution events."""
        if event.exception:
            logger.error(f"Job {event.job_id} failed: {event.exception}")
        else:
            logger.info(f"Job {event.job_id} executed successfully")
    
    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Sync scheduler started")
    
    def stop(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Sync scheduler stopped")
    
    def trigger_sync_now(self):
        """Manually trigger a sync job."""
        self.scheduler.add_job(
            func=self._sync_with_logging,
            id="manual_sync",
            name="Manual Asset Sync",
            replace_existing=True
        )
        logger.info("Manual sync job triggered")
    
    def get_next_run_times(self):
        """Get the next scheduled run times."""
        jobs = self.scheduler.get_jobs()
        return {job.name: job.next_run_time for job in jobs if job.next_run_time}

# Global scheduler instance
sync_scheduler = SyncScheduler() 