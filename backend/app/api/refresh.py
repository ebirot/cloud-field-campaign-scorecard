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
    Get status of scheduled refresh jobs and last update info

    Returns next run times, job information, and last refresh status
    """
    try:
        jobs = scheduler.get_scheduled_jobs()

        # Get next CSV refresh time
        next_morning = scheduler.get_next_run_time('morning_csv_refresh')

        # Get last update status
        last_status = scheduler.get_last_update_status()

        return {
            'scheduler_running': scheduler.is_running,
            'jobs': jobs,
            'next_refresh': next_morning.isoformat() if next_morning else None,
            'current_time': datetime.now().isoformat(),
            'last_update': last_status
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


@router.get("/last-insights-status")
async def get_last_insights_status():
    """
    Get detailed status of last Insights Backend refresh

    Returns workbook_found status and views count
    """
    try:
        last_status = scheduler.get_last_update_status()
        insights = last_status.get('insights', {})

        return {
            'workbook_found': insights.get('workbook_found', False),
            'views_success': insights.get('views_success', 0),
            'views_failed': insights.get('views_failed', 0),
            'views_total': insights.get('views_total', 0),
            'last_updated': last_status.get('last_updated')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get insights status: {str(e)}")
