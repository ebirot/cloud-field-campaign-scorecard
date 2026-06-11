"""
Download view data using Crosstab export (similar to manual download)
"""
import tableauserverclient as TSC
import os
from pathlib import Path
from dotenv import load_dotenv
import requests

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

try:
    with server.auth.sign_in(tableau_auth):
        print("[OK] Signed in\n")

        # Get the view
        view = server.views.get_by_id(view_id)
        print(f"View: {view.name}")
        print(f"View URL: {view.content_url}\n")

        # Method 1: Try Excel export (Crosstab)
        print("Attempting Excel (Crosstab) export...")
        try:
            output_dir = Path(__file__).parent.parent / 'data'
            excel_file = output_dir / 'lead_leaderboard_cloud_crosstab.xlsx'

            server.views.populate_excel(view)
            with open(excel_file, 'wb') as f:
                f.write(b''.join(view.excel))

            file_size = excel_file.stat().st_size / 1024
            print(f"[OK] Downloaded Excel: {excel_file.name} ({file_size:.1f} KB)\n")

        except Exception as e:
            print(f"[ERROR] Excel export failed: {e}\n")

        # Method 2: Try CSV with maxrows parameter
        print("Attempting CSV export with maxrows...")
        try:
            output_dir = Path(__file__).parent.parent / 'data'
            csv_file = output_dir / 'lead_leaderboard_cloud_full.csv'

            # Use the REST API directly to get CSV with parameters
            req_option = TSC.RequestOptions()
            req_option.max_items = 10000  # Request more rows

            server.views.populate_csv(view, req_options=req_option)
            csv_data = b''.join(view.csv).decode('utf-8-sig')

            with open(csv_file, 'w', encoding='utf-8') as f:
                f.write(csv_data)

            file_size = len(csv_data) / 1024
            print(f"[OK] Downloaded CSV: {csv_file.name} ({file_size:.1f} KB)")
            print(f"CSV Preview (first 500 chars):")
            print(csv_data[:500])

        except Exception as e:
            print(f"[ERROR] CSV export failed: {e}\n")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
