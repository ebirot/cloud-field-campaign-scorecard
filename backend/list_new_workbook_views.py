"""
Find view IDs in the new workbook: FY27 AMER EMEA CFM MDP Scorecard Builder Data CSV BackEnd
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.tableau import tableau_service

def main():
    # Connect
    print("Connecting to Tableau...")
    tableau_service.connect()
    print(f"Connected to: {tableau_service.server.server_info.baseurl}")

    # Search for the new workbook
    workbook_name = "FY27 AMER EMEA CFM MDP Scorecard Builder Data CSV BackEnd"

    print(f"\nSearching for workbook: {workbook_name}")
    print("=" * 80)

    # Get all workbooks
    all_workbooks, pagination = tableau_service.server.workbooks.get()

    target_workbook = None
    for wb in all_workbooks:
        if workbook_name.lower() in wb.name.lower():
            target_workbook = wb
            break

    if not target_workbook:
        print(f"[X] Workbook not found!")
        print(f"\nSearching for partial match...")
        for wb in all_workbooks:
            if "csv" in wb.name.lower() and "backend" in wb.name.lower():
                print(f"  Found: {wb.name}")
                target_workbook = wb
                break

    if not target_workbook:
        print("[X] No matching workbook found!")
        tableau_service.disconnect()
        return

    print(f"[OK] Found workbook: {target_workbook.name}")
    print(f"   ID: {target_workbook.id}")

    # Get all views
    print(f"\n📊 Views in this workbook:")
    print("=" * 80)

    tableau_service.server.workbooks.populate_views(target_workbook)

    view_mapping = []

    for i, view in enumerate(target_workbook.views, 1):
        print(f"\n{i}. {view.name}")
        print(f"   ID: {view.id}")
        print(f"   Content URL: {view.content_url}")

        view_mapping.append({
            "name": view.name,
            "id": view.id
        })

    # Print Python dict format
    print("\n" + "=" * 80)
    print("COPY THIS TO export_all_views.py:")
    print("=" * 80)
    print("\nVIEWS = [")

    # Map to our expected names
    name_map = {
        "1. REGIONAL VIEW (Sales L2)": ("1_REGIONAL_VIEW_Sales_L2", "1_regional_sales_l2.csv"),
        "1. REGIONAL VIEW (Sales L2 & Cloud)": ("1_REGIONAL_VIEW_Sales_L2_Cloud", "2_regional_sales_l2_cloud.csv"),
        "1. REGIONAL VIEW (Sales L3)": ("1_REGIONAL_VIEW_Sales_L3", "3_regional_sales_l3.csv"),
        "2. CLOUD VIEW APM L1": ("2_CLOUD_VIEW_APM_L1", "4_cloud_view_l1.csv"),
        "2. CLOUD VIEW APM L2": ("2_CLOUD_VIEW_APM_L2", "5_cloud_view_l2.csv"),
        "3. HORSEMAN": ("3_HORSEMAN", "6_horseman.csv"),
        "4. TRAFFIC SOURCE": ("4_TRAFFIC_SOURCE", "7_traffic_source.csv"),
        "5.OFFER L1/L2": ("5_OFFER_L1_L2", "8_offer_l1_l2.csv"),
        "6.WEBINAR": ("6_WEBINAR", "9_webinar.csv"),
        "Data Freshness": ("Data_Freshness", "10_data_freshness.csv"),
    }

    for vm in view_mapping:
        if vm['name'] in name_map:
            var_name, filename = name_map[vm['name']]
            print(f'    {{')
            print(f'        "id": "{vm["id"]}",')
            print(f'        "name": "{var_name}",')
            print(f'        "filename": "{filename}"')
            print(f'    }},')

    print("]")

    tableau_service.disconnect()
    print("\n[OK] Done!")

if __name__ == "__main__":
    main()
