"""
Test Script - Manual Tableau CSV Refresh
Run this to test the Tableau refresh system manually
"""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

# Load .env
from dotenv import load_dotenv
load_dotenv(backend_path / '.env')

print("=" * 60)
print("🧪 TEST: Tableau CSV Refresh")
print("=" * 60)

from app.services.tableau_refresh import tableau_service

print("\n📊 Configuration:")
print(f"   Server: {tableau_service.server_url}")
print(f"   Site: {tableau_service.site_id}")
print(f"   Token: {tableau_service.token_name}")
print(f"   Workbook: {tableau_service.workbook_id}")
print(f"   Output: {tableau_service.data_dir}")

print("\n🔄 Starting refresh...")
print("-" * 60)

results = tableau_service.refresh_all_csvs()

print("-" * 60)
print("\n📈 Results:")
successful = sum(1 for v in results.values() if v)
total = len(results)

print(f"   ✅ Success: {successful}/{total} files")

if results:
    print("\n📋 Details:")
    for view_name, success in results.items():
        status = "✅ OK" if success else "❌ FAIL"
        print(f"   {status} {view_name}")
else:
    print("   ⚠️  No files processed")

print("\n" + "=" * 60)
print("✅ Test complete!")
print("=" * 60)
