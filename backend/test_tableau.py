"""
Quick test script for Tableau connection
Run this to verify your Tableau credentials work
"""
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.tableau import tableau_service


def test_connection():
    """Test Tableau connection and list workbooks"""
    print("🔍 Testing Tableau Connection...")
    print("=" * 60)

    result = tableau_service.test_connection()

    if result["status"] == "success":
        print(f"✅ {result['message']}\n")

        if result.get("workbooks"):
            print("📊 Available Workbooks (first 10):")
            print("-" * 60)
            for wb in result["workbooks"]:
                print(f"  ID: {wb['id']}")
                print(f"  Name: {wb['name']}")
                print(f"  Project: {wb['project']}")
                print("-" * 60)
    else:
        print(f"❌ Error: {result['message']}")

    return result


def test_workbook_details():
    """Test getting specific workbook details"""
    print("\n🔍 Testing Workbook Access...")
    print("=" * 60)

    workbook_id = "1534752"  # MDP Scorecard workbook

    if not tableau_service.server:
        tableau_service.connect()

    workbook = tableau_service.get_workbook(workbook_id)

    if workbook:
        print(f"✅ Workbook Found: {workbook.name}")
        print(f"   ID: {workbook.id}")
        print(f"   Project: {workbook.project_name}")

        # Get views
        print("\n📈 Views in this workbook:")
        views = tableau_service.get_workbook_views(workbook_id)
        for i, view in enumerate(views, 1):
            print(f"   {i}. {view.name} (ID: {view.id})")
    else:
        print("❌ Could not access workbook")

    tableau_service.disconnect()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TABLEAU CONNECTION TEST")
    print("=" * 60 + "\n")

    # Test 1: Basic connection
    result = test_connection()

    # Test 2: Specific workbook (if connection successful)
    if result["status"] == "success":
        test_workbook_details()

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60 + "\n")
