"""
Explore the MDP Scorecard workbook and list all views
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.tableau import tableau_service


def find_workbook_by_name(name):
    """Find workbook by name"""
    print(f"Searching for workbook: '{name}'...")
    print("=" * 70)

    if not tableau_service.server:
        tableau_service.connect()

    # Get all workbooks
    all_workbooks, pagination = tableau_service.server.workbooks.get()

    for wb in all_workbooks:
        if name.lower() in wb.name.lower():
            print(f"\nFOUND:")
            print(f"  Name: {wb.name}")
            print(f"  ID: {wb.id}")
            print(f"  Project: {wb.project_name}")
            print(f"  Created: {wb.created_at}")
            print(f"  Updated: {wb.updated_at}")
            return wb

    print(f"ERROR: Workbook not found")
    return None


def list_workbook_views(workbook_id):
    """List all views in a workbook"""
    print(f"\nListing views for workbook...")
    print("=" * 70)

    views = tableau_service.get_workbook_views(workbook_id)

    if views:
        print(f"\nFound {len(views)} views:\n")
        for i, view in enumerate(views, 1):
            print(f"{i}. {view.name}")
            print(f"   ID: {view.id}")
            print(f"   Content URL: {view.content_url}")
            print("-" * 70)
    else:
        print("No views found or error occurred")

    return views


def get_view_preview_image(view_id, filename):
    """Download preview image of a view"""
    try:
        print(f"\nDownloading preview image...")
        tableau_service.server.views.populate_preview_image(
            tableau_service.server.views.get_by_id(view_id)
        )
        print(f"Preview image available")
    except Exception as e:
        print(f"Could not download preview: {str(e)}")


if __name__ == "__main__":
    # Connect to Tableau
    tableau_service.connect()

    # Search for the workbook
    workbook_name = "FY27AMEREMEACFMMDPScorecardBuilder"
    workbook = find_workbook_by_name(workbook_name)

    if workbook:
        # List all views
        views = list_workbook_views(workbook.id)

        # Save workbook info to file
        output_file = Path("data/mdp_workbook_info.txt")
        output_file.parent.mkdir(exist_ok=True)

        with open(output_file, "w") as f:
            f.write(f"Workbook: {workbook.name}\n")
            f.write(f"ID: {workbook.id}\n")
            f.write(f"Project: {workbook.project_name}\n\n")
            f.write(f"Views ({len(views) if views else 0}):\n")
            f.write("=" * 70 + "\n\n")

            if views:
                for i, view in enumerate(views, 1):
                    f.write(f"{i}. {view.name}\n")
                    f.write(f"   ID: {view.id}\n")
                    f.write(f"   URL: {view.content_url}\n\n")

        print(f"\nWorkbook info saved to: {output_file}")

    # Disconnect
    tableau_service.disconnect()

    print("\n" + "=" * 70)
    print("EXPLORATION COMPLETE")
    print("=" * 70)
