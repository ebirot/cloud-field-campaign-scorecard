"""
Utility script to find Lead Scorecard workbook IDs from Tableau Server
"""
import tableauserverclient as TSC
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

server_url = os.getenv('TABLEAU_SERVER_URL')
site_id = os.getenv('TABLEAU_SITE_ID')
token_name = os.getenv('TABLEAU_TOKEN_NAME')
token_value = os.getenv('TABLEAU_TOKEN_VALUE')

print(f"Connecting to {server_url} / {site_id}...")

# Create authentication
tableau_auth = TSC.PersonalAccessTokenAuth(
    token_name,
    token_value,
    site_id=site_id
)

# Create server object
server = TSC.Server(server_url, use_server_version=True)

try:
    with server.auth.sign_in(tableau_auth):
        print("[OK] Signed in successfully\n")

        # Get all workbooks
        print("Searching for Lead Scorecard workbooks...\n")

        # Define search patterns for Lead Scorecard workbooks
        search_patterns = [
            'Cloud Field Campaign',
            'LeadScorecardBuilder',
            'Lead Scorecard Builder',
            'Leaderboard',
            'Core',
            'Traffic',
            'Lead'
        ]

        all_workbooks, _ = server.workbooks.get()

        found_workbooks = []

        for wb in all_workbooks:
            for pattern in search_patterns:
                if pattern.lower() in wb.name.lower():
                    found_workbooks.append(wb)
                    break

        if not found_workbooks:
            print("[ERROR] No Lead Scorecard workbooks found!")
            print("\nShowing first 20 workbooks for reference:")
            for i, wb in enumerate(all_workbooks[:20], 1):
                print(f"{i}. {wb.name}")
                print(f"   ID: {wb.id}")
                print(f"   Project: {wb.project_name}\n")
        else:
            print(f"[OK] Found {len(found_workbooks)} Lead Scorecard workbook(s):\n")

            for wb in found_workbooks:
                print(f"* {wb.name}")
                print(f"   ID: {wb.id}")
                print(f"   Project: {wb.project_name}")

                # Get views for this workbook
                server.workbooks.populate_views(wb)
                if wb.views:
                    print(f"   Views ({len(wb.views)}):")
                    for view in wb.views:
                        print(f"      - {view.name}")
                print()

            print("\nNOTE: Add these to your .env file:")
            print("-" * 60)
            for wb in found_workbooks:
                env_var_name = wb.name.upper().replace(' ', '_').replace('-', '_')
                env_var_name = f"TABLEAU_WORKBOOK_{env_var_name}"
                print(f"{env_var_name}={wb.id}")

except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
