"""
Email Scorecard API
Email campaign performance data
"""
from fastapi import APIRouter, Query
from typing import Optional
from app.services.email_parser import email_parser

router = APIRouter()


@router.get("/scorecard")
async def get_email_scorecard(
    quarters: Optional[str] = Query(None, description="Quarters to include (comma-separated, e.g., Q1,Q2)"),
    fiscal_years: Optional[str] = Query(None, description="Fiscal years to include (comma-separated, e.g., FY2026,FY2027)"),
    regions: Optional[str] = Query(None, description="Filter by regions (comma-separated, e.g., AMER,EMEA)"),
    ous: Optional[str] = Query(None, description="Filter by OUs (comma-separated, e.g., FRANCE,CENTRAL)"),
    clouds: Optional[str] = Query(None, description="Filter by clouds (comma-separated, e.g., Sales,Service)")
):
    """
    Get email scorecard data with metrics:
    - DSE Coverage (%)
    - # Emails Delivered
    - Unique CTR (%)
    - U:CR (Unsubscribe to Click Rate %)

    Data aggregated by OU + Cloud
    """
    # Parse parameters
    quarters_list = [q.strip() for q in quarters.split(',')] if quarters else None
    fiscal_years_list = [fy.strip() for fy in fiscal_years.split(',')] if fiscal_years else None
    regions_list = [r.strip() for r in regions.split(',')] if regions else None
    ous_list = [o.strip() for o in ous.split(',')] if ous else None
    clouds_list = [c.strip() for c in clouds.split(',')] if clouds else None

    # Parse data
    data = email_parser.parse(
        quarters=quarters_list,
        fiscal_years=fiscal_years_list,
        regions=regions_list,
        ous=ous_list,
        clouds=clouds_list
    )

    return data
