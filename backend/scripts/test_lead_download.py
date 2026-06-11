"""
Test downloading Lead Scorecard CSVs
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from app.services.lead_scorecard_refresh import lead_scorecard_service

print("Starting Lead Scorecard CSV download...\n")
results = lead_scorecard_service.refresh_all_csvs()

print("\n" + "="*60)
print("RESULTS:")
print("="*60)
for key, success in results.items():
    status = "OK" if success else "FAILED"
    print(f"  {key}: {status}")
