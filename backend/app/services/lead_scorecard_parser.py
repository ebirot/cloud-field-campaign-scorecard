"""
Lead Scorecard CSV Parser
Parses the downloaded Lead Scorecard CSV files from Tableau
"""
import csv
import os
from pathlib import Path
from typing import Dict, List
import codecs


class LeadScorecardParser:
    """Parser for Lead Scorecard data"""

    def __init__(self):
        # Point to centralized Lead Scorecard data folder
        self.data_dir = Path(__file__).parent.parent.parent.parent / 'data' / 'Lead Scorecard Import csv'

    def parse_leaderboard_3dim(self) -> Dict:
        """
        Parse the Leaderboard 3 dim CSV file
        Returns data structure:
        {
            'by_quarter': {
                'Q1': {
                    'by_cloud': {
                        'AI and Data': {
                            'by_ou': {
                                'AMER CBS': {
                                    'metric1_pct': 90.6,
                                    'metric1_value': 509,
                                    ...
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        csv_file = self.data_dir / 'Leaderboard 3 dim (1).csv'

        if not csv_file.exists():
            print(f"[ERROR] File not found: {csv_file}")
            return {}

        result = {'by_quarter': {}, 'raw_data': []}

        try:
            # Try UTF-16 LE encoding (common for Tableau exports)
            with codecs.open(csv_file, 'r', encoding='utf-16-le') as f:
                # Read and clean the file content
                content = f.read()
                # Remove BOM if present
                if content.startswith('﻿'):
                    content = content[1:]

                # Split into lines
                lines = content.strip().split('\n')

                if len(lines) < 2:
                    print("[ERROR] CSV file has no data rows")
                    return {}

                # Parse header
                header = [col.strip() for col in lines[0].split('\t')]
                print(f"[INFO] Header columns: {len(header)}")
                print(f"[INFO] Columns: {header[:5]}...")  # First 5 columns

                # Parse data rows
                for i, line in enumerate(lines[1:], start=2):
                    if not line.strip():
                        continue

                    cols = line.split('\t')

                    if len(cols) < 3:
                        continue

                    # Extract dimensions
                    quarter = cols[0].strip() if cols[0] else ''
                    cloud = cols[1].strip() if len(cols) > 1 else ''
                    ou = cols[2].strip() if len(cols) > 2 else ''

                    if not quarter or not cloud or not ou:
                        continue

                    # Initialize nested structure
                    if quarter not in result['by_quarter']:
                        result['by_quarter'][quarter] = {'by_cloud': {}}

                    if cloud not in result['by_quarter'][quarter]['by_cloud']:
                        result['by_quarter'][quarter]['by_cloud'][cloud] = {'by_ou': {}}

                    # Extract metrics (every 3 columns: $ format, % format, raw value)
                    metrics = {}
                    for m in range(1, 9):  # Metric 1-8
                        base_idx = 3 + (m - 1) * 3
                        if base_idx + 2 < len(cols):
                            try:
                                # Skip the format column, use raw value
                                raw_value = cols[base_idx + 2].strip()
                                if raw_value and raw_value != '':
                                    # Remove commas from numbers (e.g., "4,352,776" -> "4352776")
                                    raw_value = raw_value.replace(',', '')
                                    metrics[f'metric{m}'] = float(raw_value)
                            except (ValueError, IndexError):
                                pass

                    result['by_quarter'][quarter]['by_cloud'][cloud]['by_ou'][ou] = metrics

                    # Store raw row for debugging
                    result['raw_data'].append({
                        'quarter': quarter,
                        'cloud': cloud,
                        'ou': ou,
                        'metrics': metrics
                    })

                print(f"[OK] Parsed {len(result['raw_data'])} rows")
                print(f"[OK] Quarters: {list(result['by_quarter'].keys())}")

                return result

        except Exception as e:
            print(f"[ERROR] Failed to parse Leaderboard 3 dim: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def parse_3dim_header(self) -> Dict:
        """
        Parse the 3 dim header CSV file (summary metrics)
        """
        csv_file = self.data_dir / '3 dim header (1).csv'

        if not csv_file.exists():
            print(f"[ERROR] File not found: {csv_file}")
            return {}

        result = {}

        try:
            with codecs.open(csv_file, 'r', encoding='utf-16-le') as f:
                content = f.read()
                if content.startswith('﻿'):
                    content = content[1:]

                lines = content.strip().split('\n')

                if len(lines) < 2:
                    return {}

                # This file has high-level summary metrics
                # Parse similar to leaderboard but simpler structure

                for line in lines[1:]:
                    if not line.strip():
                        continue
                    cols = line.split('\t')
                    # TODO: Parse header metrics based on structure
                    pass

                return result

        except Exception as e:
            print(f"[ERROR] Failed to parse 3 dim header: {e}")
            return {}

    def get_lead_scorecard_data(self, quarter: str = 'Q1', cloud: str = None, ou: str = None) -> Dict:
        """
        Get Lead Scorecard data filtered by quarter, cloud, and/or OU
        """
        leaderboard = self.parse_leaderboard_3dim()

        if not leaderboard or 'by_quarter' not in leaderboard:
            return {'error': 'No data available'}

        # Handle YTD by aggregating Q1 + Q2
        if quarter == 'YTD':
            q1_data = leaderboard['by_quarter'].get('Q1', {}).get('by_cloud', {})
            q2_data = leaderboard['by_quarter'].get('Q2', {}).get('by_cloud', {})

            if not q1_data or not q2_data:
                return {'error': 'YTD requires both Q1 and Q2 data'}

            # Merge Q1 + Q2 data
            ytd_data = {'by_cloud': {}}

            for cloud_name in set(list(q1_data.keys()) + list(q2_data.keys())):
                ytd_data['by_cloud'][cloud_name] = {'by_ou': {}}

                # Get OUs from both quarters
                q1_ous = q1_data.get(cloud_name, {}).get('by_ou', {})
                q2_ous = q2_data.get(cloud_name, {}).get('by_ou', {})

                for ou_name in set(list(q1_ous.keys()) + list(q2_ous.keys())):
                    q1_metrics = q1_ous.get(ou_name, {})
                    q2_metrics = q2_ous.get(ou_name, {})

                    # Sum metric2 (VL #) and metric7 (S2 $)
                    # Keep other metrics from Q2 (most recent)
                    ytd_metrics = {}
                    for m in range(1, 9):
                        key = f'metric{m}'
                        if m in [2, 7]:  # Sum these
                            ytd_metrics[key] = q1_metrics.get(key, 0) + q2_metrics.get(key, 0)
                        else:  # Use Q2 values (YoY, %, ppnts)
                            ytd_metrics[key] = q2_metrics.get(key)

                    ytd_data['by_cloud'][cloud_name]['by_ou'][ou_name] = ytd_metrics

            quarter_data = ytd_data
        else:
            # Filter by quarter
            if quarter not in leaderboard['by_quarter']:
                available = list(leaderboard['by_quarter'].keys())
                return {'error': f'Quarter {quarter} not found. Available: {available}'}

            quarter_data = leaderboard['by_quarter'][quarter]

        # If filtering by cloud
        if cloud:
            if cloud not in quarter_data['by_cloud']:
                return {'error': f'Cloud {cloud} not found in {quarter}'}
            return {
                'quarter': quarter,
                'cloud': cloud,
                'data': quarter_data['by_cloud'][cloud]
            }

        # If filtering by OU (show all clouds for that OU)
        if ou:
            ou_data = {}
            for cloud_name, cloud_info in quarter_data['by_cloud'].items():
                if ou in cloud_info['by_ou']:
                    ou_data[cloud_name] = cloud_info['by_ou'][ou]

            return {
                'quarter': quarter,
                'ou': ou,
                'data': ou_data
            }

        # Return all data for the quarter
        return {
            'quarter': quarter,
            'data': quarter_data
        }


# Global instance
lead_scorecard_parser = LeadScorecardParser()
