"""
AI Insights API Endpoints
Generate insights using Claude
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.services.claude_insights import claude_service
from app.services.csv_parser import csv_parser

router = APIRouter()


class InsightRequest(BaseModel):
    """Request to generate insights"""
    cloud: str
    region: Optional[str] = "All"
    leader: Optional[str] = None


@router.post("/generate")
async def generate_insights(request: InsightRequest):
    """
    Generate AI-powered insights for a specific cloud/region

    Uses Claude API to analyze data and generate:
    - Highlights (positive trends)
    - Areas to watch (concerns)
    - Next steps (actionable recommendations)
    """
    try:
        # Get relevant data
        regional_data = csv_parser.parse_regional_cloud_view()
        horseman_data = csv_parser.parse_horseman()
        traffic_data = csv_parser.parse_traffic_source()

        # Filter by cloud
        filtered = [
            item for item in regional_data
            if item.get('cloud') == request.cloud
        ]

        if not filtered:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for cloud: {request.cloud}"
            )

        # Aggregate metrics for this cloud
        total_mdp = sum(item.get('mdp', 0) or 0 for item in filtered)
        yoy_changes = [
            item.get('yoy_change')
            for item in filtered
            if item.get('yoy_change') is not None
        ]
        avg_yoy = sum(yoy_changes) / len(yoy_changes) if yoy_changes else 0

        mdp_data = {
            'mdp_total': total_mdp,
            'yoy_change': avg_yoy,
            'leaders_count': len(filtered)
        }

        # Generate insights using Claude
        insights = claude_service.generate_scorecard_insights(
            cloud=request.cloud,
            region=request.region,
            mdp_data=mdp_data,
            horseman_data=horseman_data,
            traffic_data=traffic_data
        )

        return {
            "cloud": request.cloud,
            "region": request.region,
            "insights": insights,
            "data_summary": mdp_data
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/example")
async def get_example_insights():
    """
    Get example AI-generated insights

    Useful for testing without calling Claude API
    """
    return {
        "cloud": "Service",
        "region": "EMEA",
        "insights": {
            "highlights": [
                "Strong overall performance with +37% YoY growth, all regions showing positive momentum",
                "Webinar channel driving significant impact with 62% increase, now representing 8% of MDP share",
                "North region standout performer at +45% YoY, benefiting from English-language campaign coverage"
            ],
            "areas_to_watch": [
                "Central performance declining -32% YoY, primarily driven by reduced paid search and organic traffic",
                "AE contribution down -14% YoY, the only horseman showing negative growth",
                "Email channel growth marginal despite being the largest traffic source, requires optimization"
            ],
            "next_steps": [
                "Launch Q2 Service webinar series with 9 webinars planned to maintain momentum and expand language coverage",
                "Activate Core Offers in email engine and audit offer mix with Email team to improve engagement",
                "Partner with Paid Media team to optimize budget allocation given -62% reduction in Cloud Campaigns budget"
            ]
        },
        "data_summary": {
            "mdp_total": 38000000,
            "yoy_change": 0.37,
            "leaders_count": 5
        }
    }
