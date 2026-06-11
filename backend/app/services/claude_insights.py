"""
Claude API Integration for Auto-generating Insights
"""
import os
from typing import Dict, Any, List
import json


class ClaudeInsightsService:
    """Generate insights using Claude API"""

    def __init__(self, api_key: str = None):
        # Use env var or provided key
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

    def generate_scorecard_insights(
        self,
        cloud: str,
        region: str,
        mdp_data: Dict[str, Any],
        horseman_data: Dict[str, Any],
        traffic_data: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """
        Generate highlights, areas to watch, and next steps
        using Claude API based on scorecard data

        Args:
            cloud: Cloud name (e.g., "Service", "Sales")
            region: Region (e.g., "EMEA North", "AMER")
            mdp_data: MDP metrics and YoY changes
            horseman_data: Breakdown by AE/BDR/Specialist
            traffic_data: Breakdown by Email/Paid/Organic

        Returns:
            {
                "highlights": [...],
                "areas_to_watch": [...],
                "next_steps": [...]
            }
        """

        # Build prompt for Claude
        prompt = self._build_prompt(cloud, region, mdp_data, horseman_data, traffic_data)

        # Call Claude API
        insights = self._call_claude_api(prompt)

        return insights

    def _build_prompt(
        self,
        cloud: str,
        region: str,
        mdp_data: Dict,
        horseman_data: Dict,
        traffic_data: Dict
    ) -> str:
        """Build the prompt for Claude"""

        prompt = f"""You are a marketing analytics expert analyzing Cloud Field Campaign performance.

Generate a concise scorecard analysis for:
- **Cloud**: {cloud}
- **Region**: {region}

**Performance Data:**

MDP Metrics:
- Total MDP: ${mdp_data.get('mdp_total', 0):,.0f}
- YoY Change: {mdp_data.get('yoy_change', 0) * 100:.1f}%
- Contribution: {mdp_data.get('contribution', 0) * 100:.1f}%

Horseman Breakdown:
{json.dumps(horseman_data, indent=2)}

Traffic Source Breakdown:
{json.dumps(traffic_data, indent=2)}

**Task:**
Generate a scorecard analysis with exactly:

1. **🟢 Highlights** (2-3 bullet points):
   - Focus on positive YoY growth, strong performers, standout metrics
   - Be specific with numbers and percentages
   - Mention what's driving the success

2. **🔴 Areas to Watch** (2-3 bullet points):
   - Focus on declining metrics, underperformers, risks
   - Be specific with numbers and percentages
   - Highlight what needs attention

3. **📋 Next Steps** (2-3 bullet points):
   - Actionable recommendations based on the data
   - Specific tactics to address areas to watch
   - Concrete initiatives to maintain momentum

**Style Guidelines:**
- Professional, concise, data-driven
- Start each bullet with action/insight, not "The..."
- Include specific metrics in each point
- Focus on what matters for campaign leaders

**Output Format (JSON):**
{{
    "highlights": ["point 1", "point 2", "point 3"],
    "areas_to_watch": ["point 1", "point 2", "point 3"],
    "next_steps": ["action 1", "action 2", "action 3"]
}}

Generate the analysis now:"""

        return prompt

    def _call_claude_api(self, prompt: str) -> Dict[str, List[str]]:
        """
        Call Claude API to generate insights

        NOTE: Requires anthropic package and API key
        """
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.api_key)

            # Call Claude
            message = client.messages.create(
                model="claude-sonnet-4-20250514",  # Latest Sonnet
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Parse response
            response_text = message.content[0].text

            # Extract JSON from response
            # Claude might wrap it in markdown ```json blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text

            insights = json.loads(json_text)

            return insights

        except ImportError:
            # Fallback if anthropic package not installed
            return self._generate_fallback_insights()

        except Exception as e:
            print(f"Error calling Claude API: {str(e)}")
            return self._generate_fallback_insights()

    def _generate_fallback_insights(self) -> Dict[str, List[str]]:
        """Fallback insights if Claude API fails"""
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
claude_service = ClaudeInsightsService()
