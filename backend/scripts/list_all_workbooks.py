"""
List ALL workbooks to find the Lead Scorecard ones
"""
import tableauserverclient as TSC
import os
from dotenv import load_dotenv

load_dotenv()

server_url = os.getenv('TABLEAU_SERVER_URL')
site_id = os.getenv('TABLEAU_SITE_ID')
token_name = os.getenv('TABLEAU_TOKEN_NAME')
token_value = os.getenv('TABLEAU_TOKEN_VALUE')

print(f"Connecting to {server_url} / {site_id}...")

tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_id)
server = TSC.Server(server_url, use_server_version=True)

try:
    with server.auth.sign_in(tableau_auth):
        print("[OK] Signed in\n")

        # Get ALL workbooks with pagination
        all_workbooks = []
        for wb in TSC.Pager(server.workbooks):
            all_workbooks.append(wb)

        print(f"Total workbooks: {len(all_workbooks)}\n")

        # Filter for anything with "Campaign" or "Scorecard"
        filtered = [wb for wb in all_workbooks if 'campaign' in wb.name.lower() or 'scorecard' in wb.name.lower() or 'cloud field' in wb.name.lower()]

        print(f"Workbooks matching 'campaign' or 'scorecard' or 'cloud field': {len(filtered)}\n")

        for wb in filtered:
            print(f"* {wb.name}")
            print(f"  ID: {wb.id}")
            print(f"  Project: {wb.project_name}\n")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
