"""
Automated Task Scheduler
Runs CSV refresh and other maintenance tasks on schedule
"""
import asyncio
import logging
from datetime import datetime, time
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.services.tableau_refresh import tableau_service

logger = logging.getLogger(__name__)


class TaskScheduler:
    """Manages scheduled tasks for the application"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False

    def start(self):
        """Start the scheduler"""
        if self.is_running:
            logger.warning("Scheduler already running")
            return

        # Schedule CSV refresh every day at 23:00 CET
        self.scheduler.add_job(
            self._run_csv_refresh,
            CronTrigger(hour=23, minute=0, timezone='Europe/Paris'),
            id='daily_csv_refresh',
            name='Daily CSV Refresh from Tableau',
            replace_existing=True
        )

        # Optional: Schedule additional refresh at 06:00 for morning data
        self.scheduler.add_job(
            self._run_csv_refresh,
            CronTrigger(hour=6, minute=0, timezone='Europe/Paris'),
            id='morning_csv_refresh',
            name='Morning CSV Refresh',
            replace_existing=True
        )

        self.scheduler.start()
        self.is_running = True
        logger.info("✅ Task scheduler started")
        logger.info("📅 CSV refresh scheduled: 06:00 CET and 23:00 CET daily")

    def stop(self):
        """Stop the scheduler"""
        if not self.is_running:
            return

        self.scheduler.shutdown()
        self.is_running = False
        logger.info("Scheduler stopped")

    def _run_csv_refresh(self):
        """Execute the CSV refresh task"""
        try:
            logger.info("🔄 Starting scheduled CSV refresh...")
            start_time = datetime.now()

            results = tableau_service.refresh_all_csvs()

            elapsed = (datetime.now() - start_time).total_seconds()
            successful = sum(1 for v in results.values() if v)
            total = len(results)

            logger.info(f"✅ CSV refresh completed: {successful}/{total} files in {elapsed:.1f}s")

            # Log any failures
            failures = [name for name, success in results.items() if not success]
            if failures:
                logger.warning(f"⚠️  Failed to refresh: {', '.join(failures)}")

        except Exception as e:
            logger.error(f"❌ Scheduled CSV refresh failed: {e}")

    def trigger_manual_refresh(self) -> dict:
        """Manually trigger a CSV refresh"""
        logger.info("🔄 Manual CSV refresh triggered")
        try:
            results = tableau_service.refresh_all_csvs()
            successful = sum(1 for v in results.values() if v)
            total = len(results)

            return {
                'success': True,
                'results': results,
                'summary': f'{successful}/{total} files refreshed',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Manual refresh failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def get_next_run_time(self, job_id: str) -> Optional[datetime]:
        """Get the next scheduled run time for a job"""
        job = self.scheduler.get_job(job_id)
        if job:
            return job.next_run_time
        return None

    def get_scheduled_jobs(self) -> list:
        """Get all scheduled jobs info"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        return jobs


# Global scheduler instance
scheduler = TaskScheduler()


# Initialize scheduler on module import
def init_scheduler():
    """Initialize and start the scheduler"""
    try:
        scheduler.start()
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")


# Cleanup on shutdown
def shutdown_scheduler():
    """Stop the scheduler gracefully"""
    scheduler.stop()
