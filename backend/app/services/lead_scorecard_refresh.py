"""
Lead Scorecard Tableau CSV Refresh Service
Downloads CSV exports for Lead Scorecard views from Tableau Server
"""
import tableauserverclient as TSC
import os
import logging
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)


class LeadScorecardRefreshService:
    """Service to download Lead Scorecard CSV files from Tableau Server"""

    def __init__(self):
        self.server_url = os.getenv('TABLEAU_SERVER_URL', 'https://prod-uswest-c.online.tableau.com')
        self.site_id = os.getenv('TABLEAU_SITE_ID', 'salesforce')
        self.token_name = os.getenv('TABLEAU_TOKEN_NAME', 'Token_Claude_CFM_Scorecard')
        self.token_value = os.getenv('TABLEAU_TOKEN_VALUE')

        # Workbook configurations: workbook_id, view_name, output filename
        self.workbook_configs = [
            {
                'key': 'leaderboard_cloud',
                'workbook_id': 'a78452dc-76a4-4462-ae68-1bd2b4f661bc',
                'view_name': 'Leaderboard by APM L1',
                'filename': 'lead_leaderboard_cloud.csv'
            },
            {
                'key': 'leaderboard_ou',
                'workbook_id': 'cff6e09c-34f6-4abb-bbfb-b5c22ba83efb',
                'view_name': 'Leaderboard by OU',
                'filename': 'lead_leaderboard_ou.csv'
            },
            {
                'key': 'core_noncore',
                'workbook_id': 'e6c67272-4bce-4e94-93c5-3b1f4a69f6ef',
                'view_name': 'Core /Non-Core',
                'filename': 'lead_core_noncore.csv'
            },
            {
                'key': 'lead_source',
                'workbook_id': '6f6f1132-0739-4876-bddb-303daaa53d6e',
                'view_name': 'Top Lead Source',
                'filename': 'lead_source.csv'
            },
            {
                'key': 'lead_score',
                'workbook_id': 'a96ce92a-b426-4c5f-8fb9-86e60494d588',
                'view_name': 'Lead Score',
                'filename': 'lead_score.csv'
            },
            {
                'key': 'traffic_flag',
                'workbook_id': 'fa27e5b7-a9f1-44ac-9158-c254a9f7971b',
                'view_name': 'Top Lead Source',
                'filename': 'lead_traffic_flag.csv'
            }
        ]

        # Point to centralized data folder at project root
        self.data_dir = Path(__file__).parent.parent.parent.parent / 'data' / 'csv'

    def refresh_all_csvs(self) -> Dict[str, bool]:
        """Download all Lead Scorecard CSV files from Tableau Server"""
        results = {}

        try:
            # Create authentication object using Personal Access Token
            tableau_auth = TSC.PersonalAccessTokenAuth(
                self.token_name,
                self.token_value,
                site_id=self.site_id
            )

            # Create server object
            server = TSC.Server(self.server_url, use_server_version=True)

            print(f"[LEAD SCORECARD] Signing in to {self.server_url} / {self.site_id}")
            logger.info(f"Connecting to Tableau Server: {self.server_url}")

            with server.auth.sign_in(tableau_auth):
                print(f"[LEAD SCORECARD] OK Signed in successfully")
                logger.info("OK Tableau authentication successful")

                # Download each workbook's view
                for config in self.workbook_configs:
                    workbook_id = config['workbook_id']
                    view_name = config['view_name']
                    output_filename = config['filename']
                    key = config['key']

                    try:
                        print(f"[LEAD SCORECARD] Fetching workbook {key}...")
                        workbook = server.workbooks.get_by_id(workbook_id)
                        server.workbooks.populate_views(workbook)

                        # Find the matching view
                        matching_view = None
                        for view in workbook.views:
                            if view_name.lower() in view.name.lower() or view.name.lower() in view_name.lower():
                                matching_view = view
                                break

                        if not matching_view:
                            print(f"[LEAD SCORECARD] WARNING  View '{view_name}' not found in workbook, skipping")
                            logger.warning(f"View '{view_name}' not found in workbook")
                            results[key] = False
                            continue

                        output_path = self.data_dir / output_filename

                        print(f"[LEAD SCORECARD] Downloading {view_name}...")

                        # Download as CSV
                        server.views.populate_csv(matching_view)
                        csv_data = b''.join(matching_view.csv).decode('utf-8-sig')

                        # Save to file
                        with open(output_path, 'w', encoding='utf-8') as f:
                            f.write(csv_data)

                        file_size = len(csv_data) / 1024  # KB
                        print(f"[LEAD SCORECARD] OK Downloaded {view_name} -> {output_filename} ({file_size:.1f} KB)")
                        logger.info(f"OK Downloaded {view_name} -> {output_filename} ({file_size:.1f} KB)")
                        results[key] = True

                    except Exception as e:
                        print(f"[LEAD SCORECARD] ERROR Error downloading {key}: {e}")
                        logger.error(f"Error downloading {key}: {e}")
                        results[key] = False

                print(f"[LEAD SCORECARD] COMPLETE Refresh complete!")
                logger.info("COMPLETE Lead Scorecard CSV refresh complete")

        except Exception as e:
            print(f"[LEAD SCORECARD] ERROR Tableau refresh error: {e}")
            logger.error(f"Tableau refresh error: {e}")

        return results


# Global instance
lead_scorecard_service = LeadScorecardRefreshService()
