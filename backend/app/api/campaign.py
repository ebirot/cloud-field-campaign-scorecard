"""
Campaign Scorecard API
Webinar and Email campaign performance data
"""
from fastapi import APIRouter, Query
from typing import Optional
from app.services.webinar_parser import webinar_parser

router = APIRouter()


@router.get("/webinar")
async def get_webinar_data(
    quarters: Optional[str] = Query('Q2', description="Quarters to include (comma-separated)"),
    cloud: Optional[str] = Query(None, description="Filter by single cloud (e.g., Service, Sales, Marketing)"),
    clouds: Optional[str] = Query(None, description="Filter by multiple clouds (comma-separated)"),
    leaders: Optional[str] = Query(None, description="Filter by leaders (comma-separated)")
):
    """
    Get webinar campaign performance data

    Returns MDP by Cloud (APM L1) and Sales Leader with YoY and Share metrics
    """
    # Parse parameters
    quarters_list = [q.strip() for q in quarters.split(',')] if quarters else ['Q2']

    # Handle both 'cloud' (singular) and 'clouds' (plural)
    clouds_list = None
    if cloud:
        clouds_list = [cloud]
    elif clouds:
        clouds_list = [c.strip() for c in clouds.split(',')]

    leaders_list = [l.strip() for l in leaders.split(',')] if leaders else None

    # Parse data
    data = webinar_parser.parse(
        quarters=quarters_list,
        clouds=clouds_list,
        leaders=leaders_list
    )

    return data
