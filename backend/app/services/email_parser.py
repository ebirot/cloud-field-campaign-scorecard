"""
Email CSV Parser
Parses email performance data by Cloud and OU with mappings
"""
import csv
import json
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict


class EmailParser:
    """Parse email data from multiple sources with country and product mappings"""

    # Default Country/Subregion to OU mapping (fallback if no custom mappings saved)
    DEFAULT_COUNTRY_TO_OU = {
        # From CG_Product_Report
        'Ireland': 'UKI', 'India': 'Others', 'South Korea': 'Others',
        'Germany': 'CENTRAL', 'Asia - Rest of Asia': 'Others', 'Sweden': 'NORTH',
        'Japan': 'Others', 'Spain': 'SOUTH', 'CEE': 'SOUTH', 'Italy': 'SOUTH',
        'Growth and Emerging': 'SOUTH', 'Asia': 'Others', 'UK': 'UKI',
        'Taiwan': 'Others', 'CIS': 'SOUTH', 'Turkey': 'SOUTH',
        'United States': 'AMER', 'Finland': 'NORTH', 'Norway': 'NORTH',
        'Brazil': 'Others', 'Luxembourg': 'NORTH', 'Denmark': 'NORTH',
        'Portugal': 'SOUTH', 'Austria': 'CENTRAL', 'Canada': 'Canada',
        'Mexico': 'Others', 'Israel': 'SOUTH', 'Mediterranean': 'SOUTH',
        'France': 'FRANCE', 'MDE': 'SOUTH', 'ANZ': 'Others', 'Iceland': 'NORTH',
        'Africa': 'SOUTH', 'Switzerland & Liechtenstein': 'CENTRAL',
        'Thailand': 'Others', 'Netherlands': 'NORTH', 'Belgium': 'NORTH',
        # From Email Level
        'United Kingdom': 'UKI',
    }

    # Default Product to Cloud mapping (fallback if no custom mappings saved)
    DEFAULT_PRODUCT_TO_CLOUD = {
        # Agentforce products
        'Agentforce': 'Agentforce', 'Einstein AI': 'Agentforce', 'Einstein Voice': 'Agentforce',
        # Sales
        'Agentforce Sales': 'Sales', 'Sales Performance Management': 'Sales',
        'High Velocity Sales': 'Sales', 'Sales Cloud PRM': 'Sales',
        'Agentforce Revenue Management': 'Sales', 'Sales Cloud Essentials': 'Sales',
        # Service
        'Agentforce Service': 'Service', 'Agentforce Field Service': 'Service',
        'Service Cloud Essentials': 'Service',
        # Marketing
        'Marketing Cloud': 'Marketing', 'Marketing Cloud Intelligence': 'Marketing',
        'Marketing Cloud Account Engagement': 'Marketing', 'Marketing Cloud (Social)': 'Marketing',
        # Commerce
        'Agentforce Commerce': 'Commerce', 'Commerce B2B': 'Commerce',
        # Data
        'Data 360': 'Data',
        # Platform
        'Platform': 'Platform', 'Developer Services': 'Platform', 'Trusted Services': 'Platform',
        # MuleSoft
        'MuleSoft': 'Mulesoft',
        # Tableau
        'Tableau': 'Tableau',
        # Slack
        'Slack': 'Slack',
        # Vertical/Industry products → Others
        'Agentforce Public Sector': 'Others', 'Agentforce Health': 'Others',
        'Agentforce Energy & Utilities': 'Others', 'Agentforce Nonprofit': 'Others',
        'Agentforce Retail': 'Others', 'Agentforce Education': 'Others',
        'Agentforce Financial Services': 'Others', 'Agentforce Media': 'Others',
        'Agentforce Manufacturing': 'Others', 'Agentforce Consumer Goods': 'Others',
        'Agentforce Automotive': 'Others', 'Agentforce Net Zero': 'Others',
        'Agentforce Communications': 'Others',
        # Multi/Other
        'Multi-Product': 'Others', 'Salesforce Customer 360': 'Others',
        'Success Cloud': 'Others', 'Community Cloud': 'Others', 'CRM Analytics': 'Others',
        'Loyalty Management': 'Others', 'Quip': 'Others', 'Spiff': 'Others',
        'myTrailhead': 'Others', 'Salesforce Inbox': 'Others', 'Salesforce CPQ': 'Others',
        'Salesforce Composer': 'Others', 'Salesforce Starter': 'Others',
    }

    def __init__(self):
        # Email Datas is in root data/ folder, not backend/data/
        self.data_dir = Path(__file__).parent.parent.parent.parent / 'data' / 'Email Datas'

        # Mappings directory
        self.mappings_dir = Path(__file__).parent.parent.parent.parent / 'data' / 'mappings'
        self.country_mapping_file = self.mappings_dir / 'country_to_ou.json'
        self.product_mapping_file = self.mappings_dir / 'product_to_cloud.json'

        # Load mappings (custom or default)
        self.COUNTRY_TO_OU = self._load_country_mappings()
        self.PRODUCT_TO_CLOUD = self._load_product_mappings()

        print(f"[EmailParser] Initialized with {len(self.COUNTRY_TO_OU)} country mappings and {len(self.PRODUCT_TO_CLOUD)} product mappings")

    def _load_country_mappings(self) -> Dict[str, str]:
        """Load country mappings from JSON file or use defaults"""
        if self.country_mapping_file.exists():
            try:
                with open(self.country_mapping_file, 'r', encoding='utf-8') as f:
                    custom_mappings = json.load(f)
                    print(f"[EmailParser] Loaded {len(custom_mappings)} custom country mappings from file")
                    return custom_mappings
            except Exception as e:
                print(f"[EmailParser] Error loading country mappings: {e}, using defaults")
                return self.DEFAULT_COUNTRY_TO_OU.copy()
        else:
            print("[EmailParser] No custom country mappings found, using defaults")
            return self.DEFAULT_COUNTRY_TO_OU.copy()

    def _load_product_mappings(self) -> Dict[str, str]:
        """Load product mappings from JSON file or use defaults"""
        if self.product_mapping_file.exists():
            try:
                with open(self.product_mapping_file, 'r', encoding='utf-8') as f:
                    custom_mappings = json.load(f)
                    print(f"[EmailParser] Loaded {len(custom_mappings)} custom product mappings from file")
                    return custom_mappings
            except Exception as e:
                print(f"[EmailParser] Error loading product mappings: {e}, using defaults")
                return self.DEFAULT_PRODUCT_TO_CLOUD.copy()
        else:
            print("[EmailParser] No custom product mappings found, using defaults")
            return self.DEFAULT_PRODUCT_TO_CLOUD.copy()

    def _map_country_to_ou(self, country: str) -> str:
        """Map country/subregion to OU"""
        return self.COUNTRY_TO_OU.get(country.strip(), 'Others')

    def _map_product_to_cloud(self, product: str) -> str:
        """Map product to Cloud"""
        return self.PRODUCT_TO_CLOUD.get(product.strip(), 'Others')

    def _parse_cg_product_report(self) -> Dict:
        """Parse CG_Product_Report for DSE Coverage (AudienceWithContent / Total Audience)"""
        csv_path = self.data_dir / 'CG_Product_Report_20260601.csv'

        # Structure: {OU: {Cloud: {'with': sum, 'total': sum}}}
        audience_data = defaultdict(lambda: defaultdict(lambda: {'with': 0, 'total': 0}))

        try:
            with open(csv_path, 'r', encoding='utf-16-le') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    subregion = row.get('SubregionName', '').strip()
                    product = row.get('ProductInterest', '').strip()

                    if not subregion or not product:
                        continue

                    # Map to OU and Cloud
                    ou = self._map_country_to_ou(subregion)
                    cloud = self._map_product_to_cloud(product)

                    # Get audience counts
                    try:
                        with_content = int(row.get('AudienceWithContent', 0) or 0)
                        no_content = int(row.get('AudienceNoContent', 0) or 0)
                        total = with_content + no_content

                        audience_data[ou][cloud]['with'] += with_content
                        audience_data[ou][cloud]['total'] += total
                    except (ValueError, TypeError):
                        continue

        except FileNotFoundError:
            print(f"Warning: {csv_path} not found")
            return {}

        return audience_data

    def _parse_email_level(self, quarters: Optional[List[str]] = None, fiscal_years: Optional[List[str]] = None) -> Dict:
        """Parse Email Level data for metrics: Total Delivered, Unique Clicks, Unsubscribes"""
        csv_path = self.data_dir / 'Email Level_data Export.csv'

        # Structure: {OU: {Cloud: {'delivered': sum, 'clicks': sum, 'unsubs': sum}}}
        email_data = defaultdict(lambda: defaultdict(lambda: {'delivered': 0, 'clicks': 0, 'unsubs': 0}))

        # Default to FY2027 only if no fiscal_years specified
        if fiscal_years is None:
            fiscal_years = ['FY2027']

        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    subregion = row.get('Subregion', '').strip()
                    product = row.get('Product Advertised', '').strip()
                    measure_name = row.get('Measure Names', '').strip()
                    fiscal_quarter = row.get('Fiscal Quarter', '').strip()
                    fiscal_year = row.get('Fiscal Year', '').strip()

                    if not subregion or not product:
                        continue

                    # Filter by fiscal year (default FY2027)
                    if fiscal_year not in fiscal_years:
                        continue

                    # Filter by quarter if specified
                    if quarters and fiscal_quarter not in quarters:
                        continue

                    # Map to OU and Cloud
                    ou = self._map_country_to_ou(subregion)
                    cloud = self._map_product_to_cloud(product)

                    # Get metric value
                    try:
                        # Total Unique Offer Clicks is the UNIQUE clicks count
                        unique_clicks = float(row.get('Total Unique Offer Clicks', 0) or 0)

                        # Parse measure value for Total Delivered and Total Unsubscribes
                        measure_value_str = row.get('Measure Values', '').strip()
                        if not measure_value_str:
                            continue

                        measure_value = float(measure_value_str.replace(',', ''))

                        # Accumulate based on measure type (strip to handle trailing spaces)
                        measure_name_clean = measure_name.strip()
                        if measure_name_clean == 'Total Delivered':
                            email_data[ou][cloud]['delivered'] += measure_value
                        elif measure_name_clean == 'Email Total Unsubscribes':
                            email_data[ou][cloud]['unsubs'] += measure_value

                        # Add unique clicks for every row (to sum per OU+Cloud)
                        # Note: This might count clicks multiple times if there are multiple measure rows
                        # We'll handle this more carefully
                        if measure_name_clean == 'Total Delivered':  # Use one measure as anchor
                            email_data[ou][cloud]['clicks'] += unique_clicks

                    except (ValueError, TypeError):
                        continue

        except FileNotFoundError:
            print(f"Warning: {csv_path} not found")
            return {}

        return email_data

    def parse(
        self,
        quarters: Optional[List[str]] = None,
        fiscal_years: Optional[List[str]] = None,
        regions: Optional[List[str]] = None,
        ous: Optional[List[str]] = None,
        clouds: Optional[List[str]] = None
    ) -> Dict:
        """
        Parse email data with filters

        Returns data structure:
        {
            'by_ou': {
                'FRANCE': {
                    'clouds': {
                        'Sales': {
                            'dse_coverage': 93.07,
                            'emails_delivered': 1819,
                            'unique_ctr': 1.3,
                            'ucr': 13.0
                        },
                        ...
                    },
                    'total': {...}
                },
                ...
            },
            'by_cloud': {
                'Sales': {
                    'dse_coverage': 85.5,
                    'emails_delivered': 28265,
                    'unique_ctr': 1.5,
                    'ucr': 15.2
                },
                ...
            },
            'grand_total': {...}
        }
        """

        # Parse data sources
        audience_data = self._parse_cg_product_report()
        email_data = self._parse_email_level(quarters=quarters, fiscal_years=fiscal_years)

        # Combine data by OU + Cloud
        result = {
            'by_ou': {},
            'by_cloud': {},
            'grand_total': {
                'dse_coverage': 0,
                'emails_delivered': 0,
                'unique_ctr': 0,
                'ucr': 0
            }
        }

        # Build by_ou structure
        all_ous = set(list(audience_data.keys()) + list(email_data.keys()))

        for ou in all_ous:
            # Filter by OU if specified
            if ous and ou not in ous:
                continue

            # Filter by region if specified (AMER vs EMEA logic)
            if regions:
                if 'AMER' in regions and ou not in ['AMER', 'Canada']:
                    continue
                if 'EMEA' in regions and ou in ['AMER', 'Canada', 'Others']:
                    continue

            result['by_ou'][ou] = {'clouds': {}, 'total': {}}

            # Get all clouds for this OU
            all_clouds = set(
                list(audience_data.get(ou, {}).keys()) +
                list(email_data.get(ou, {}).keys())
            )

            ou_totals = {
                'dse_with': 0, 'dse_total': 0,
                'delivered': 0, 'clicks': 0, 'unsubs': 0
            }

            for cloud in all_clouds:
                # Filter by cloud if specified
                if clouds and cloud not in clouds:
                    continue

                # Get data for this OU+Cloud
                aud = audience_data.get(ou, {}).get(cloud, {'with': 0, 'total': 0})
                email = email_data.get(ou, {}).get(cloud, {'delivered': 0, 'clicks': 0, 'unsubs': 0})

                # Calculate metrics
                dse_coverage = (aud['with'] / aud['total'] * 100) if aud['total'] > 0 else 0
                emails_delivered = email['delivered']
                unique_ctr = (email['clicks'] / email['delivered'] * 100) if email['delivered'] > 0 else 0
                ucr = (email['unsubs'] / email['clicks'] * 100) if email['clicks'] > 0 else 0

                result['by_ou'][ou]['clouds'][cloud] = {
                    'dse_coverage': round(dse_coverage, 2),
                    'emails_delivered': int(emails_delivered),
                    'unique_ctr': round(unique_ctr, 2),
                    'ucr': round(ucr, 2)
                }

                # Accumulate for OU totals
                ou_totals['dse_with'] += aud['with']
                ou_totals['dse_total'] += aud['total']
                ou_totals['delivered'] += email['delivered']
                ou_totals['clicks'] += email['clicks']
                ou_totals['unsubs'] += email['unsubs']

            # Calculate OU totals
            result['by_ou'][ou]['total'] = {
                'dse_coverage': round((ou_totals['dse_with'] / ou_totals['dse_total'] * 100) if ou_totals['dse_total'] > 0 else 0, 2),
                'emails_delivered': int(ou_totals['delivered']),
                'unique_ctr': round((ou_totals['clicks'] / ou_totals['delivered'] * 100) if ou_totals['delivered'] > 0 else 0, 2),
                'ucr': round((ou_totals['unsubs'] / ou_totals['clicks'] * 100) if ou_totals['clicks'] > 0 else 0, 2)
            }

        # Build by_cloud aggregates
        cloud_totals = defaultdict(lambda: {
            'dse_with': 0, 'dse_total': 0,
            'delivered': 0, 'clicks': 0, 'unsubs': 0
        })

        for ou, ou_data in result['by_ou'].items():
            for cloud, metrics in ou_data['clouds'].items():
                # Get raw data for aggregation
                aud = audience_data.get(ou, {}).get(cloud, {'with': 0, 'total': 0})
                email = email_data.get(ou, {}).get(cloud, {'delivered': 0, 'clicks': 0, 'unsubs': 0})

                cloud_totals[cloud]['dse_with'] += aud['with']
                cloud_totals[cloud]['dse_total'] += aud['total']
                cloud_totals[cloud]['delivered'] += email['delivered']
                cloud_totals[cloud]['clicks'] += email['clicks']
                cloud_totals[cloud]['unsubs'] += email['unsubs']

        for cloud, totals in cloud_totals.items():
            result['by_cloud'][cloud] = {
                'dse_coverage': round((totals['dse_with'] / totals['dse_total'] * 100) if totals['dse_total'] > 0 else 0, 2),
                'emails_delivered': int(totals['delivered']),
                'unique_ctr': round((totals['clicks'] / totals['delivered'] * 100) if totals['delivered'] > 0 else 0, 2),
                'ucr': round((totals['unsubs'] / totals['clicks'] * 100) if totals['clicks'] > 0 else 0, 2)
            }

        # Calculate grand total
        grand = {
            'dse_with': sum(t['dse_with'] for t in cloud_totals.values()),
            'dse_total': sum(t['dse_total'] for t in cloud_totals.values()),
            'delivered': sum(t['delivered'] for t in cloud_totals.values()),
            'clicks': sum(t['clicks'] for t in cloud_totals.values()),
            'unsubs': sum(t['unsubs'] for t in cloud_totals.values())
        }

        result['grand_total'] = {
            'dse_coverage': round((grand['dse_with'] / grand['dse_total'] * 100) if grand['dse_total'] > 0 else 0, 2),
            'emails_delivered': int(grand['delivered']),
            'unique_ctr': round((grand['clicks'] / grand['delivered'] * 100) if grand['delivered'] > 0 else 0, 2),
            'ucr': round((grand['unsubs'] / grand['clicks'] * 100) if grand['clicks'] > 0 else 0, 2)
        }

        return result


# Global instance
email_parser = EmailParser()
# Force reload
