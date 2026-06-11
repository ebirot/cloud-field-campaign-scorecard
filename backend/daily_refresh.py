"""
Daily Tableau Data Refresh Script
Runs every day at 23:00 CET to export fresh CSVs from Tableau
"""
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.tableau import TableauService
from app.core.config import settings

# View IDs from export_all_views.py
VIEW_IDS = {
    'REGIONAL_VIEW': '1_REGIONALVIEWSalesL2',
    'REGIONAL_VIEW_CLOUD': '2_REGIONALVIEWSalesL2_Cloud',
    'CLOUD_VIEW': '3_CLOUDVIEWSalesL2',
    'CLOUD_VIEW_APM': '4_CLOUDVIEWAPMDemandL2',
    'CLOUD_VIEW_APM_L2': '5_CLOUDVIEWAPMDemandL2_APML2',
    'HORSEMAN': '6_Horseman',
    'TRAFFIC_SOURCE': '7_TrafficSource',
    'OFFER': '8_OfferL1L2',
    'WEBINAR': '9_Webinar',
    'WEBINAR_LANGUAGE': '10_WebinarLanguage'
}

def log(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def export_all_views():
    """Export all Tableau views to CSV"""
    log("Starting daily Tableau data refresh...")

    # Initialize Tableau service (reads config from settings automatically)
    tableau = TableauService()

    try:
        # Connect to Tableau
        log("Connecting to Tableau Server...")
        tableau.connect()
        log(f"Connected! Server: {settings.TABLEAU_SERVER_URL}, Site: {settings.TABLEAU_SITE_ID}")

        # Get workbook
        workbook_name = "FY27 AMER + EMEA CFM MDP Scorecard Builder"
        log(f"Finding workbook: {workbook_name}")
        workbook = tableau.get_workbook(workbook_name)

        if not workbook:
            log(f"ERROR: Workbook '{workbook_name}' not found!")
            return False

        log(f"Found workbook: {workbook.name} (ID: {workbook.id})")

        # Get all views
        views = tableau.get_workbook_views(workbook.id)
        log(f"Found {len(views)} views in workbook")

        # Create data directory if doesn't exist
        data_dir = Path(__file__).parent / "data"
        data_dir.mkdir(exist_ok=True)

        # Export each view
        success_count = 0
        fail_count = 0

        for i, (key, view_name) in enumerate(VIEW_IDS.items(), 1):
            log(f"[{i}/{len(VIEW_IDS)}] Exporting {key} ({view_name})...")

            # Find matching view
            matching_view = None
            for view in views:
                if view_name.lower().replace('_', '') in view.name.lower().replace(' ', '').replace('_', ''):
                    matching_view = view
                    break

            if not matching_view:
                log(f"  WARNING: View not found for {key}")
                fail_count += 1
                continue

            # Export to CSV
            output_file = data_dir / f"{i}_{key.lower()}.csv"

            try:
                tableau.server.views.populate_csv(matching_view)
                csv_data = b''.join(matching_view.csv)

                with open(output_file, 'wb') as f:
                    f.write(csv_data)

                file_size = len(csv_data)
                log(f"  SUCCESS: Exported {file_size:,} bytes to {output_file.name}")
                success_count += 1

            except Exception as e:
                log(f"  ERROR: Failed to export {key}: {str(e)}")
                fail_count += 1

        # Summary
        log("=" * 60)
        log(f"Export complete! Success: {success_count}/{len(VIEW_IDS)}, Failed: {fail_count}")
        log("=" * 60)

        # Update last refresh timestamp
        timestamp_file = data_dir / "last_refresh.txt"
        with open(timestamp_file, 'w') as f:
            f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        log(f"Timestamp saved to {timestamp_file}")

        return fail_count == 0

    except Exception as e:
        log(f"FATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        tableau.disconnect()
        log("Disconnected from Tableau")

if __name__ == "__main__":
    log("Daily Tableau Refresh Script")
    log("=" * 60)

    success = export_all_views()

    if success:
        log("✓ All views exported successfully!")
        sys.exit(0)
    else:
        log("✗ Some views failed to export")
        sys.exit(1)
