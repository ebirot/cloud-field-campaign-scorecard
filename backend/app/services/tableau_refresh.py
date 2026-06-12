"""
Tableau Server CSV Refresh Service
Downloads CSV exports from Tableau Server views using official SDK
"""
import tableauserverclient as TSC
import os
import logging
from pathlib import Path
from typing import Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

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

        # Insights Backend workbook (for AI-generated insights)
        self.insights_workbook_name = "FY27 AMER + EMEA CFM MDP Insights Back End"
        self.insights_workbook_id = "65b63465-7926-4997-8cc5-625f177fd072"

        # Point to centralized data folder at project root
        self.data_dir = Path(__file__).parent.parent.parent.parent / 'data' / 'csv'

    def refresh_all_csvs(self) -> Dict:
        """Download all CSV files from Tableau Server using official SDK - in parallel"""
        results = {
            'scorecard': {
                'success': [],
                'failed': []
            },
            'insights': {
                'success': [],
                'failed': [],
                'workbook_found': False,
                'views_count': 0
            }
        }

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

                # Get all views from the main scorecard workbook
                print(f"[TABLEAU] Fetching views from workbook {self.workbook_id}")
                workbook = server.workbooks.get_by_id(self.workbook_id)
                server.workbooks.populate_views(workbook)

                print(f"[TABLEAU] Found {len(workbook.views)} views in main workbook")
                logger.info(f"INFO Found {len(workbook.views)} views in main workbook")

                # Prepare tasks for parallel download
                scorecard_views = []
                for view in workbook.views:
                    if view.name in self.view_mappings:
                        scorecard_views.append((view, self.view_mappings[view.name]))

                print(f"[TABLEAU] Starting PARALLEL download of {len(scorecard_views)} scorecard views + Insights Backend...")
                logger.info(f"Starting parallel download: {len(scorecard_views)} scorecard + Insights Backend")

                # Use ThreadPoolExecutor for parallel downloads
                with ThreadPoolExecutor(max_workers=5) as executor:
                    futures = {}

                    # Submit scorecard view downloads
                    for view, output_filename in scorecard_views:
                        future = executor.submit(self._download_single_view, server, view, output_filename)
                        futures[future] = ('scorecard', view.name)

                    # Submit Insights Backend download
                    insights_future = executor.submit(self.download_insights_backend_detailed, server)
                    futures[insights_future] = ('insights', 'Insights Backend')

                    # Collect results as they complete
                    for future in as_completed(futures):
                        task_type, task_name = futures[future]
                        try:
                            result = future.result()

                            if task_type == 'scorecard':
                                if result:
                                    results['scorecard']['success'].append(task_name)
                                    print(f"[TABLEAU] ✅ {task_name} downloaded successfully")
                                    logger.info(f"✅ {task_name} downloaded successfully")
                                else:
                                    results['scorecard']['failed'].append(task_name)
                                    print(f"[TABLEAU] ❌ {task_name} failed")
                                    logger.error(f"❌ {task_name} failed")

                            elif task_type == 'insights':
                                # Result is now a dict with details
                                results['insights'] = result
                                if result.get('workbook_found'):
                                    print(f"[TABLEAU] ✅ Insights Backend: {len(result['success'])} views downloaded")
                                    logger.info(f"✅ Insights Backend: {len(result['success'])} views downloaded")
                                else:
                                    print(f"[TABLEAU] ❌ Insights Backend workbook not found")
                                    logger.error(f"❌ Insights Backend workbook not found")

                        except Exception as e:
                            print(f"[TABLEAU] ERROR {task_name} error: {e}")
                            logger.error(f"{task_name} error: {e}")
                            if task_type == 'scorecard':
                                results['scorecard']['failed'].append(task_name)

                print(f"[TABLEAU] COMPLETE Parallel refresh complete!")
                logger.info("COMPLETE Parallel CSV refresh complete (Scorecard + Insights)")

        except Exception as e:
            print(f"[TABLEAU] ERROR Tableau refresh error: {e}")
            logger.error(f"Tableau refresh error: {e}")

        return results

    def _download_single_view(self, server: TSC.Server, view: TSC.ViewItem, output_filename: str) -> bool:
        """
        Download a single view as CSV (helper for parallel execution)

        Args:
            server: Authenticated Tableau server instance
            view: View item to download
            output_filename: Local filename to save

        Returns:
            True if successful, False otherwise
        """
        try:
            output_path = self.data_dir / output_filename

            # Get full view details
            view = server.views.get_by_id(view.id)

            # Download as CSV
            server.views.populate_csv(view)
            csv_data = b''.join(view.csv).decode('utf-8-sig')

            # Save to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(csv_data)

            file_size = len(csv_data) / 1024  # KB
            print(f"[TABLEAU] OK Downloaded {view.name} -> {output_filename} ({file_size:.1f} KB)")
            logger.info(f"OK Downloaded {view.name} -> {output_filename} ({file_size:.1f} KB)")
            return True

        except Exception as e:
            print(f"[TABLEAU] ERROR Error downloading {view.name}: {e}")
            logger.error(f"Error downloading {view.name}: {e}")
            return False

    def download_insights_backend_detailed(self, server: TSC.Server) -> Dict:
        """
        Download FY27 AMER + EMEA CFM MDP Insights Back End workbook CSV
        Returns detailed results for UI display

        Args:
            server: Authenticated Tableau server instance

        Returns:
            Dict with success/failed lists and metadata
        """
        result = {
            'workbook_found': False,
            'views_count': 0,
            'success': [],
            'failed': []
        }

        try:
            print(f"[TABLEAU] Fetching Insights workbook by ID: {self.insights_workbook_id}")
            logger.info(f"Fetching Insights workbook by ID: {self.insights_workbook_id}")

            # Get workbook directly by ID (more reliable than name search)
            try:
                insights_workbook = server.workbooks.get_by_id(self.insights_workbook_id)
                print(f"[TABLEAU] OK Found workbook: {insights_workbook.name} (ID: {insights_workbook.id})")
                logger.info(f"Found insights workbook: {insights_workbook.name} (ID: {insights_workbook.id})")
            except Exception as e:
                print(f"[TABLEAU] ERROR Insights workbook not found with ID {self.insights_workbook_id}: {e}")
                logger.error(f"Insights workbook not found with ID {self.insights_workbook_id}: {e}")
                return result

            result['workbook_found'] = True

            # Get all views from this workbook
            server.workbooks.populate_views(insights_workbook)
            views = list(insights_workbook.views)

            if not views:
                print(f"[TABLEAU] ERROR No views found in insights workbook")
                logger.error("No views found in insights workbook")
                return result

            result['views_count'] = len(views)
            print(f"[TABLEAU] INFO Found {len(views)} views in insights workbook")
            logger.info(f"Found {len(views)} views in insights workbook")

            # Download all views from this workbook
            for idx, view in enumerate(views, 1):
                try:
                    print(f"[TABLEAU] Downloading insights view {idx}/{len(views)}: {view.name}")

                    # Get full view details
                    view = server.views.get_by_id(view.id)

                    # Download as CSV
                    server.views.populate_csv(view)
                    csv_data = b''.join(view.csv).decode('utf-8-sig')

                    # Save to file with numbered prefix
                    safe_filename = f"insights_{idx:02d}_{view.name.replace(' ', '_').replace('/', '_')[:50]}.csv"
                    output_path = self.data_dir / safe_filename

                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(csv_data)

                    file_size = len(csv_data) / 1024  # KB
                    print(f"[TABLEAU] OK Downloaded {view.name} -> {safe_filename} ({file_size:.1f} KB)")
                    logger.info(f"OK Downloaded insights view: {view.name} -> {safe_filename} ({file_size:.1f} KB)")

                    result['success'].append(view.name)

                except Exception as e:
                    print(f"[TABLEAU] ERROR Error downloading insights view {view.name}: {e}")
                    logger.error(f"Error downloading insights view {view.name}: {e}")
                    result['failed'].append(view.name)

        except Exception as e:
            print(f"[TABLEAU] ERROR Failed to download insights backend: {e}")
            logger.error(f"Failed to download insights backend: {e}")

        return result

    def download_insights_backend(self, server: TSC.Server) -> bool:
        """
        Download FY27 AMER + EMEA CFM MDP Insights Back End workbook CSV
        This contains unlocked data for AI-generated insights (Highs/Lows/Next Steps)

        Args:
            server: Authenticated Tableau server instance

        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"[TABLEAU] Fetching Insights workbook by ID: {self.insights_workbook_id}")
            logger.info(f"Fetching Insights workbook by ID: {self.insights_workbook_id}")

            # Get workbook directly by ID (more reliable than name search)
            try:
                insights_workbook = server.workbooks.get_by_id(self.insights_workbook_id)
                print(f"[TABLEAU] OK Found workbook: {insights_workbook.name} (ID: {insights_workbook.id})")
                logger.info(f"Found insights workbook: {insights_workbook.name} (ID: {insights_workbook.id})")
            except Exception as e:
                print(f"[TABLEAU] ERROR Insights workbook not found with ID {self.insights_workbook_id}: {e}")
                logger.error(f"Insights workbook not found with ID {self.insights_workbook_id}: {e}")
                return False

            # Get all views from this workbook
            server.workbooks.populate_views(insights_workbook)
            views = list(insights_workbook.views)

            if not views:
                print(f"[TABLEAU] ERROR No views found in insights workbook")
                logger.error("No views found in insights workbook")
                return False

            print(f"[TABLEAU] INFO Found {len(views)} views in insights workbook")
            logger.info(f"Found {len(views)} views in insights workbook")

            # Download all views from this workbook
            for idx, view in enumerate(views, 1):
                try:
                    print(f"[TABLEAU] Downloading insights view {idx}/{len(views)}: {view.name}")

                    # Get full view details
                    view = server.views.get_by_id(view.id)

                    # Download as CSV
                    server.views.populate_csv(view)
                    csv_data = b''.join(view.csv).decode('utf-8-sig')

                    # Save to file with numbered prefix
                    safe_filename = f"insights_{idx:02d}_{view.name.replace(' ', '_').replace('/', '_')[:50]}.csv"
                    output_path = self.data_dir / safe_filename

                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(csv_data)

                    file_size = len(csv_data) / 1024  # KB
                    print(f"[TABLEAU] OK Downloaded {view.name} -> {safe_filename} ({file_size:.1f} KB)")
                    logger.info(f"Downloaded insights view: {view.name} -> {safe_filename} ({file_size:.1f} KB)")

                except Exception as e:
                    print(f"[TABLEAU] ERROR Error downloading insights view {view.name}: {e}")
                    logger.error(f"Error downloading insights view {view.name}: {e}")

            return True

        except Exception as e:
            print(f"[TABLEAU] ERROR Failed to download insights backend: {e}")
            logger.error(f"Failed to download insights backend: {e}")
            return False


# Global instance
tableau_service = TableauRefreshService()
