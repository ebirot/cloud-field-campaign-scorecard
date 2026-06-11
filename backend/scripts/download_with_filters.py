"""
Download Tableau views with filter parameters
"""
import tableauserverclient as TSC
import os
from pathlib import Path
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

server_url = os.getenv('TABLEAU_SERVER_URL')
site_id = os.getenv('TABLEAU_SITE_ID')
token_name = os.getenv('TABLEAU_TOKEN_NAME')
token_value = os.getenv('TABLEAU_TOKEN_VALUE')

# Test with Leaderboard by APM L1
view_id = '460376b2-1d7b-4f06-a9b1-2d91bb488fe9'

print(f"Connecting to {server_url} / {site_id}...")

tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_id)
server = TSC.Server(server_url, use_server_version=True)

# Try different filter combinations
filter_combinations = [
    {},  # No filters
    {'Fiscal Quarter': 'Q2', 'Fiscal Year': 'FY27'},
    {'vf_fiscal_quarter_filter': 'Q2'},
    {'Region': 'EMEA + AMER'},
]

try:
    with server.auth.sign_in(tableau_auth):
        print("[OK] Signed in\n")

        view = server.views.get_by_id(view_id)
        print(f"View: {view.name}\n")

        for i, filters in enumerate(filter_combinations, 1):
            print(f"Attempt {i}: Filters = {filters}")

            try:
                # Create request options with filters
                req_options = TSC.RequestOptions()

                # Add filters as view filters
                for key, value in filters.items():
                    req_options.vf(key, value)

                # Download CSV with filters
                server.views.populate_csv(view, req_options=req_options)
                csv_data = b''.join(view.csv).decode('utf-8-sig')

                if len(csv_data) > 100:
                    print(f"[SUCCESS] Got data! Size: {len(csv_data)} bytes")

                    output_dir = Path(__file__).parent.parent / 'data'
                    csv_file = output_dir / f'lead_leaderboard_cloud_attempt_{i}.csv'

                    with open(csv_file, 'w', encoding='utf-8') as f:
                        f.write(csv_data)

                    print(f"Saved to: {csv_file.name}")
                    print(f"Preview:\n{csv_data[:500]}\n")
                    break
                else:
                    print(f"[EMPTY] Still no data (size: {len(csv_data)})\n")

            except Exception as e:
                print(f"[ERROR] {e}\n")

        # Also try downloading all data sources
        print("\n" + "="*60)
        print("Trying to list view data sources...")
        print("="*60)

        # Use the REST API endpoint directly to get view data
        site_url_name = server.sites.get_by_id(server.site_id).content_url

        # Build the query data URL
        query_url = f"{server_url}/api/{server.version}/sites/{server.site_id}/views/{view_id}/data"
        print(f"Query URL: {query_url}")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
