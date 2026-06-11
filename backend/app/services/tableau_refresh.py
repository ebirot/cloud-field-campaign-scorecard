"""
Tableau Server CSV Refresh Service
Downloads CSV exports from Tableau Server views using official SDK
"""
import tableauserverclient as TSC
import os
import logging
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)


class TableauRefreshService:
    """Service to download CSV files from Tableau Server"""

    def __init__(self):
        self.server_url = os.getenv('TABLEAU_SERVER_URL', 'https://prod-uswest-c.online.tableau.com')
        self.site_id = os.getenv('TABLEAU_SITE_ID', 'salesforce')
        self.token_name = os.getenv('TABLEAU_TOKEN_NAME', 'Token_Claude_CFM_Scorecard')
        self.token_value = os.getenv('TABLEAU_TOKEN_VALUE')
        self.workbook_id = os.getenv('TABLEAU_WORKBOOK_MDP_SCORECARD')

        # CSV file mapping: View name -> Local filename
        self.view_mappings = {
            '1. REGIONAL VIEW (Sales L2)': '1_regional_sales_l2.csv',
            '1. REGIONAL VIEW (Sales L2 & Cloud)': '2_regional_sales_l2_cloud.csv',
            '1. REGIONAL VIEW (Sales L3)': '3_regional_sales_l3.csv',
            '2. CLOUD VIEW APM L1': '4_cloud_view_l1.csv',
            '2. CLOUD VIEW APM L2': '5_cloud_view_l2.csv',
            '3. HORSEMAN': '6_horseman.csv',
            '4. TRAFFIC SOURCE': '7_traffic_source.csv',
            '5.OFFER L1/L2': '8_offer_l1_l2.csv',
            '6.WEBINAR': '9_webinar.csv',
            'Data Freshness': '10_data_freshness.csv'
        }

        # Point to centralized data folder at project root
        self.data_dir = Path(__file__).parent.parent.parent.parent / 'data' / 'csv'

    def refresh_all_csvs(self) -> Dict[str, bool]:
        """Download all CSV files from Tableau Server using official SDK"""
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

            print(f"[TABLEAU] Signing in to {self.server_url} / {self.site_id}")
            logger.info(f"Connecting to Tableau Server: {self.server_url}")

            with server.auth.sign_in(tableau_auth):
                print(f"[TABLEAU] OK Signed in successfully")
                logger.info("OK Tableau authentication successful")

                # Get all views from the workbook
                print(f"[TABLEAU] Fetching views from workbook {self.workbook_id}")
                workbook = server.workbooks.get_by_id(self.workbook_id)
                server.workbooks.populate_views(workbook)

                print(f"[TABLEAU] Found {len(workbook.views)} views in workbook")
                logger.info(f"INFO Found {len(workbook.views)} views in workbook")

                # Download each view that's in our mapping
                for view in workbook.views:
                    view_name = view.name

                    if view_name not in self.view_mappings:
                        print(f"[TABLEAU] WARNING  View '{view_name}' not in mapping, skipping")
                        logger.warning(f"View '{view_name}' not in mapping, skipping")
                        continue

                    output_filename = self.view_mappings[view_name]
                    output_path = self.data_dir / output_filename

                    try:
                        print(f"[TABLEAU] Downloading {view_name}...")

                        # Populate the view to get full details
                        view = server.views.get_by_id(view.id)

                        # Download as CSV
                        server.views.populate_csv(view)
                        csv_data = b''.join(view.csv).decode('utf-8-sig')

                        # Save to file
                        with open(output_path, 'w', encoding='utf-8') as f:
                            f.write(csv_data)

                        file_size = len(csv_data) / 1024  # KB
                        print(f"[TABLEAU] OK Downloaded {view_name} -> {output_filename} ({file_size:.1f} KB)")
                        logger.info(f"OK Downloaded {view_name} -> {output_filename} ({file_size:.1f} KB)")
                        results[view_name] = True

                    except Exception as e:
                        print(f"[TABLEAU] ERROR Error downloading {view_name}: {e}")
                        logger.error(f"Error downloading {view_name}: {e}")
                        results[view_name] = False

                print(f"[TABLEAU] COMPLETE Refresh complete!")
                logger.info("COMPLETE CSV refresh complete")

        except Exception as e:
            print(f"[TABLEAU] ERROR Tableau refresh error: {e}")
            logger.error(f"Tableau refresh error: {e}")

        return results


# Global instance
tableau_service = TableauRefreshService()
