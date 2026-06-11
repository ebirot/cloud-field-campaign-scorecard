"""
Slack API Endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from app.services.slack import slack_service

router = APIRouter()


@router.get("/test")
async def test_slack_connection():
    """Test Slack connection"""
    result = slack_service.test_connection()

    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])

    return result


@router.get("/channel-info")
async def get_channel_info():
    """Get information about the configured Slack channel"""
    result = slack_service.get_channel_info()

    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])

    return result


@router.get("/updates")
async def get_monthly_updates(
    month: str,
    region: Optional[str] = None
):
    """
    Get scorecard updates from Slack for a specific month

    Args:
        month: Format "2026-05" or "May 2026"
        region: Optional filter by EMEA or AMER
    """
    updates = slack_service.get_monthly_updates(month=month, region=region)

    return {
        "month": month,
        "region": region,
        "count": len(updates),
        "updates": updates
    }


@router.get("/messages")
async def get_channel_messages(limit: int = 50):
    """
    Get recent messages from the Slack channel

    Args:
        limit: Number of messages to retrieve (max 100)
    """
    if limit > 100:
        raise HTTPException(status_code=400, detail="Limit cannot exceed 100")

    messages = slack_service.get_channel_messages(limit=limit)

    return {
        "count": len(messages),
        "messages": messages
    }
