"""
Slack API Integration Service
Handles parsing of campaign leader updates from Slack broadcast channel
"""
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import Dict, List, Optional
from datetime import datetime
import re
from app.core.config import settings


class SlackService:
    """Service for interacting with Slack API"""

    def __init__(self):
        self.client = WebClient(token=settings.SLACK_BOT_TOKEN)
        self.channel_id = settings.SLACK_CHANNEL_ID

    def get_channel_messages(
        self,
        limit: int = 100,
        oldest: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve messages from the broadcast channel

        Args:
            limit: Number of messages to retrieve
            oldest: Unix timestamp to get messages after this time

        Returns:
            List of message dictionaries
        """
        try:
            response = self.client.conversations_history(
                channel=self.channel_id,
                limit=limit,
                oldest=oldest
            )

            messages = response["messages"]
            print(f"✅ Retrieved {len(messages)} messages from Slack")
            return messages

        except SlackApiError as e:
            print(f"❌ Error fetching Slack messages: {e.response['error']}")
            return []

    def parse_scorecard_update(self, message_text: str) -> Dict:
        """
        Parse a campaign leader's scorecard update message

        Expected format:
        📊 Cloud: Service
        📅 Month: May 2026
        🌍 Region: EMEA North

        🟢 Highlights:
        - Point 1
        - Point 2

        🔴 Areas to watch:
        - Issue 1
        - Issue 2

        📋 Next Steps:
        - Action 1
        - Action 2
        """
        parsed = {
            "cloud": None,
            "month": None,
            "region": None,
            "highlights": [],
            "areas_to_watch": [],
            "next_steps": []
        }

        # Extract metadata
        cloud_match = re.search(r'Cloud:\s*(.+)', message_text, re.IGNORECASE)
        if cloud_match:
            parsed["cloud"] = cloud_match.group(1).strip()

        month_match = re.search(r'Month:\s*(.+)', message_text, re.IGNORECASE)
        if month_match:
            parsed["month"] = month_match.group(1).strip()

        region_match = re.search(r'Region:\s*(.+)', message_text, re.IGNORECASE)
        if region_match:
            parsed["region"] = region_match.group(1).strip()

        # Extract sections
        # Highlights
        highlights_section = re.search(
            r'🟢\s*Highlights?:(.+?)(?=🔴|📋|$)',
            message_text,
            re.DOTALL | re.IGNORECASE
        )
        if highlights_section:
            highlights_text = highlights_section.group(1)
            parsed["highlights"] = self._extract_bullet_points(highlights_text)

        # Areas to watch
        areas_section = re.search(
            r'🔴\s*Areas?\s*to\s*watch:(.+?)(?=📋|$)',
            message_text,
            re.DOTALL | re.IGNORECASE
        )
        if areas_section:
            areas_text = areas_section.group(1)
            parsed["areas_to_watch"] = self._extract_bullet_points(areas_text)

        # Next steps
        next_steps_section = re.search(
            r'📋\s*(?:Next\s*Steps?|Actions?):(.+?)$',
            message_text,
            re.DOTALL | re.IGNORECASE
        )
        if next_steps_section:
            next_steps_text = next_steps_section.group(1)
            parsed["next_steps"] = self._extract_bullet_points(next_steps_text)

        return parsed

    def _extract_bullet_points(self, text: str) -> List[str]:
        """Extract bullet points from text"""
        # Match lines starting with -, *, •, or numbers
        bullet_pattern = r'^\s*[-*•\d.]+\s*(.+)$'
        lines = text.strip().split('\n')

        bullets = []
        for line in lines:
            match = re.match(bullet_pattern, line.strip())
            if match:
                bullets.append(match.group(1).strip())
            elif line.strip() and not re.match(r'^[🟢🔴📋📊📅🌍]', line):
                # Also capture non-bullet lines that aren't emojis
                bullets.append(line.strip())

        return bullets

    def get_monthly_updates(self, month: str, region: Optional[str] = None) -> List[Dict]:
        """
        Get all scorecard updates for a specific month

        Args:
            month: Format "2026-05" or "May 2026"
            region: Optional filter by region (EMEA/AMER)

        Returns:
            List of parsed update dictionaries
        """
        try:
            # Calculate timestamp for beginning of month
            # For now, get last 100 messages
            messages = self.get_channel_messages(limit=100)

            parsed_updates = []
            for msg in messages:
                text = msg.get("text", "")

                # Check if message is a scorecard update (contains required keywords)
                if "Cloud:" in text or "Highlights" in text:
                    parsed = self.parse_scorecard_update(text)

                    # Filter by month and region if specified
                    if month and parsed["month"]:
                        if month.lower() not in parsed["month"].lower():
                            continue

                    if region and parsed["region"]:
                        if region.upper() not in parsed["region"].upper():
                            continue

                    # Add metadata
                    parsed["timestamp"] = msg.get("ts")
                    parsed["user"] = msg.get("user")
                    parsed["raw_text"] = text

                    parsed_updates.append(parsed)

            print(f"✅ Parsed {len(parsed_updates)} scorecard updates for {month}")
            return parsed_updates

        except Exception as e:
            print(f"❌ Error getting monthly updates: {str(e)}")
            return []

    def test_connection(self) -> Dict:
        """Test Slack connection"""
        try:
            response = self.client.auth_test()
            return {
                "status": "success",
                "message": "Connected to Slack successfully",
                "workspace": response["team"],
                "bot_user": response["user"]
            }
        except SlackApiError as e:
            return {
                "status": "error",
                "message": f"Failed to connect: {e.response['error']}"
            }

    def get_channel_info(self) -> Dict:
        """Get information about the configured channel"""
        try:
            response = self.client.conversations_info(channel=self.channel_id)
            channel = response["channel"]

            return {
                "status": "success",
                "channel_name": channel.get("name"),
                "channel_id": channel.get("id"),
                "is_archived": channel.get("is_archived"),
                "num_members": channel.get("num_members")
            }
        except SlackApiError as e:
            return {
                "status": "error",
                "message": f"Failed to get channel info: {e.response['error']}"
            }


# Singleton instance
slack_service = SlackService()
