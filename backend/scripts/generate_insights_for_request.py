"""
Helper script to generate insights for a specific request
Usage: python generate_insights_for_request.py <request_file>
"""
import sys
import os
import json
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: python generate_insights_for_request.py <request_id>")
    print("Example: python generate_insights_for_request.py 20260612_120530_Service_EMEA")
    sys.exit(1)

request_id = sys.argv[1]

# Get insights queue directory
BACKEND_DIR = Path(__file__).parent.parent
INSIGHTS_QUEUE = BACKEND_DIR / "data" / "insights_queue"

# Find request file
request_file = INSIGHTS_QUEUE / f"request_{request_id}.json"

if not request_file.exists():
    print(f"❌ Request file not found: {request_file}")
    sys.exit(1)

# Read request
with open(request_file, 'r') as f:
    request = json.load(f)

print("📊 INSIGHTS REQUEST")
print("=" * 60)
print(f"Cloud: {request['cloud']}")
print(f"Region: {request['region']}")
print(f"\n📈 MDP Data:")
print(json.dumps(request['mdp_data'], indent=2))
if request.get('horseman_data'):
    print(f"\n👥 Horseman Data:")
    print(json.dumps(request['horseman_data'], indent=2))
if request.get('traffic_data'):
    print(f"\n🚦 Traffic Data:")
    print(json.dumps(request['traffic_data'], indent=2))
print("=" * 60)
print("\n✍️ Claude Code will now generate insights based on this data...")
print("   (This output will be written to the response file)")
