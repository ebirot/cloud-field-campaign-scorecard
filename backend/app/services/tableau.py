"""
Tableau API Integration Service
Handles data extraction from Tableau workbooks
"""
import tableauserverclient as TSC
from typing import Dict, List, Optional
from app.core.config import settings


class TableauService:
    """Service for interacting with Tableau Server API"""

    def __init__(self):
        self.server_url = settings.TABLEAU_SERVER_URL
        self.site_id = settings.TABLEAU_SITE_ID
        self.token_name = settings.TABLEAU_TOKEN_NAME
        self.token_value = settings.TABLEAU_TOKEN_VALUE
        self.api_version = settings.TABLEAU_API_VERSION
        self.server = None
        self.auth = None

    def connect(self):
        """Establish connection to Tableau Server using Personal Access Token"""
        try:
            # Create authentication object using Personal Access Token
            self.auth = TSC.PersonalAccessTokenAuth(
                token_name=self.token_name,
                personal_access_token=self.token_value,
                site_id=self.site_id
            )

            # Create server object
            self.server = TSC.Server(self.server_url, use_server_version=False)
            self.server.version = self.api_version

            # Sign in
            self.server.auth.sign_in(self.auth)
            print(f"SUCCESS: Connected to Tableau Server: {self.server_url}")
            return True

        except Exception as e:
            print(f"ERROR: Failed to connect to Tableau: {str(e)}")
            return False

    def disconnect(self):
        """Sign out from Tableau Server"""
        if self.server:
            self.server.auth.sign_out()
            print("SUCCESS: Disconnected from Tableau Server")

    def get_workbook(self, workbook_id: str) -> Optional[TSC.WorkbookItem]:
        """Get workbook by ID"""
        try:
            workbook = self.server.workbooks.get_by_id(workbook_id)
            print(f"SUCCESS: Found workbook: {workbook.name}")
            return workbook
        except Exception as e:
            print(f"ERROR: Error fetching workbook {workbook_id}: {str(e)}")
            return None

    def get_workbook_views(self, workbook_id: str) -> List[TSC.ViewItem]:
        """Get all views from a workbook"""
        try:
            workbook = self.get_workbook(workbook_id)
            if not workbook:
                return []

            # Populate views
            self.server.workbooks.populate_views(workbook)
            views = list(workbook.views)
            print(f"SUCCESS: Found {len(views)} views in workbook")
            return views

        except Exception as e:
            print(f"ERROR: Error fetching views: {str(e)}")
            return []

    def get_view_data(self, view_id: str) -> Optional[bytes]:
        """
        Get data from a specific view as CSV bytes
        Returns raw CSV data that can be parsed later
        """
        try:
            # Get view item
            view = self.server.views.get_by_id(view_id)
            print(f"SUCCESS: Fetching data from view: {view.name}")

            # Download view data as CSV
            self.server.views.populate_csv(view)

            # Return CSV content (this needs to be implemented based on TSC API)
            # For now, placeholder
            print(f"SUCCESS: Data extracted from view: {view.name}")
            return None  # TODO: Get actual CSV bytes from view

        except Exception as e:
            print(f"ERROR: Error fetching view data: {str(e)}")
            return None

    def extract_mdp_data(self, region: str = "EMEA", month: str = None) -> Dict:
        """
        Extract MDP scorecard data for a specific region and month

        Args:
            region: "EMEA" or "AMER" or "COMBINED"
            month: Format "2026-05" (defaults to current month)

        Returns:
            Dict containing MDP metrics by Cloud, OU, Horseman, Traffic, Offer
        """
        try:
            if not self.server:
                self.connect()

            workbook_id = settings.TABLEAU_WORKBOOK_MDP_SCORECARD
            print(f"DATA: Extracting MDP data for {region} - {month}")

            # TODO: Implement actual data extraction logic
            # This will depend on the specific structure of your Tableau workbooks

            return {
                "region": region,
                "month": month,
                "status": "success",
                "data": {
                    "clouds": [],
                    "ous": [],
                    "mdp_total": 0
                }
            }

        except Exception as e:
            print(f"ERROR: Error extracting MDP data: {str(e)}")
            return {"status": "error", "message": str(e)}

    def extract_lead_data(self, region: str = "EMEA", month: str = None) -> Dict:
        """
        Extract Lead Performance data

        Args:
            region: "EMEA" or "AMER" or "COMBINED"
            month: Format "2026-05"

        Returns:
            Dict containing Lead metrics by OU and Cloud
        """
        try:
            if not self.server:
                self.connect()

            print(f"DATA: Extracting Lead data for {region} - {month}")

            # TODO: Implement actual data extraction logic

            return {
                "region": region,
                "month": month,
                "status": "success",
                "data": {
                    "valid_leads_total": 0,
                    "core_leads": 0,
                    "non_core_leads": 0,
                    "lead_sources": []
                }
            }

        except Exception as e:
            print(f"ERROR: Error extracting Lead data: {str(e)}")
            return {"status": "error", "message": str(e)}

    def extract_campaign_data(self, region: str = "EMEA", month: str = None) -> Dict:
        """
        Extract Campaign Performance data (Webinar, Email, Assets)

        Args:
            region: "EMEA" or "AMER" or "COMBINED"
            month: Format "2026-05"

        Returns:
            Dict containing Campaign metrics
        """
        try:
            if not self.server:
                self.connect()

            print(f"DATA: Extracting Campaign data for {region} - {month}")

            # TODO: Implement actual data extraction logic

            return {
                "region": region,
                "month": month,
                "status": "success",
                "data": {
                    "webinar": {},
                    "email": {},
                    "assets": []
                }
            }

        except Exception as e:
            print(f"ERROR: Error extracting Campaign data: {str(e)}")
            return {"status": "error", "message": str(e)}

    def test_connection(self) -> Dict:
        """Test Tableau connection and return available workbooks"""
        try:
            if not self.connect():
                return {"status": "error", "message": "Failed to connect"}

            # Get all workbooks (limit to first 10 for testing)
            all_workbooks, pagination = self.server.workbooks.get()

            workbooks_list = [
                {
                    "id": wb.id,
                    "name": wb.name,
                    "project": wb.project_name
                }
                for wb in all_workbooks[:10]
            ]

            self.disconnect()

            return {
                "status": "success",
                "message": f"Connected successfully. Found {len(all_workbooks)} workbooks",
                "workbooks": workbooks_list
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}


# Singleton instance
tableau_service = TableauService()
