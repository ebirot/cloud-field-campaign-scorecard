"""
Webinar CSV Parser
Parses webinar performance data by Cloud (APM L1) and Sales Leader
"""
import csv
from pathlib import Path
from typing import Dict, List, Optional
from decimal import Decimal


class WebinarParser:
    """Parse webinar MDP data by cloud and leader"""

    def __init__(self):
        self.csv_path = Path(__file__).parent.parent.parent.parent / 'data' / 'csv' / '9_webinar.csv'

    def parse(
        self,
        quarters: Optional[List[str]] = None,
        clouds: Optional[List[str]] = None,
        leaders: Optional[List[str]] = None,
        fiscal_year: str = 'FY 2027'
    ) -> Dict:
        """
        Parse webinar data with filters

        Returns data structure:
        {
            'by_leader': {
                'Leader Name': {
                    'clouds': {
                        'Service': {
                            'mdp': 123456.78,
                            'yoy': 0.15,
                            'share': 0.25
                        },
                        ...
                    },
                    'total_mdp': 500000.0
                },
                ...
            },
            'by_cloud': {
                'Service': {
                    'mdp': 1000000.0,
                    'yoy': 0.12,
                    'share': 0.30
                },
                ...
            },
            'grand_total': 3500000.0
        }
        """
        if quarters is None:
            quarters = ['Q2']

        # Read and parse CSV
        data_by_leader_cloud = {}  # {leader: {cloud: {mdp, yoy, share}}}

        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                cloud = row.get('APM L1', '').strip()
                measure = row.get('Measure Names', '').strip()
                quarter = row.get('Opportunity Stage 2 Date - Fiscal Quarter', '').strip()
                leader = row.get('OvA Level 2 Username', '').strip()
                value_str = row.get('Measure Values', '').strip()

                # Skip empty rows
                if not measure or not quarter:
                    continue

                # Skip rows where leader is empty (these are grand totals)
                if not leader or leader.strip() == '':
                    continue

                # Skip "All" cloud rows - they're just totals that would double-count
                if cloud == 'All':
                    continue

                # Skip rows where cloud is empty
                if not cloud or cloud.strip() == '':
                    continue

                # Filter by quarter
                if quarter not in quarters:
                    continue

                # Filter by cloud
                if clouds and cloud not in clouds:
                    continue

                # Filter by leader
                if leaders and leader not in leaders:
                    continue

                # Parse value
                try:
                    value = float(value_str.replace(',', ''))
                except (ValueError, AttributeError):
                    continue

                # Initialize nested dicts
                if leader not in data_by_leader_cloud:
                    data_by_leader_cloud[leader] = {}

                if cloud not in data_by_leader_cloud[leader]:
                    data_by_leader_cloud[leader][cloud] = {
                        'mdp': 0,
                        'previous_mdp': 0,
                        'yoy': 0,
                        'share': 0
                    }

                # Store values by measure type
                if measure == 'Current FY MDP':
                    data_by_leader_cloud[leader][cloud]['mdp'] += value  # Sum across quarters
                elif measure == 'Previous FY MDP Snapped':
                    data_by_leader_cloud[leader][cloud]['previous_mdp'] += value  # Sum across quarters
                elif measure == 'MDP YOY':
                    data_by_leader_cloud[leader][cloud]['yoy'] = value  # Take last value
                elif measure == '% MDP Share - APM L1':
                    data_by_leader_cloud[leader][cloud]['share'] = value  # Take last value

        # Calculate aggregates
        result = {
            'by_leader': {},
            'by_cloud': {},
            'grand_total': 0,
            'grand_total_previous': 0,
            'grand_total_yoy': 0
        }

        # Aggregate by leader
        for leader, clouds_data in data_by_leader_cloud.items():
            leader_total = sum(c['mdp'] for c in clouds_data.values())
            leader_total_previous = sum(c['previous_mdp'] for c in clouds_data.values())

            result['by_leader'][leader] = {
                'clouds': clouds_data,
                'total_mdp': leader_total
            }

            result['grand_total'] += leader_total
            result['grand_total_previous'] += leader_total_previous

        # Aggregate by cloud
        cloud_totals = {}
        for leader, clouds_data in data_by_leader_cloud.items():
            for cloud, metrics in clouds_data.items():
                if cloud not in cloud_totals:
                    cloud_totals[cloud] = {
                        'mdp': 0,
                        'previous_mdp': 0,
                        'share_sum': 0,
                        'share_count': 0
                    }

                cloud_totals[cloud]['mdp'] += metrics['mdp']
                cloud_totals[cloud]['previous_mdp'] += metrics['previous_mdp']

                if metrics['share'] != 0:
                    cloud_totals[cloud]['share_sum'] += metrics['share']
                    cloud_totals[cloud]['share_count'] += 1

        # Calculate YoY from totals and averages for cloud totals
        for cloud, totals in cloud_totals.items():
            # Calculate YoY from actual totals (not average)
            yoy = 0
            if totals['previous_mdp'] > 0:
                yoy = (totals['mdp'] - totals['previous_mdp']) / totals['previous_mdp']

            result['by_cloud'][cloud] = {
                'mdp': totals['mdp'],
                'previous_mdp': totals['previous_mdp'],
                'yoy': yoy,
                'share': totals['share_sum'] / totals['share_count'] if totals['share_count'] > 0 else 0
            }

        # Calculate Grand Total YoY
        if result['grand_total_previous'] > 0:
            result['grand_total_yoy'] = (result['grand_total'] - result['grand_total_previous']) / result['grand_total_previous']

        return result


# Global instance
webinar_parser = WebinarParser()
