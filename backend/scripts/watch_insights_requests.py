"""
Watch for insights requests and notify user to ask Claude Code
This script monitors the insights queue and shows pending requests
"""
import os
import json
import time
from pathlib import Path

# Get insights queue directory
BACKEND_DIR = Path(__file__).parent.parent
INSIGHTS_QUEUE = BACKEND_DIR / "data" / "insights_queue"
INSIGHTS_QUEUE.mkdir(parents=True, exist_ok=True)

print("🔍 Watching for insights requests...")
print(f"📂 Queue directory: {INSIGHTS_QUEUE}")
print("-" * 60)

processed = set()

while True:
    # Find all request files
    request_files = list(INSIGHTS_QUEUE.glob("request_*.json"))

    for req_file in request_files:
        if req_file.name not in processed:
            # New request!
            with open(req_file, 'r') as f:
                request = json.load(f)

            print(f"\n🆕 NEW INSIGHTS REQUEST!")
            print(f"📊 Cloud: {request['cloud']}")
            print(f"🌍 Region: {request['region']}")
            print(f"📈 MDP Data: {json.dumps(request['mdp_data'], indent=2)}")
            print(f"🔗 Request ID: {request['request_id']}")
            print(f"\n💬 Tell Claude Code:")
            print(f"   'Generate insights for the request in {req_file.name}'")
            print("-" * 60)

            processed.add(req_file.name)

    time.sleep(3)
