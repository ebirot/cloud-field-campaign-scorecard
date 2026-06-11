"""
Download data sources from Lead Scorecard workbooks
"""
import tableauserverclient as TSC
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

server_url = os.getenv('TABLEAU_SERVER_URL')
site_id = os.getenv('TABLEAU_SITE_ID')
token_name = os.getenv('TABLEAU_TOKEN_NAME')
token_value = os.getenv('TABLEAU_TOKEN_VALUE')

# Workbook to test
workbook_id = 'a78452dc-76a4-4462-ae68-1bd2b4f661bc'  # Leaderboard by APM L1

print(f"Connecting to {server_url} / {site_id}...")

tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_id)
server = TSC.Server(server_url, use_server_version=True)

try:
    with server.auth.sign_in(tableau_auth):
        print("[OK] Signed in\n")

        # Get workbook
        workbook = server.workbooks.get_by_id(workbook_id)
        print(f"Workbook: {workbook.name}\n")

        # Get all data sources in the workbook
        server.workbooks.populate_connections(workbook)
        print(f"Connections: {len(workbook.connections)}")
        for conn in workbook.connections:
            print(f"  - {conn.datasource_name if hasattr(conn, 'datasource_name') else conn}")
        print()

        # Get views
        server.workbooks.populate_views(workbook)
        print(f"Views: {len(workbook.views)}")
        for view in workbook.views:
            print(f"  - {view.name} (ID: {view.id})")
        print()

        # Try to get data sources
        print("Fetching all data sources on server...")
        all_datasources = []
        for ds in TSC.Pager(server.datasources):
            # Filter for this workbook's project
            if 'Lead Scorecard' in ds.name or '3 dim' in ds.name.lower():
                all_datasources.append(ds)

        print(f"\nFound {len(all_datasources)} relevant data sources:")
        for ds in all_datasources:
            print(f"  - {ds.name} (ID: {ds.id})")
            print(f"    Project: {ds.project_name}")

            # Try to download this data source
            try:
                output_dir = Path(__file__).parent.parent / 'data'
                output_file = output_dir / f"{ds.name.replace('/', '_').replace(' ', '_')}.csv"

                print(f"    Attempting download to {output_file.name}...")

                # Download data source
                file_path = server.datasources.download(ds.id, filepath=str(output_dir), include_extract=False)
                print(f"    [OK] Downloaded to {file_path}")

            except Exception as e:
                print(f"    [ERROR] Could not download: {e}")
            print()

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
