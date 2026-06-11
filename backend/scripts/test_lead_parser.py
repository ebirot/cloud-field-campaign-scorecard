"""
Test Lead Scorecard parser
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.lead_scorecard_parser import lead_scorecard_parser
import json

print("Testing Lead Scorecard Parser...\n")

# Parse the leaderboard file
result = lead_scorecard_parser.parse_leaderboard_3dim()

if result and 'by_quarter' in result:
    print(f"✓ Successfully parsed data")
    print(f"✓ Quarters found: {list(result['by_quarter'].keys())}")
    print(f"✓ Total rows: {len(result.get('raw_data', []))}")

    # Show sample data for Q1
    if 'Q1' in result['by_quarter']:
        q1_data = result['by_quarter']['Q1']
        clouds = list(q1_data['by_cloud'].keys())
        print(f"\n✓ Q1 Clouds: {clouds[:5]}...")

        if clouds:
            first_cloud = clouds[0]
            ous = list(q1_data['by_cloud'][first_cloud]['by_ou'].keys())
            print(f"✓ {first_cloud} OUs: {ous}")

            if ous:
                first_ou = ous[0]
                metrics = q1_data['by_cloud'][first_cloud]['by_ou'][first_ou]
                print(f"\n✓ Sample data ({first_cloud} / {first_ou}):")
                print(json.dumps(metrics, indent=2))

    # Test filtered queries
    print("\n" + "="*60)
    print("Testing filtered queries:")
    print("="*60)

    # Get data for AI and Data cloud in Q1
    ai_data = lead_scorecard_parser.get_lead_scorecard_data(quarter='Q1', cloud='AI and Data')
    print(f"\n1. AI and Data (Q1): {len(ai_data.get('data', {}).get('by_ou', {}))} OUs")

    # Get data for AMER CBS OU across all clouds in Q1
    cbs_data = lead_scorecard_parser.get_lead_scorecard_data(quarter='Q1', ou='AMER CBS')
    print(f"2. AMER CBS (Q1): {len(cbs_data.get('data', {}))} clouds")

else:
    print("✗ Failed to parse data")
