"""
Scorecard API Endpoints
Combines data from Tableau and Slack to generate complete scorecards
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from app.services.tableau import tableau_service
from app.services.slack import slack_service

router = APIRouter()


@router.get("/combined")
async def get_combined_scorecard(
    month: str,
    region: str = "COMBINED"
):
    """
    Get complete scorecard combining Tableau data and Slack updates

    Args:
        month: Format "2026-05"
        region: EMEA, AMER, or COMBINED (default)
    """
    try:
        # Fetch data from Tableau
        mdp_data = tableau_service.extract_mdp_data(region=region, month=month)
        lead_data = tableau_service.extract_lead_data(region=region, month=month)
        campaign_data = tableau_service.extract_campaign_data(region=region, month=month)

        # Fetch updates from Slack
        slack_updates = slack_service.get_monthly_updates(month=month, region=region)

        # Combine everything
        scorecard = {
            "month": month,
            "region": region,
            "generated_at": None,  # TODO: Add timestamp
            "mdp": mdp_data.get("data", {}),
            "leads": lead_data.get("data", {}),
            "campaigns": campaign_data.get("data", {}),
            "slack_updates": slack_updates,
            "status": "success"
        }

        return scorecard

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health-of-cloud")
async def get_health_of_cloud(
    cloud: str,
    month: str,
    region: str = "COMBINED"
):
    """
    Get Health of Cloud scorecard for a specific cloud

    Args:
        cloud: Service, Sales, Marketing, Commerce, AI_Data, Field_Service
        month: Format "2026-05"
        region: EMEA, AMER, or COMBINED
    """
    valid_clouds = ["Service", "Sales", "Marketing", "Commerce", "AI_Data", "Field_Service"]
    if cloud not in valid_clouds:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid cloud. Must be one of: {', '.join(valid_clouds)}"
        )

    # TODO: Filter combined scorecard data for specific cloud
    return {
        "cloud": cloud,
        "month": month,
        "region": region,
        "data": {}
    }


@router.get("/lead-performance")
async def get_lead_performance(
    ou: str,
    month: str,
    region: str = "COMBINED"
):
    """
    Get Lead Performance scorecard for a specific OU

    Args:
        ou: UKI, France, South, Central, North
        month: Format "2026-05"
        region: EMEA, AMER, or COMBINED
    """
    valid_ous = ["UKI", "France", "South", "Central", "North"]
    if ou not in valid_ous:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid OU. Must be one of: {', '.join(valid_ous)}"
        )

    # TODO: Filter combined scorecard data for specific OU
    return {
        "ou": ou,
        "month": month,
        "region": region,
        "data": {}
    }


@router.get("/campaign-performance")
async def get_campaign_performance(
    channel: str,
    month: str,
    region: str = "COMBINED"
):
    """
    Get Campaign Performance for a specific channel

    Args:
        channel: Webinar, Email, Assets
        month: Format "2026-05"
        region: EMEA, AMER, or COMBINED
    """
    valid_channels = ["Webinar", "Email", "Assets"]
    if channel not in valid_channels:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid channel. Must be one of: {', '.join(valid_channels)}"
        )

    # TODO: Filter combined scorecard data for specific channel
    return {
        "channel": channel,
        "month": month,
        "region": region,
        "data": {}
    }
