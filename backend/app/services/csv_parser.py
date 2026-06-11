"""
CSV Parser Service
Parses exported Tableau CSV files and structures data
"""
import csv
from pathlib import Path
from typing import Dict, List, Any
from decimal import Decimal


class CSVParser:
    """Parse Tableau CSV exports"""

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # Point to centralized data/csv folder at project root
            self.data_dir = Path(__file__).parent.parent.parent.parent / 'data' / 'csv'
        else:
            self.data_dir = Path(data_dir)

    def parse_regional_cloud_view(self, quarters: list = None, fiscal_year: str = None) -> List[Dict[str, Any]]:
        """
        Parse REGIONAL VIEW (Sales L2 & Cloud) with Quarter filter
        Structure: APM L1, Measure Names, Quarter, OvA Level 2 Username, Measure Values

        Args:
            quarters: List of quarters to include (e.g., ['Q2'] or ['Q1', 'Q2'])
            fiscal_year: Not used (kept for compatibility)
        """
        file_path = self.data_dir / "2_regional_sales_l2_cloud.csv"

        # Default to Q2 only
        if quarters is None:
            quarters = ['Q2']

        # Structure: {(leader, cloud, quarter): metrics}
        data_by_quarter = {}

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                cloud = row['APM L1']
                measure = row['Measure Names']
                quarter = row.get('Opportunity Stage 2 Date - Fiscal Quarter', '').strip()
                leader = row['OvA Level 2 Username']
                value_str = row['Measure Values'].replace(',', '')

                # Filter by quarter only (no FY column anymore)
                if quarter not in quarters:
                    continue

                # Try to parse as number
                try:
                    value = float(value_str) if value_str else None
                except:
                    value = None

                # Key by leader + cloud + quarter
                key = (leader, cloud, quarter)

                if key not in data_by_quarter:
                    data_by_quarter[key] = {}

                # Store metrics
                if measure == 'Current FY MDP':
                    data_by_quarter[key]['mdp'] = value
                elif measure == '% YoY':
                    data_by_quarter[key]['yoy_change'] = value
                elif measure == 'CFY MDP Contribution':
                    data_by_quarter[key]['contribution'] = value
                elif measure == 'MDP Contr. Diff vs FY-1 (ppts)':
                    data_by_quarter[key]['contribution_diff'] = value

        # Aggregate by leader + cloud across selected quarters
        aggregated = {}
        for (leader, cloud, quarter), metrics in data_by_quarter.items():
            key = (leader, cloud)

            if key not in aggregated:
                aggregated[key] = {
                    'leader': leader,
                    'cloud': cloud,
                    'mdp': 0,
                    'yoy_change': None,
                    'contribution': None,
                    'contribution_diff': None
                }

            # Sum MDP across quarters
            aggregated[key]['mdp'] += metrics.get('mdp', 0) or 0

            # Take last non-null values for percentages (or could average)
            if metrics.get('yoy_change') is not None:
                aggregated[key]['yoy_change'] = metrics['yoy_change']
            if metrics.get('contribution') is not None:
                aggregated[key]['contribution'] = metrics['contribution']
            if metrics.get('contribution_diff') is not None:
                aggregated[key]['contribution_diff'] = metrics['contribution_diff']

        # Convert to list
        data = list(aggregated.values())
        return data

    def parse_horseman(self, cloud_filter: str = None, leaders_filter: list = None, quarters: list = None, fiscal_year: str = 'FY 2027') -> Dict[str, Any]:
        """
        Parse HORSEMAN view with Quarter filter
        Structure: APM L1, Measure Names, Quarter, Fiscal Year, Opportunity Source, OvA Level 2 Username, Measure Values
        """
        file_path = self.data_dir / "6_horseman.csv"

        # Default to Q2 only
        if quarters is None:
            quarters = ['Q2']

        # Use provided leaders_filter or default to EMEA + AMER
        if leaders_filter:
            VALID_LEADERS = leaders_filter
        else:
            VALID_LEADERS = [
                'Alexander Wallner', 'Bob Vanstraelen', 'Emilie Sidiqian',
                'Marco Hernansanz', 'Zahra Bahrololoumi',  # EMEA
                'Mark Sullivan', 'Lenore Lang', 'Connor Marsden', 'Scot Blocker'  # AMER
            ]

        horseman_data = {}

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                cloud = row.get('APM L1', '').strip()
                quarter = row.get('Opportunity Stage 2 Date - Fiscal Quarter', '').strip()
                # FY column removed
                leader = row.get('OvA Level 2 Username', '').strip()
                measure = row['Measure Names']
                source = row['Opportunity Source']
                value_str = row['Measure Values'].replace(',', '')

                # Filter by quarter and fiscal year
                if quarter not in quarters:
                    continue

                # Filter by cloud if specified
                if cloud_filter and cloud != cloud_filter:
                    continue

                # Filter by EMEA+AMER leaders only (skip empty leaders too!)
                if not leader or leader not in VALID_LEADERS:
                    continue

                try:
                    value = float(value_str) if value_str else None
                except:
                    value = None

                if source not in horseman_data:
                    horseman_data[source] = {'mdp': 0, 'previous_mdp': 0, 'yoy_change': None, 'contribution': None, 'mdp_share': None, 'share_diff': None}

                if measure == 'Current FY MDP':
                    horseman_data[source]['mdp'] += (value or 0)
                elif measure == '% YoY':
                    horseman_data[source]['yoy_change'] = value  # Take last/average
                elif measure == 'CFY MDP Contribution':
                    horseman_data[source]['contribution'] = value
                elif measure == '% MDP Share ':
                    horseman_data[source]['mdp_share'] = value
                elif measure == 'MDP Share Diff vs FY-1 (ppts) ':
                    horseman_data[source]['share_diff'] = value

        # Calculate previous_mdp from mdp and yoy_change
        for source, data in horseman_data.items():
            if data['yoy_change'] is not None and data['yoy_change'] != 0:
                # mdp = previous_mdp * (1 + yoy_change)
                # previous_mdp = mdp / (1 + yoy_change)
                data['previous_mdp'] = data['mdp'] / (1 + data['yoy_change'])
            elif data['mdp'] > 0:
                # No YoY data, assume no change
                data['previous_mdp'] = data['mdp']

        return horseman_data

    def parse_traffic_source(self, cloud_filter: str = None, leaders_filter: list = None, quarters: list = None, fiscal_year: str = 'FY 2027') -> Dict[str, Any]:
        """Parse TRAFFIC SOURCE view with L1 + L2 hierarchy and Quarter filter"""
        file_path = self.data_dir / "7_traffic_source.csv"

        # Default to Q2 only
        if quarters is None:
            quarters = ['Q2']

        # Use provided leaders_filter or default to EMEA + AMER
        if leaders_filter:
            VALID_LEADERS = leaders_filter
        else:
            VALID_LEADERS = [
                'Alexander Wallner', 'Bob Vanstraelen', 'Emilie Sidiqian',
                'Marco Hernansanz', 'Zahra Bahrololoumi',  # EMEA
                'Mark Sullivan', 'Lenore Lang', 'Connor Marsden', 'Scot Blocker'  # AMER
            ]

        # Structure: {L1: {l1_totals}, {L2: {l2_data}}}
        traffic_data = {}

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                cloud = row.get('APM L1', '').strip()
                quarter = row.get('Opportunity Stage 2 Date - Fiscal Quarter', '').strip()
                # FY column removed
                leader = row.get('OvA Level 2 Username', '').strip()
                measure = row['Measure Names']
                source_l1 = row['Traffic Source Grouping L1']
                source_l2 = row.get('Traffic Source Grouping L2', '').strip()
                value_str = row['Measure Values'].replace(',', '')

                # Filter by quarter and fiscal year
                if quarter not in quarters:
                    continue

                # Filter by cloud if specified
                if cloud_filter and cloud != cloud_filter:
                    continue

                # Filter by EMEA+AMER leaders only
                if not leader or leader not in VALID_LEADERS:
                    continue

                try:
                    value = float(value_str) if value_str else None
                except:
                    value = None

                # Initialize L1 structure
                if source_l1 not in traffic_data:
                    traffic_data[source_l1] = {
                        'mdp': 0, 'previous_mdp': 0, 'yoy_change': None, 'mdp_share': None, 'share_diff': None,
                        'children': {}
                    }

                # L2 = "All" means L1 total
                if source_l2 == 'All':
                    if measure == 'Current FY MDP':
                        traffic_data[source_l1]['mdp'] += (value or 0)
                    elif measure == '% YoY':
                        traffic_data[source_l1]['yoy_change'] = value
                    elif measure == '% MDP Share ':
                        traffic_data[source_l1]['mdp_share'] = value
                    elif measure == '% MDP Share Diff':
                        traffic_data[source_l1]['share_diff'] = value

                # L2 filled = subcategory
                elif source_l2 and source_l2 != 'All':
                    if source_l2 not in traffic_data[source_l1]['children']:
                        traffic_data[source_l1]['children'][source_l2] = {
                            'mdp': 0, 'previous_mdp': 0, 'yoy_change': None, 'mdp_share': None, 'share_diff': None
                        }

                    if measure == 'Current FY MDP':
                        traffic_data[source_l1]['children'][source_l2]['mdp'] += (value or 0)
                    elif measure == '% YoY':
                        traffic_data[source_l1]['children'][source_l2]['yoy_change'] = value
                    elif measure == '% MDP Share ':
                        traffic_data[source_l1]['children'][source_l2]['mdp_share'] = value
                    elif measure == '% MDP Share Diff':
                        traffic_data[source_l1]['children'][source_l2]['share_diff'] = value

        # Calculate previous_mdp from mdp and yoy_change
        for source_l1, l1_data in traffic_data.items():
            if l1_data['yoy_change'] is not None and l1_data['yoy_change'] != 0:
                l1_data['previous_mdp'] = l1_data['mdp'] / (1 + l1_data['yoy_change'])
            elif l1_data['mdp'] > 0:
                l1_data['previous_mdp'] = l1_data['mdp']

            # L2 children
            for source_l2, l2_data in l1_data.get('children', {}).items():
                if l2_data['yoy_change'] is not None and l2_data['yoy_change'] != 0:
                    l2_data['previous_mdp'] = l2_data['mdp'] / (1 + l2_data['yoy_change'])
                elif l2_data['mdp'] > 0:
                    l2_data['previous_mdp'] = l2_data['mdp']

        return traffic_data

    def parse_offer(self, cloud_filter: str = None, leaders_filter: list = None, quarters: list = None, fiscal_year: str = 'FY 2027') -> Dict[str, Any]:
        """Parse OFFER L1/L2 view with hierarchy and Quarter filter"""
        file_path = self.data_dir / "8_offer_l1_l2.csv"

        # Default to Q2 only
        if quarters is None:
            quarters = ['Q2']

        # Use provided leaders_filter or default to EMEA + AMER
        if leaders_filter:
            VALID_LEADERS = leaders_filter
        else:
            VALID_LEADERS = [
                'Alexander Wallner', 'Bob Vanstraelen', 'Emilie Sidiqian',
                'Marco Hernansanz', 'Zahra Bahrololoumi',  # EMEA
                'Mark Sullivan', 'Lenore Lang', 'Connor Marsden', 'Scot Blocker'  # AMER
            ]

        # Structure: {L1: {l1_totals, children: {L2: l2_data}}}
        offer_data = {}

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                cloud = row.get('APM L1', '').strip()
                quarter = row.get('Opportunity Stage 2 Date - Fiscal Quarter', '').strip()
                leader = row.get('OvA Level 2 Username', '').strip()
                measure = row['Measure Names']
                offer_l1 = row.get('Offer Grouping L1', '').strip()
                offer_l2 = row.get('Offer Grouping L2', '').strip()
                value_str = row['Measure Values'].replace(',', '')

                # Filter by quarter - skip if empty or not in requested quarters
                if quarter and quarter not in quarters:
                    continue

                # Filter by cloud if specified
                if cloud_filter and cloud != cloud_filter:
                    continue

                # Skip totals row and filter by EMEA+AMER leaders only
                if not leader or leader == 'All' or leader not in VALID_LEADERS:
                    continue

                # Skip rows without L1
                if not offer_l1:
                    continue

                try:
                    value = float(value_str) if value_str else None
                except:
                    value = None

                # Initialize L1 structure
                if offer_l1 not in offer_data:
                    offer_data[offer_l1] = {
                        'mdp': 0, 'previous_mdp': 0, 'yoy_change': None, 'mdp_share': None, 'share_diff': None,
                        'children': {}
                    }

                # L2 empty = L1 total
                if not offer_l2:
                    if measure == 'Current FY MDP':
                        offer_data[offer_l1]['mdp'] += (value or 0)
                    elif measure == 'Previous FY MDP Snapped':
                        offer_data[offer_l1]['previous_mdp'] += (value or 0)
                    elif measure == '% YoY':
                        pass  # Will recalculate from mdp and previous_mdp
                    elif measure == '% MDP Share ':
                        offer_data[offer_l1]['mdp_share'] = value
                    elif measure == '% MDP Share Diff':
                        offer_data[offer_l1]['share_diff'] = value

                # L2 filled = subcategory
                else:
                    if offer_l2 not in offer_data[offer_l1]['children']:
                        offer_data[offer_l1]['children'][offer_l2] = {
                            'mdp': 0, 'previous_mdp': 0, 'yoy_change': None, 'mdp_share': None, 'share_diff': None
                        }

                    if measure == 'Current FY MDP':
                        offer_data[offer_l1]['children'][offer_l2]['mdp'] += (value or 0)
                    elif measure == 'Previous FY MDP Snapped':
                        offer_data[offer_l1]['children'][offer_l2]['previous_mdp'] += (value or 0)
                    elif measure == '% YoY':
                        pass  # Will recalculate
                    elif measure == '% MDP Share ':
                        offer_data[offer_l1]['children'][offer_l2]['mdp_share'] = value
                    elif measure == '% MDP Share Diff':
                        offer_data[offer_l1]['children'][offer_l2]['share_diff'] = value

        # Recalculate YoY from actual MDP values
        for offer_l1, l1_data in offer_data.items():
            if l1_data['previous_mdp'] > 0:
                l1_data['yoy_change'] = (l1_data['mdp'] - l1_data['previous_mdp']) / l1_data['previous_mdp']

            for offer_l2, l2_data in l1_data.get('children', {}).items():
                if l2_data['previous_mdp'] > 0:
                    l2_data['yoy_change'] = (l2_data['mdp'] - l2_data['previous_mdp']) / l2_data['previous_mdp']

        return offer_data

    def parse_webinar(self, cloud_filter: str = None, leaders_filter: list = None, quarters: list = None) -> Dict[str, Any]:
        """Parse WEBINAR view with Cloud and Leader filtering

        Structure: APM L1, Measure Names, Quarter, OvA Level 2 Username, Measure Values
        Returns aggregated webinar metrics by Cloud
        """
        file_path = self.data_dir / "9_webinar.csv"

        # Default to Q2 only
        if quarters is None:
            quarters = ['Q2']

        # Use provided leaders_filter or default to EMEA + AMER
        if leaders_filter:
            VALID_LEADERS = leaders_filter
        else:
            VALID_LEADERS = [
                'Alexander Wallner', 'Bob Vanstraelen', 'Emilie Sidiqian',
                'Marco Hernansanz', 'Zahra Bahrololoumi',  # EMEA
                'Mark Sullivan', 'Lenore Lang', 'Connor Marsden', 'Scot Blocker'  # AMER
            ]

        # Structure: {cloud: {mdp, previous_mdp, yoy_change, mdp_share}}
        webinar_data = {}

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                cloud = row.get('APM L1', '').strip()
                quarter = row.get('Opportunity Stage 2 Date - Fiscal Quarter', '').strip()
                leader = row.get('OvA Level 2 Username', '').strip()
                measure = row['Measure Names']
                value_str = row['Measure Values'].replace(',', '')

                # Filter by quarter
                if quarter not in quarters:
                    continue

                # Filter by cloud if specified
                if cloud_filter and cloud != cloud_filter:
                    continue

                # Filter by EMEA+AMER leaders only
                if not leader or leader not in VALID_LEADERS:
                    continue

                # Skip empty cloud (totals)
                if not cloud:
                    continue

                try:
                    value = float(value_str) if value_str else None
                except:
                    value = None

                # Initialize cloud structure
                if cloud not in webinar_data:
                    webinar_data[cloud] = {
                        'mdp': 0, 'previous_mdp': 0, 'yoy_change': None, 'mdp_share': None
                    }

                # Aggregate metrics
                if measure == 'Current FY MDP':
                    webinar_data[cloud]['mdp'] += (value or 0)
                elif measure == 'Previous FY MDP Snapped':
                    webinar_data[cloud]['previous_mdp'] += (value or 0)
                elif measure == '% MDP Share - APM L1':
                    webinar_data[cloud]['mdp_share'] = value  # Take last value
                elif measure == 'MDP YOY':
                    pass  # Will recalculate from totals

        # Recalculate YoY from actual MDP values
        for cloud, metrics in webinar_data.items():
            if metrics['previous_mdp'] > 0:
                metrics['yoy_change'] = (metrics['mdp'] - metrics['previous_mdp']) / metrics['previous_mdp']

        return webinar_data

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics from all data"""
        regional_data = self.parse_regional_cloud_view()
        horseman_data = self.parse_horseman()
        traffic_data = self.parse_traffic_source()

        # Calculate totals
        total_mdp = sum(item.get('mdp', 0) or 0 for item in regional_data)

        # Get cloud breakdowns
        cloud_breakdown = {}
        for item in regional_data:
            cloud = item['cloud']
            if cloud not in cloud_breakdown:
                cloud_breakdown[cloud] = {'mdp': 0, 'count': 0}
            cloud_breakdown[cloud]['mdp'] += item.get('mdp', 0) or 0
            cloud_breakdown[cloud]['count'] += 1

        return {
            'total_mdp': total_mdp,
            'cloud_breakdown': cloud_breakdown,
            'horseman': horseman_data,
            'traffic': traffic_data,
            'regional_count': len(regional_data)
        }


# Singleton instance
csv_parser = CSVParser()
