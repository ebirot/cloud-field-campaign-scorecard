"""
Data Refresh API
Manual trigger and status endpoints for CSV refresh
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.services.scheduler import scheduler

router = APIRouter()


@router.post("/trigger")
def trigger_manual_refresh():
    """
    Manually trigger a CSV refresh from Tableau Server

    Returns status and results of the refresh operation
    """
    try:
        result = scheduler.trigger_manual_refresh()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refresh failed: {str(e)}")


@router.get("/status")
async def get_refresh_status():
    """
    Get status of scheduled refresh jobs

    Returns next run times and job information
    """
    try:
        jobs = scheduler.get_scheduled_jobs()

        # Get next CSV refresh time
        next_daily = scheduler.get_next_run_time('daily_csv_refresh')
        next_morning = scheduler.get_next_run_time('morning_csv_refresh')

        return {
            'scheduler_running': scheduler.is_running,
            'jobs': jobs,
            'next_daily_refresh': next_daily.isoformat() if next_daily else None,
            'next_morning_refresh': next_morning.isoformat() if next_morning else None,
            'current_time': datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.get("/last-update")
async def get_last_update():
    """
    Get timestamp of last data update

    Reads from the data freshness CSV file
    """
    try:
        from pathlib import Path
        freshness_file = Path(__file__).parent.parent.parent / 'data' / '10_data_freshness.csv'

        if freshness_file.exists():
            with open(freshness_file, 'r') as f:
                lines = f.readlines()
                if len(lines) > 0:
                    # Parse "Last Updated,2026-05-29 23:00:00"
                    last_updated = lines[0].strip().split(',')[1]
                    return {
                        'last_updated': last_updated,
                        'file_exists': True
                    }

        return {
            'last_updated': None,
            'file_exists': False,
            'message': 'No freshness data available'
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read freshness: {str(e)}")
