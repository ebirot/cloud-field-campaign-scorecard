"""
Export ALL views from CFM workbook automatically
No manual work needed!
"""
import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent))

from app.services.tableau import tableau_service
import tableauserverclient as TSC


# View definitions
VIEWS = [
    {
        "id": "7f023632-9253-4801-8f01-1ee8f07c2dd2",
        "name": "1_REGIONAL_VIEW_Sales_L2",
        "filename": "1_regional_sales_l2.csv"
    },
    {
        "id": "1a4cca3a-ead5-452c-b215-12e2eb808f56",
        "name": "1_REGIONAL_VIEW_Sales_L2_Cloud",
        "filename": "2_regional_sales_l2_cloud.csv"
    },
    {
        "id": "8307da78-b522-437c-807c-ec99aca37759",
        "name": "1_REGIONAL_VIEW_Sales_L3",
        "filename": "3_regional_sales_l3.csv"
    },
    {
        "id": "62f7283e-f571-491f-bcd9-dacd0f92006c",
        "name": "2_CLOUD_VIEW_APM_L1",
        "filename": "4_cloud_view_l1.csv"
    },
    {
        "id": "d6703c61-0fa7-42f2-9962-df1aa6b7eb3d",
        "name": "2_CLOUD_VIEW_APM_L2",
        "filename": "5_cloud_view_l2.csv"
    },
    {
        "id": "eed26c73-b9f4-4598-b68e-1db515463695",
        "name": "3_HORSEMAN",
        "filename": "6_horseman.csv"
    },
    {
        "id": "1d203316-c6d7-475c-bbd1-e7cce0c29147",
        "name": "4_TRAFFIC_SOURCE",
        "filename": "7_traffic_source.csv"
    },
    {
        "id": "05657272-e2dd-4a60-a3fd-9cf1c1691155",
        "name": "5_OFFER_L1_L2",
        "filename": "8_offer_l1_l2.csv"
    },
    {
        "id": "929ad87f-af7f-46f5-b6bb-9c4b0f838a7d",
        "name": "6_WEBINAR",
        "filename": "9_webinar.csv"
    },
    {
        "id": "419c11ba-199c-42ae-8d52-474b0f10970e",
        "name": "Data_Freshness",
        "filename": "10_data_freshness.csv"
    }
]


def export_view_to_csv(view_id, filename):
    """Export a single view to CSV"""
    try:
        print(f"\nExporting: {filename}")
        print("-" * 60)

        # Get the view
        view = tableau_service.server.views.get_by_id(view_id)
        print(f"View found: {view.name}")

        # Download as CSV
        tableau_service.server.views.populate_csv(view)

        # Save to file
        output_path = Path("data") / filename
        output_path.parent.mkdir(exist_ok=True)

        # Write CSV content (view.csv is a generator)
        with open(output_path, 'wb') as f:
            for chunk in view.csv:
                f.write(chunk)

        print(f"SUCCESS: Saved to {output_path}")
        return True

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False


def main():
    """Export all views"""
    print("=" * 60)
    print("EXPORTING ALL VIEWS FROM CFM WORKBOOK")
    print("=" * 60)
    print(f"\nTotal views to export: {len(VIEWS)}\n")

    # Connect to Tableau
    print("Connecting to Tableau...")
    tableau_service.connect()

    # Export each view
    success_count = 0
    failed_count = 0

    for i, view_info in enumerate(VIEWS, 1):
        print(f"\n[{i}/{len(VIEWS)}] Processing: {view_info['name']}")

        success = export_view_to_csv(view_info['id'], view_info['filename'])

        if success:
            success_count += 1
        else:
            failed_count += 1

        # Small delay between requests
        if i < len(VIEWS):
            time.sleep(1)

    # Disconnect
    tableau_service.disconnect()

    # Summary
    print("\n" + "=" * 60)
    print("EXPORT COMPLETE")
    print("=" * 60)
    print(f"\nSuccessful: {success_count}/{len(VIEWS)}")
    print(f"Failed: {failed_count}/{len(VIEWS)}")

    if success_count > 0:
        print(f"\nCSV files saved in: data/")
        print("\nNext steps:")
        print("1. Check the CSV files in the data/ folder")
        print("2. Ready to build the web app!")


if __name__ == "__main__":
    main()
