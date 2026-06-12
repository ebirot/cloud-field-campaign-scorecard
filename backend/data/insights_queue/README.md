# Insights Queue - Local Claude Code Integration

This directory enables communication between the FastAPI app and Claude Code for generating insights without needing an Anthropic API key.

## How it works

1. **App creates request**: When `/api/insights/generate` is called, a `request_*.json` file is created here
2. **You notify Claude Code**: Tell Claude Code "generate insights for the pending request"
3. **Claude Code generates**: I read the request, analyze CSV data, and write `response_*.json`
4. **App reads response**: The API endpoint reads the response and returns insights to frontend

## File Format

**Request** (`request_20260612_120530_Service_EMEA.json`):
```json
{
  "request_id": "20260612_120530_Service_EMEA",
  "timestamp": "2026-06-12T12:05:30",
  "cloud": "Service",
  "region": "EMEA",
  "mdp_data": {
    "mdp_total": 38000000,
    "yoy_change": 0.37,
    "contribution": 0.24
  },
  "horseman_data": {...},
  "traffic_data": {...}
}
```

**Response** (`response_20260612_120530_Service_EMEA.json`):
```json
{
  "request_id": "20260612_120530_Service_EMEA",
  "timestamp": "2026-06-12T12:06:15",
  "insights": {
    "highlights": [
      "Strong 37% YoY growth across all regions",
      "Webinar channel up 62%, now 8% of total MDP",
      "North region leading with 45% YoY increase"
    ],
    "areas_to_watch": [
      "Central region declining -32% YoY",
      "Paid search traffic down significantly",
      "Email channel growth stagnant despite large volume"
    ],
    "next_steps": [
      "Launch Q2 webinar series (9 events planned)",
      "Optimize email offer mix with Email team",
      "Reallocate budget from paid to organic channels"
    ]
  }
}
```

## Usage

**Option 1: Watch script (automatic notification)**
```bash
cd backend
python scripts/watch_insights_requests.py
# Leave this running - it will notify you of new requests
```

**Option 2: Manual check**
```bash
# List pending requests
ls backend/data/insights_queue/request_*.json

# Tell Claude Code:
"Generate insights for request_20260612_120530_Service_EMEA"
```

## Advantages
- ✅ No API key needed
- ✅ Free (uses your Claude Code session)
- ✅ Full control over insight quality
- ✅ Can incorporate custom business logic

## Limitations
- ⚠️ Manual process (requires you to tell Claude Code)
- ⚠️ Not real-time (few seconds delay)
- ⚠️ Requires Claude Code session active
