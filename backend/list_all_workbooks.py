"""
List ALL workbooks accessible with your token and save to file
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.tableau import tableau_service
import tableauserverclient as TSC


if __name__ == "__main__":
    print("Fetching ALL workbooks accessible with your token...")
    print("=" * 70)

    # Connect
    tableau_service.connect()

    # Get ALL workbooks (not just first 100)
    all_workbooks = []
    page_number = 1
    page_size = 100

    while True:
        print(f"Fetching page {page_number}...")
        req_option = TSC.RequestOptions(
            pagesize=page_size,
            pagenumber=page_number
        )
        workbooks, pagination = tableau_service.server.workbooks.get(req_option)

        all_workbooks.extend(workbooks)

        if len(workbooks) < page_size:
            # Last page
            break

        page_number += 1

    print(f"\nTotal workbooks found: {len(all_workbooks)}")

    # Save to file
    output_file = Path("data/all_workbooks.txt")
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"Total Workbooks: {len(all_workbooks)}\n")
        f.write("=" * 70 + "\n\n")

        for i, wb in enumerate(all_workbooks, 1):
            f.write(f"{i}. {wb.name}\n")
            f.write(f"   ID: {wb.id}\n")
            f.write(f"   Project: {wb.project_name}\n")
            f.write(f"   Created: {wb.created_at}\n")
            f.write(f"   Updated: {wb.updated_at}\n")
            f.write("-" * 70 + "\n")

    print(f"\nAll workbooks saved to: {output_file}")
    print("\nPlease search this file for:")
    print("  - 'MDP'")
    print("  - 'Scorecard'")
    print("  - 'Field Campaign'")
    print("  - 'Lead'")
    print("  - Or any other relevant keywords")

    # Also search for common patterns
    print("\n\nSearching for relevant workbooks...")
    print("=" * 70)

    keywords = ["MDP", "scorecard", "field", "campaign", "lead", "AMER", "EMEA", "CFM"]

    for keyword in keywords:
        matches = [wb for wb in all_workbooks if keyword.lower() in wb.name.lower()]
        if matches:
            print(f"\n'{keyword}' found in {len(matches)} workbook(s):")
            for wb in matches[:5]:  # Show first 5
                print(f"  - {wb.name}")

    # Disconnect
    tableau_service.disconnect()

    print("\n" + "=" * 70)
    print("COMPLETE")
    print("=" * 70)
