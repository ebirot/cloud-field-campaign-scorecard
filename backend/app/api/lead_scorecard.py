"""
Lead Scorecard API endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.services.lead_scorecard_parser import lead_scorecard_parser

router = APIRouter()


@router.get("/lead-scorecard")
async def get_lead_scorecard(
    quarter: str = Query("Q2", description="Fiscal quarter (Q1, Q2, Q3, Q4, or YTD)"),
    cloud: Optional[str] = Query(None, description="Filter by Cloud (e.g., 'AI and Data', 'Service', 'Sales')"),
    ou: Optional[str] = Query(None, description="Filter by OU (e.g., 'AMER CBS', 'UKI')")
):
    """
    Get Lead Scorecard data filtered by quarter, cloud, and/or OU

    Returns:
    - If cloud specified: data for that cloud broken down by OU
    - If OU specified: data for that OU broken down by cloud
    - Otherwise: all data for the quarter
    """
    try:
        data = lead_scorecard_parser.get_lead_scorecard_data(
            quarter=quarter,
            cloud=cloud,
            ou=ou
        )

        if 'error' in data:
            raise HTTPException(status_code=404, detail=data['error'])

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lead-scorecard/summary")
async def get_lead_scorecard_summary(
    quarter: str = Query("Q2", description="Fiscal quarter")
):
    """
    Get high-level summary metrics for the Lead Scorecard
    (Valid Leads, Core/Non-Core %, Lead Score, etc.)
    """
    try:
        # Parse the 3 dim header file for summary metrics
        header_data = lead_scorecard_parser.parse_3dim_header()

        # For now, return a placeholder structure
        # TODO: Implement proper summary parsing
        return {
            "quarter": quarter,
            "valid_leads": {
                "total": 0,
                "yoy": 0
            },
            "core_leads_pct": 0,
            "non_core_leads_pct": 0,
            "lead_score": {
                "avg": 0,
                "distribution": {}
            },
            "top_lead_sources": [],
            "top_traffic_flags": []
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lead-scorecard/quarters")
async def get_available_quarters():
    """
    Get list of available quarters in the Lead Scorecard data
    """
    try:
        leaderboard = lead_scorecard_parser.parse_leaderboard_3dim()

        if not leaderboard or 'by_quarter' not in leaderboard:
            return {"quarters": []}

        quarters = list(leaderboard['by_quarter'].keys())

        # Add YTD if Q1 and Q2 exist
        if 'Q1' in quarters and 'Q2' in quarters:
            quarters.append('YTD')

        return {
            "quarters": quarters
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lead-scorecard/clouds")
async def get_available_clouds(quarter: str = Query("Q2")):
    """
    Get list of available clouds for a given quarter
    """
    try:
        leaderboard = lead_scorecard_parser.parse_leaderboard_3dim()

        if not leaderboard or 'by_quarter' not in leaderboard:
            return {"clouds": []}

        if quarter not in leaderboard['by_quarter']:
            return {"clouds": []}

        clouds = list(leaderboard['by_quarter'][quarter]['by_cloud'].keys())

        return {
            "quarter": quarter,
            "clouds": clouds
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lead-scorecard/ous")
async def get_available_ous(quarter: str = Query("Q2")):
    """
    Get list of available OUs for a given quarter
    """
    try:
        leaderboard = lead_scorecard_parser.parse_leaderboard_3dim()

        if not leaderboard or 'by_quarter' not in leaderboard:
            return {"ous": []}

        if quarter not in leaderboard['by_quarter']:
            return {"ous": []}

        # Collect all unique OUs across all clouds
        ous = set()
        for cloud_data in leaderboard['by_quarter'][quarter]['by_cloud'].values():
            ous.update(cloud_data['by_ou'].keys())

        return {
            "quarter": quarter,
            "ous": sorted(list(ous))
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
