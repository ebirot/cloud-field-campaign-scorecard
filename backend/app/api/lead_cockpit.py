"""
Lead Cockpit API endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.services.lead_cockpit_parser import lead_cockpit_parser

router = APIRouter()


@router.get("")
async def get_lead_cockpit(
    quarter: str = Query("Q2", description="Quarter: Q1, Q2, or YTD"),
    cloud: Optional[str] = Query(None, description="Filter by Cloud"),
    ou: Optional[str] = Query(None, description="Filter by OU")
):
    """
    Get Lead Cockpit data filtered by quarter, cloud, and/or OU

    Returns all 22 metrics plus traffic flags and lead scores
    """
    try:
        data = lead_cockpit_parser.get_lead_data(quarter=quarter, cloud=cloud, ou=ou)

        if 'error' in data:
            raise HTTPException(status_code=404, detail=data['error'])

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clouds")
async def get_available_clouds():
    """Get list of available clouds"""
    try:
        data = lead_cockpit_parser.parse_lead_cockpit()

        if not data or 'by_cloud' not in data:
            return {"clouds": []}

        return {
            "clouds": list(data['by_cloud'].keys())
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ous")
async def get_available_ous():
    """Get list of available OUs"""
    try:
        data = lead_cockpit_parser.parse_lead_cockpit()

        if not data or 'by_ou' not in data:
            return {"ous": []}

        return {
            "ous": list(data['by_ou'].keys())
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
