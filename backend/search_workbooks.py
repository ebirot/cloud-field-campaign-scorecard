"""
Search for specific workbooks by name
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.tableau import tableau_service


def search_workbooks(search_term):
    """Search for workbooks containing search term"""
    print(f"\nSearching for workbooks containing '{search_term}'...")
    print("=" * 70)

    if not tableau_service.server:
        tableau_service.connect()

    # Get all workbooks
    all_workbooks, pagination = tableau_service.server.workbooks.get()

    matches = []
    for wb in all_workbooks:
        if search_term.lower() in wb.name.lower():
            matches.append({
                "id": wb.id,
                "name": wb.name,
                "project": wb.project_name
            })

    if matches:
        print(f"Found {len(matches)} matching workbook(s):\n")
        for wb in matches:
            print(f"Name: {wb['name']}")
            print(f"ID: {wb['id']}")
            print(f"Project: {wb['project']}")
            print("-" * 70)
    else:
        print(f"No workbooks found containing '{search_term}'")

    tableau_service.disconnect()
    return matches


if __name__ == "__main__":
    # Connect once
    tableau_service.connect()

    # Search for key workbooks
    search_terms = [
        "scorecard",
        "MDP",
        "Field Campaign",
        "Lead Performance",
        "Campaign Performance"
    ]

    for term in search_terms:
        print(f"\nSearching for workbooks containing '{term}'...")
        print("=" * 70)

        # Get all workbooks
        all_workbooks, pagination = tableau_service.server.workbooks.get()

        matches = []
        for wb in all_workbooks:
            if term.lower() in wb.name.lower():
                matches.append({
                    "id": wb.id,
                    "name": wb.name,
                    "project": wb.project_name
                })

        if matches:
            print(f"Found {len(matches)} matching workbook(s):\n")
            for wb in matches:
                print(f"Name: {wb['name']}")
                print(f"ID: {wb['id']}")
                print(f"Project: {wb['project']}")
                print("-" * 70)
        else:
            print(f"No workbooks found containing '{term}'")

    # Disconnect once at the end
    tableau_service.disconnect()

    print("\n" + "=" * 70)
    print("SEARCH COMPLETE")
    print("=" * 70)
