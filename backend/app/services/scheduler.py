"""
Automated Task Scheduler
Runs CSV refresh and other maintenance tasks on schedule
"""
import asyncio
import logging
import json
from pathlib import Path
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
        # Status file path
        self.status_file = Path(__file__).parent.parent.parent.parent / 'data' / 'refresh_status.json'
        self.status_file.parent.mkdir(parents=True, exist_ok=True)

    def start(self):
        """Start the scheduler"""
        if self.is_running:
            logger.warning("Scheduler already running")
            return

        # Schedule CSV refresh every day at 06:00 CET
        self.scheduler.add_job(
            self._run_csv_refresh,
            CronTrigger(hour=6, minute=0, timezone='Europe/Paris'),
            id='morning_csv_refresh',
            name='Morning CSV Refresh at 06:00 CET',
            replace_existing=True
        )

        self.scheduler.start()
        self.is_running = True
        logger.info("✅ Task scheduler started")
        logger.info("📅 CSV refresh scheduled: 06:00 CET daily")

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

            # Calculate totals
            scorecard_success = len(results.get('scorecard', {}).get('success', []))
            scorecard_failed = len(results.get('scorecard', {}).get('failed', []))
            insights_success = len(results.get('insights', {}).get('success', []))
            insights_failed = len(results.get('insights', {}).get('failed', []))

            total_success = scorecard_success + insights_success
            total_files = scorecard_success + scorecard_failed + insights_success + insights_failed

            logger.info(f"✅ CSV refresh completed: {total_success}/{total_files} files in {elapsed:.1f}s")
            logger.info(f"   Scorecard: {scorecard_success}/{scorecard_success + scorecard_failed}")
            logger.info(f"   Insights: {insights_success}/{insights_success + insights_failed}")

            # Save last update timestamp and status
            self._save_last_update(total_success, total_files, elapsed)

            # Log any failures
            all_failures = results.get('scorecard', {}).get('failed', []) + results.get('insights', {}).get('failed', [])
            if all_failures:
                logger.warning(f"⚠️  Failed to refresh: {', '.join(all_failures)}")

        except Exception as e:
            logger.error(f"❌ Scheduled CSV refresh failed: {e}")
            self._save_last_update(0, 0, 0, error=str(e))

    def trigger_manual_refresh(self) -> dict:
        """Manually trigger a CSV refresh"""
        logger.info("🔄 Manual CSV refresh triggered")
        start_time = datetime.now()
        try:
            results = tableau_service.refresh_all_csvs()

            # Calculate totals
            scorecard_success = len(results.get('scorecard', {}).get('success', []))
            scorecard_failed = len(results.get('scorecard', {}).get('failed', []))
            insights_success = len(results.get('insights', {}).get('success', []))
            insights_failed = len(results.get('insights', {}).get('failed', []))

            total_success = scorecard_success + insights_success
            total_files = scorecard_success + scorecard_failed + insights_success + insights_failed
            elapsed = (datetime.now() - start_time).total_seconds()

            # Save status
            self._save_last_update(total_success, total_files, elapsed)

            return {
                'success': True,
                'results': results,
                'summary': {
                    'scorecard': f'{scorecard_success}/{scorecard_success + scorecard_failed} views',
                    'insights': f'{insights_success}/{insights_success + insights_failed} views',
                    'total': f'{total_success}/{total_files} files'
                },
                'elapsed_seconds': elapsed,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Manual refresh failed: {e}")
            elapsed = (datetime.now() - start_time).total_seconds()
            self._save_last_update(0, 0, elapsed, error=str(e))
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

    def _save_last_update(self, successful: int, total: int, elapsed: float, error: str = None):
        """Save last refresh status to file"""
        try:
            status = {
                'last_updated': datetime.now().isoformat(),
                'successful': successful,
                'total': total,
                'elapsed_seconds': elapsed,
                'success': successful == total and total > 0,
                'error': error
            }
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(status, f, indent=2)
            logger.info(f"💾 Saved refresh status: {successful}/{total} files")
        except Exception as e:
            logger.error(f"Failed to save refresh status: {e}")

    def get_last_update_status(self) -> dict:
        """Get last refresh status from file"""
        try:
            if self.status_file.exists():
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read refresh status: {e}")

        return {
            'last_updated': None,
            'successful': 0,
            'total': 0,
            'elapsed_seconds': 0,
            'success': False,
            'error': None
        }


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
