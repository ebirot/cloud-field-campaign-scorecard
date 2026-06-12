"""
Local Claude Code Integration for Auto-generating Insights
Uses file-based communication with Claude Code session
"""
import os
import json
from typing import Dict, Any, List
from datetime import datetime
import time


class LocalClaudeInsightsService:
    """Generate insights using local Claude Code via file communication"""

    def __init__(self):
        # Directory for request/response files
        self.insights_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "data",
            "insights_queue"
        )
        os.makedirs(self.insights_dir, exist_ok=True)

    def generate_scorecard_insights(
        self,
        cloud: str,
        region: str,
        mdp_data: Dict[str, Any],
        horseman_data: Dict[str, Any] = None,
        traffic_data: Dict[str, Any] = None,
        timeout: int = 300  # 5 minutes max wait
    ) -> Dict[str, List[str]]:
        """
        Generate insights by writing request to file and waiting for Claude Code response

        Args:
            cloud: Cloud name (e.g., "Service", "Sales")
            region: Region (e.g., "EMEA North", "AMER")
            mdp_data: MDP metrics and YoY changes
            horseman_data: Breakdown by AE/BDR/Specialist
            traffic_data: Breakdown by Email/Paid/Organic
            timeout: Max seconds to wait for response

        Returns:
            {
                "highlights": [...],
                "areas_to_watch": [...],
                "next_steps": [...]
            }
        """

        # Create unique request ID
        request_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{cloud}_{region}".replace(" ", "_")

        # Write request file
        request_file = os.path.join(self.insights_dir, f"request_{request_id}.json")
        request_data = {
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "cloud": cloud,
            "region": region,
            "mdp_data": mdp_data,
            "horseman_data": horseman_data or {},
            "traffic_data": traffic_data or {}
        }

        with open(request_file, 'w') as f:
            json.dump(request_data, f, indent=2)

        print(f"✅ Insights request written: {request_file}")
        print(f"⏳ Waiting for Claude Code to generate insights...")

        # Wait for response file
        response_file = os.path.join(self.insights_dir, f"response_{request_id}.json")
        start_time = time.time()

        while time.time() - start_time < timeout:
            if os.path.exists(response_file):
                # Read response
                with open(response_file, 'r') as f:
                    response_data = json.load(f)

                print(f"✅ Insights received from Claude Code")

                # Clean up files
                try:
                    os.remove(request_file)
                    os.remove(response_file)
                except:
                    pass

                return response_data.get("insights", self._generate_fallback_insights())

            time.sleep(2)  # Check every 2 seconds

        # Timeout - return fallback
        print(f"⚠️ Timeout waiting for Claude Code response - using fallback")
        return self._generate_fallback_insights()

    def _generate_fallback_insights(self) -> Dict[str, List[str]]:
        """Fallback insights if Claude Code doesn't respond"""
        return {
            "highlights": [
                "Strong overall performance with positive YoY growth",
                "Key channels showing momentum",
                "Campaign execution on track"
            ],
            "areas_to_watch": [
                "Monitor declining metrics closely",
                "Address underperforming segments",
                "Focus on conversion optimization"
            ],
            "next_steps": [
                "Review channel mix and optimize budget allocation",
                "Launch targeted campaigns for underperforming segments",
                "Schedule monthly performance review with stakeholders"
            ]
        }


# Singleton
local_claude_service = LocalClaudeInsightsService()
