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

    def parse_horseman_view(self, cloud: str = None, quarters: list = None, leaders: list = None) -> List:
        """Return empty horseman data"""
        return []

    def parse_traffic_source_view(self, cloud: str = None, quarters: list = None, leaders: list = None) -> List:
        """Return empty traffic source data"""
        return []

    def parse_offer_l1_l2_view(self, cloud: str = None, quarters: list = None, leaders: list = None) -> List:
        """Return empty offer data"""
        return []

    def parse_webinar_view(self, quarters: list = None) -> List:
        """Return empty webinar data"""
        return []

    def get_available_clouds(self) -> List[str]:
        """Return default cloud list"""
        return ['Agentforce', 'Sales', 'Service', 'Marketing', 'Commerce', 'Data', 'Platform', 'Mulesoft', 'Tableau', 'Slack']
