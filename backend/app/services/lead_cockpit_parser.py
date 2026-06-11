"""
Lead Cockpit CSV Parser
Parses 3 separate Lead Cockpit CSV files (Q1, Q2, YTD) from Tableau
Structure: OU | Cloud | Lead Source | Lead Score | 22 metrics
"""
import codecs
from pathlib import Path
from typing import Dict, List, Optional


class LeadCockpitParser:
    """Parser for Lead Cockpit data"""

    def __init__(self):
        # Point to centralized Lead Scorecard data folder
        self.data_dir = Path(__file__).parent.parent.parent.parent / 'data' / 'Lead Scorecard Import csv'
        self.quarters_cache = {}  # Cache parsed quarters

    def clear_cache(self):
        """Clear the quarters cache"""
        self.quarters_cache = {}

    def clean_value(self, value: str) -> Optional[float]:
        """Clean and convert string value to float"""
        if not value or value.strip() == '':
            return None

        # Remove $, %, +, commas, and spaces
        value = value.replace('$', '').replace('%', '').replace('+', '').replace(',', '').strip()

        try:
            return float(value)
        except ValueError:
            return None

    def parse_quarter_file(self, quarter: str) -> Dict:
        """
        Parse a single quarter CSV file
        Files: Export CFC Lead Cockpit FY27Q1.csv, FY27Q2.csv, FY27YTD.csv
        """
        # Map quarter names to file names
        quarter_files = {
            'Q1': 'Export CFC Lead Cockpit FY27Q1.csv',
            'Q2': 'Export CFC Lead Cockpit FY27Q2.csv',
            'YTD': 'Export CFC Lead Cockpit FY27YTD.csv'
        }

        if quarter not in quarter_files:
            print(f"[ERROR] Unknown quarter: {quarter}")
            return {}

        csv_file = self.data_dir / quarter_files[quarter]

        if not csv_file.exists():
            print(f"[ERROR] File not found: {csv_file}")
            return {}

        result = {
            'by_ou': {},
            'by_cloud': {},
            'sources': set(),
            'scores': set(),
            'sources_data': {},  # VL by source with YoY
            'scores_data': {},   # VL by score with YoY
            'raw_data': []
        }

        try:
            with codecs.open(csv_file, 'r', encoding='utf-16-le') as f:
                content = f.read()
                if content.startswith('﻿'):
                    content = content[1:]

                lines = content.strip().split('\n')

                # Skip header and Grand Total
                for line in lines[2:]:
                    if not line.strip():
                        continue

                    cols = line.split('\t')

                    if len(cols) < 26:
                        continue

                    # Extract dimensions
                    ou = cols[0].strip() if cols[0] else ''
                    cloud = cols[1].strip() if len(cols) > 1 else ''
                    source = cols[2].strip() if len(cols) > 2 else ''
                    score = cols[3].strip() if len(cols) > 3 else ''

                    # Skip if essential dimensions are missing
                    if not ou or not cloud:
                        continue

                    # Collect sources and scores for reference
                    if source and source != 'Total':
                        result['sources'].add(source)
                    if score and score != 'Total':
                        result['scores'].add(score)

                    # Skip non-aggregated rows (we only want Total/Total for metrics)
                    if source != 'Total' or score != 'Total':
                        continue

                    # Extract all 22 metrics
                    metrics = {
                        'mql_num': self.clean_value(cols[4]),
                        'mql_yoy': self.clean_value(cols[5]),
                        'vl_num': self.clean_value(cols[6]),
                        'vl_yoy': self.clean_value(cols[7]),
                        'mql_vl_rate': self.clean_value(cols[8]),
                        'mql_vl_pnts': self.clean_value(cols[9]),
                        's1_num': self.clean_value(cols[10]),
                        's1_yoy': self.clean_value(cols[11]),
                        'vl_s1_rate': self.clean_value(cols[12]),
                        'vl_s1_pnts': self.clean_value(cols[13]),
                        's2_num': self.clean_value(cols[14]),
                        's2_yoy': self.clean_value(cols[15]),
                        'vl_s2_rate': self.clean_value(cols[16]),
                        'vl_s2_pnts': self.clean_value(cols[17]),
                        's2_dollar': self.clean_value(cols[18]),
                        's2_dollar_yoy': self.clean_value(cols[19]),
                        'acv_num': self.clean_value(cols[20]),
                        'acv_num_yoy': self.clean_value(cols[21]),
                        'acv_dollar': self.clean_value(cols[22]),
                        'acv_dollar_yoy': self.clean_value(cols[23]),
                        's2_acv_rate': self.clean_value(cols[24]),
                        's2_acv_pnts': self.clean_value(cols[25]) if len(cols) > 25 else None
                    }

                    # Store by OU
                    if ou not in result['by_ou']:
                        result['by_ou'][ou] = {}
                    result['by_ou'][ou][cloud] = metrics

                    # Store by Cloud
                    if cloud not in result['by_cloud']:
                        result['by_cloud'][cloud] = {}
                    result['by_cloud'][cloud][ou] = metrics

                    # Store raw
                    result['raw_data'].append({
                        'ou': ou,
                        'cloud': cloud,
                        'source': source,
                        'score': score,
                        'metrics': metrics
                    })

                result['sources'] = sorted(list(result['sources']))
                result['scores'] = sorted(list(result['scores']))

                print(f"[OK] Parsed {len(result['raw_data'])} rows from {quarter_files[quarter]}")
                print(f"[OK] OUs: {list(result['by_ou'].keys())[:5]}...")
                print(f"[OK] Clouds: {list(result['by_cloud'].keys())[:5]}...")

                return result

        except Exception as e:
            print(f"[ERROR] Failed to parse {quarter_files[quarter]}: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def get_lead_data(self, quarter: str = 'Q2', cloud: str = None, ou: str = None) -> Dict:
        """
        Get Lead Cockpit data filtered by quarter, cloud, and/or OU
        """
        # Parse the requested quarter
        if quarter not in self.quarters_cache:
            self.quarters_cache[quarter] = self.parse_quarter_file(quarter)

        data = self.quarters_cache[quarter]

        if not data:
            return {'error': f'No data available for {quarter}'}

        # Filter by cloud
        if cloud:
            if cloud not in data['by_cloud']:
                return {'error': f'Cloud {cloud} not found in {quarter}'}

            # Add "Total" entry by aggregating all OUs
            cloud_data = data['by_cloud'][cloud].copy()

            # Sum all counts/dollars
            sum_mql = sum(ou.get('mql_num') or 0 for ou in cloud_data.values())
            sum_vl = sum(ou.get('vl_num') or 0 for ou in cloud_data.values())
            sum_s1 = sum(ou.get('s1_num') or 0 for ou in cloud_data.values())
            sum_s2 = sum(ou.get('s2_num') or 0 for ou in cloud_data.values())
            sum_s2_dollar = sum(ou.get('s2_dollar') or 0 for ou in cloud_data.values())
            sum_acv_num = sum(ou.get('acv_num') or 0 for ou in cloud_data.values())
            sum_acv_dollar = sum(ou.get('acv_dollar') or 0 for ou in cloud_data.values())

            # Calculate rates from totals
            mql_vl_rate = (sum_vl / sum_mql * 100) if sum_mql > 0 else 0
            vl_s1_rate = (sum_s1 / sum_vl * 100) if sum_vl > 0 else 0
            vl_s2_rate = (sum_s2 / sum_vl * 100) if sum_vl > 0 else 0
            s2_acv_rate = (sum_acv_num / sum_s2 * 100) if sum_s2 > 0 else 0

            # Average YoY and pnts (weighted would be better but average is simpler)
            count = len(cloud_data)
            avg_mql_yoy = sum(ou.get('mql_yoy') or 0 for ou in cloud_data.values() if ou.get('mql_yoy') is not None) / count if count > 0 else 0
            avg_vl_yoy = sum(ou.get('vl_yoy') or 0 for ou in cloud_data.values() if ou.get('vl_yoy') is not None) / count if count > 0 else 0
            avg_s1_yoy = sum(ou.get('s1_yoy') or 0 for ou in cloud_data.values() if ou.get('s1_yoy') is not None) / count if count > 0 else 0
            avg_s2_yoy = sum(ou.get('s2_yoy') or 0 for ou in cloud_data.values() if ou.get('s2_yoy') is not None) / count if count > 0 else 0
            avg_s2_dollar_yoy = sum(ou.get('s2_dollar_yoy') or 0 for ou in cloud_data.values() if ou.get('s2_dollar_yoy') is not None) / count if count > 0 else 0
            avg_acv_dollar_yoy = sum(ou.get('acv_dollar_yoy') or 0 for ou in cloud_data.values() if ou.get('acv_dollar_yoy') is not None) / count if count > 0 else 0
            avg_mql_vl_pnts = sum(ou.get('mql_vl_pnts') or 0 for ou in cloud_data.values()) / count if count > 0 else 0
            avg_vl_s1_pnts = sum(ou.get('vl_s1_pnts') or 0 for ou in cloud_data.values()) / count if count > 0 else 0
            avg_vl_s2_pnts = sum(ou.get('vl_s2_pnts') or 0 for ou in cloud_data.values()) / count if count > 0 else 0
            avg_s2_acv_pnts = sum(ou.get('s2_acv_pnts') or 0 for ou in cloud_data.values()) / count if count > 0 else 0

            total_metrics = {
                'mql_num': sum_mql,
                'mql_yoy': avg_mql_yoy,
                'vl_num': sum_vl,
                'vl_yoy': avg_vl_yoy,
                'mql_vl_rate': mql_vl_rate,
                'mql_vl_pnts': avg_mql_vl_pnts,
                's1_num': sum_s1,
                's1_yoy': avg_s1_yoy,
                'vl_s1_rate': vl_s1_rate,
                'vl_s1_pnts': avg_vl_s1_pnts,
                's2_num': sum_s2,
                's2_yoy': avg_s2_yoy,
                'vl_s2_rate': vl_s2_rate,
                'vl_s2_pnts': avg_vl_s2_pnts,
                's2_dollar': sum_s2_dollar,
                's2_dollar_yoy': avg_s2_dollar_yoy,
                'acv_num': sum_acv_num,
                'acv_num_yoy': 0,
                'acv_dollar': sum_acv_dollar,
                'acv_dollar_yoy': avg_acv_dollar_yoy,
                's2_acv_rate': s2_acv_rate,
                's2_acv_pnts': avg_s2_acv_pnts
            }

            cloud_data['Total'] = total_metrics

            return {
                'quarter': quarter,
                'cloud': cloud,
                'data': {'by_ou': cloud_data},
                'sources': data['sources'],
                'scores': data['scores'],
                'sources_data': data.get('sources_data', {}),
                'scores_data': data.get('scores_data', {})
            }

        # Filter by OU
        if ou:
            if ou not in data['by_ou']:
                return {'error': f'OU {ou} not found in {quarter}'}
            return {
                'quarter': quarter,
                'ou': ou,
                'data': {'by_cloud': data['by_ou'][ou]},
                'sources': data['sources'],
                'scores': data['scores'],
                'sources_data': data.get('sources_data', {}),
                'scores_data': data.get('scores_data', {})
            }

        # Return all data
        return {
            'quarter': quarter,
            'data': data,
            'sources': data['sources'],
            'scores': data['scores'],
            'sources_data': data.get('sources_data', {}),
            'scores_data': data.get('scores_data', {})
        }


# Global instance
lead_cockpit_parser = LeadCockpitParser()
