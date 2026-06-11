"""
Explore the FY27 AMER + EMEA CFM MDP Scorecard Builder workbook
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.tableau import tableau_service


def explore_workbook(workbook_id):
    """Explore workbook and list all views"""
    print(f"Exploring workbook: {workbook_id}")
    print("=" * 70)

    # Get workbook details
    workbook = tableau_service.get_workbook(workbook_id)

    if workbook:
        print(f"\nWorkbook Details:")
        print(f"  Name: {workbook.name}")
        print(f"  Project: {workbook.project_name}")
        print(f"  Created: {workbook.created_at}")
        print(f"  Updated: {workbook.updated_at}")

        # Get all views
        print(f"\nFetching views...")
        views = tableau_service.get_workbook_views(workbook_id)

        if views:
            print(f"\nFound {len(views)} views:\n")

            # Save to file
            output_file = Path("data/cfm_workbook_views.txt")
            output_file.parent.mkdir(exist_ok=True)

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"Workbook: {workbook.name}\n")
                f.write(f"ID: {workbook.id}\n")
                f.write(f"Project: {workbook.project_name}\n")
                f.write(f"Updated: {workbook.updated_at}\n\n")
                f.write(f"Total Views: {len(views)}\n")
                f.write("=" * 70 + "\n\n")

                for i, view in enumerate(views, 1):
                    print(f"{i}. {view.name}")
                    print(f"   ID: {view.id}")
                    print(f"   URL: {view.content_url}")
                    print("-" * 70)

                    f.write(f"{i}. {view.name}\n")
                    f.write(f"   ID: {view.id}\n")
                    f.write(f"   Content URL: {view.content_url}\n")
                    f.write(f"   Workbook ID: {view.workbook_id}\n\n")

            print(f"\nViews saved to: {output_file}")
        else:
            print("No views found")

        return workbook, views
    else:
        print("ERROR: Could not access workbook")
        return None, None


if __name__ == "__main__":
    # Connect
    tableau_service.connect()

    # Workbook ID for FY27 AMER + EMEA CFM MDP Scorecard Builder
    workbook_id = "d55ddabc-02ed-4da9-b4f4-49e7959f29b6"

    # Explore
    workbook, views = explore_workbook(workbook_id)

    # Disconnect
    tableau_service.disconnect()

    print("\n" + "=" * 70)
    print("EXPLORATION COMPLETE")
    print("=" * 70)

    if views:
        print(f"\nNext steps:")
        print(f"1. Review the views in: data/cfm_workbook_views.txt")
        print(f"2. Identify which views contain the data you need")
        print(f"3. We can then extract data from specific views")
