"""
List all views in the MDP Scorecard workbook
"""
import tableauserverclient as TSC
import os
from dotenv import load_dotenv

load_dotenv()

server_url = os.getenv('TABLEAU_SERVER_URL')
site_id = os.getenv('TABLEAU_SITE_ID')
token_name = os.getenv('TABLEAU_TOKEN_NAME')
token_value = os.getenv('TABLEAU_TOKEN_VALUE')
workbook_id = os.getenv('TABLEAU_WORKBOOK_MDP_SCORECARD')

print(f"Connecting to {server_url} / {site_id}...")
print(f"Workbook ID: {workbook_id}\n")

tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_id)
server = TSC.Server(server_url, use_server_version=True)

try:
    with server.auth.sign_in(tableau_auth):
        print("[OK] Signed in\n")

        workbook = server.workbooks.get_by_id(workbook_id)
        print(f"Workbook: {workbook.name}\n")

        server.workbooks.populate_views(workbook)

        print(f"Total views: {len(workbook.views)}\n")

        for i, view in enumerate(workbook.views, 1):
            print(f"{i}. {view.name}")
            print(f"   ID: {view.id}\n")

except Exception as e:
    print(f"[ERROR] {e}")
