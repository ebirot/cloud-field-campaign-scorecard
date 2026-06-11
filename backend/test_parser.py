"""Test CSV parser"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.csv_parser import csv_parser
import json


print("Testing CSV Parser...")
print("=" * 60)

# Test regional data
print("\n1. Regional + Cloud Data:")
regional = csv_parser.parse_regional_cloud_view()
print(f"   Total entries: {len(regional)}")
print(f"   Sample: {json.dumps(regional[0], indent=2)}")

# Test horseman
print("\n2. Horseman Data:")
horseman = csv_parser.parse_horseman()
print(f"   Opportunity sources: {list(horseman.keys())}")
print(f"   AE MDP: ${horseman.get('AE', {}).get('mdp', 0):,.0f}")
print(f"   BDR MDP: ${horseman.get('BDR', {}).get('mdp', 0):,.0f}")

# Test traffic
print("\n3. Traffic Source Data:")
traffic = csv_parser.parse_traffic_source()
print(f"   Sources: {list(traffic.keys())}")

# Summary stats
print("\n4. Summary:")
summary = csv_parser.get_summary_stats()
print(f"   Total MDP: ${summary['total_mdp']:,.0f}")
print(f"   Clouds tracked: {len(summary['cloud_breakdown'])}")

print("\n" + "=" * 60)
print("Parser test complete!")
