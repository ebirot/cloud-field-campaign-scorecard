"""
Safe CSV Parser - Returns empty data when CSV files don't exist
Wrapper around csv_parser.py for Heroku deployment without CSV files
"""
from pathlib import Path
from typing import Dict, List, Any


class SafeCSVParser:
    """Wrapper that handles missing CSV files gracefully"""

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            self.data_dir = Path(__file__).parent.parent.parent.parent / 'data' / 'csv'
        else:
            self.data_dir = Path(data_dir)

    def parse_regional_cloud_view(self, quarters: list = None, fiscal_year: str = None) -> Dict:
        """Return empty regional data"""
        return {"leaders": [], "data": {}}

    def parse_horseman(self, cloud_filter: str = None, leaders_filter: list = None, quarters: list = None, fiscal_year: str = 'FY 2027') -> Dict:
        """Return empty horseman data"""
        return {"data": [], "totals": {"mdp": 0, "yoy_change": 0}}

    def parse_traffic_source(self, cloud_filter: str = None, leaders_filter: list = None, quarters: list = None, fiscal_year: str = 'FY 2027') -> Dict:
        """Return empty traffic source data"""
        return {"data": [], "totals": {"mdp": 0}}

    def parse_offer(self, cloud_filter: str = None, leaders_filter: list = None, quarters: list = None, fiscal_year: str = 'FY 2027') -> Dict:
        """Return empty offer data"""
        return {"data": [], "totals": {"mdp": 0}}

    def parse_webinar(self, cloud_filter: str = None, leaders_filter: list = None, quarters: list = None) -> Dict:
        """Return empty webinar data"""
        return {"data": [], "totals": {"total_registrations": 0, "total_attended": 0, "total_mdp": 0}}

    def get_available_clouds(self) -> List[str]:
        """Return default cloud list"""
        return ['Agentforce', 'Sales', 'Service', 'Marketing', 'Commerce', 'Data', 'Platform', 'Mulesoft', 'Tableau', 'Slack']

    def get_summary_stats(self) -> Dict:
        """Return empty summary stats"""
        return {
            "total_mdp": 0,
            "total_leads": 0,
            "total_campaigns": 0,
            "yoy_growth": 0
        }
