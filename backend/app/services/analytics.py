"""
Analytics Service
Track user events and activity
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import threading


class AnalyticsService:
    """Simple analytics service to track user activity"""

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # Point to centralized data/analytics folder at project root
            self.data_dir = Path(__file__).parent.parent.parent.parent / 'data' / 'analytics'
        else:
            self.data_dir = Path(data_dir)

        # Create directory if it doesn't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.events_file = self.data_dir / "analytics_events.json"
        self.lock = threading.Lock()

        # Create file if it doesn't exist
        if not self.events_file.exists():
            self.events_file.write_text("[]")

    def track_event(self, event_type: str, user_id: str = None, metadata: Dict = None) -> None:
        """Track a user event"""
        event = {
            "type": event_type,
            "user_id": user_id or "anonymous",
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        with self.lock:
            try:
                # Read existing events
                events = json.loads(self.events_file.read_text())

                # Add new event
                events.append(event)

                # Keep only last 10000 events
                if len(events) > 10000:
                    events = events[-10000:]

                # Write back
                self.events_file.write_text(json.dumps(events, indent=2))
            except Exception as e:
                print(f"Failed to track event: {e}")

    def get_events(self, limit: int = 100, event_type: str = None) -> List[Dict]:
        """Get recent events"""
        try:
            events = json.loads(self.events_file.read_text())

            # Filter by type if specified
            if event_type:
                events = [e for e in events if e.get("type") == event_type]

            # Return most recent
            return events[-limit:][::-1]
        except Exception as e:
            print(f"Failed to read events: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """Get analytics statistics"""
        try:
            events = json.loads(self.events_file.read_text())

            # Count events by type
            event_counts = {}
            for event in events:
                event_type = event.get("type", "unknown")
                event_counts[event_type] = event_counts.get(event_type, 0) + 1

            # Count unique users
            unique_users = set()
            for event in events:
                user_id = event.get("user_id")
                if user_id and user_id != "anonymous":
                    unique_users.add(user_id)

            # Get recent events (last 24h)
            now = datetime.now()
            recent_events = []
            for event in events:
                try:
                    event_time = datetime.fromisoformat(event.get("timestamp"))
                    if (now - event_time).total_seconds() < 86400:
                        recent_events.append(event)
                except:
                    pass

            return {
                "total_events": len(events),
                "event_counts": event_counts,
                "unique_users": len(unique_users),
                "recent_events_24h": len(recent_events)
            }
        except Exception as e:
            print(f"Failed to calculate stats: {e}")
            return {
                "total_events": 0,
                "event_counts": {},
                "unique_users": 0,
                "recent_events_24h": 0
            }

    def get_active_users(self, minutes: int = 5) -> List[Dict]:
        """Get users active in last N minutes"""
        try:
            events = json.loads(self.events_file.read_text())
            now = datetime.now()

            active_users = {}
            for event in reversed(events):
                try:
                    event_time = datetime.fromisoformat(event.get("timestamp"))
                    if (now - event_time).total_seconds() > minutes * 60:
                        break

                    user_id = event.get("user_id", "anonymous")
                    if user_id not in active_users:
                        active_users[user_id] = {
                            "user_id": user_id,
                            "last_seen": event.get("timestamp"),
                            "last_action": event.get("type"),
                            "metadata": event.get("metadata", {})
                        }
                except:
                    continue

            return list(active_users.values())
        except Exception as e:
            print(f"Failed to get active users: {e}")
            return []


# Singleton instance
analytics = AnalyticsService()
