"""
Find workbook GUIDs from numeric web IDs
"""
import tableauserverclient as TSC
import os
from dotenv import load_dotenv

load_dotenv()

server_url = os.getenv('TABLEAU_SERVER_URL')
site_id = os.getenv('TABLEAU_SITE_ID')
token_name = os.getenv('TABLEAU_TOKEN_NAME')
token_value = os.getenv('TABLEAU_TOKEN_VALUE')

# Numeric IDs from URLs
target_ids = ['1772314', '1772315', '1772316', '1772317', '1772319', '1772360']

print(f"Connecting to {server_url} / {site_id}...")

tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_id)
server = TSC.Server(server_url, use_server_version=True)

try:
    with server.auth.sign_in(tableau_auth):
        print("[OK] Signed in\n")
        print(f"Searching for workbooks with numeric IDs: {', '.join(target_ids)}\n")

        found = {}

        # Get all workbooks
        for wb in TSC.Pager(server.workbooks):
            # Check content_url which may contain the numeric ID
            for target_id in target_ids:
                if target_id in str(wb.content_url) or target_id in str(wb.webpage_url if hasattr(wb, 'webpage_url') else ''):
                    if target_id not in found:
                        found[target_id] = []
                    found[target_id].append(wb)
                    break

        if not found:
            print("[WARNING] Could not find workbooks by webpage_url.")
            print("Trying alternative approach: listing recent workbooks...\n")

            # Try to list workbooks and look at their IDs
            all_workbooks = []
            for wb in TSC.Pager(server.workbooks):
                all_workbooks.append(wb)

            # Sort by updated_at descending
            all_workbooks.sort(key=lambda x: x.updated_at if x.updated_at else '', reverse=True)

            print("Recent workbooks (top 50):")
            for i, wb in enumerate(all_workbooks[:50], 1):
                print(f"{i}. {wb.name}")
                print(f"   GUID: {wb.id}")
                print(f"   Content URL: {wb.content_url}")
                if wb.webpage_url:
                    print(f"   Web URL: {wb.webpage_url}")
                print()

        else:
            print("Found workbooks:\n")
            for num_id, workbooks in found.items():
                print(f"[{num_id}]")
                for wb in workbooks:
                    print(f"  Name: {wb.name}")
                    print(f"  GUID: {wb.id}")
                    print(f"  Project: {wb.project_name}")

                    # Get views
                    server.workbooks.populate_views(wb)
                    if wb.views:
                        print(f"  Views ({len(wb.views)}):")
                        for view in wb.views:
                            print(f"    - {view.name} (ID: {view.id})")
                    print()

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
