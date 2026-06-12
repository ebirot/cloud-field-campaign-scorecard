"""
Tableau API Endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from app.services.tableau import tableau_service

router = APIRouter()


@router.get("/test")
async def test_tableau_connection():
    """Test Tableau connection and list available workbooks"""
    result = tableau_service.test_connection()

    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])

    return result


@router.get("/mdp")
async def get_mdp_data(
    region: str = "EMEA",
    month: Optional[str] = None
):
    """
    Get MDP scorecard data

    Args:
        region: EMEA, AMER, or COMBINED
        month: Format YYYY-MM (e.g., 2026-05)
    """
    if region not in ["EMEA", "AMER", "COMBINED"]:
        raise HTTPException(status_code=400, detail="Invalid region. Must be EMEA, AMER, or COMBINED")

    result = tableau_service.extract_mdp_data(region=region, month=month)

    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message"))

    return result


@router.get("/leads")
async def get_lead_data(
    region: str = "EMEA",
    month: Optional[str] = None
):
    """
    Get Lead Performance data

    Args:
        region: EMEA, AMER, or COMBINED
        month: Format YYYY-MM
    """
    if region not in ["EMEA", "AMER", "COMBINED"]:
        raise HTTPException(status_code=400, detail="Invalid region")

    result = tableau_service.extract_lead_data(region=region, month=month)

    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message"))

    return result


@router.get("/campaigns")
async def get_campaign_data(
    region: str = "EMEA",
    month: Optional[str] = None
):
    """
    Get Campaign Performance data

    Args:
        region: EMEA, AMER, or COMBINED
        month: Format YYYY-MM
    """
    if region not in ["EMEA", "AMER", "COMBINED"]:
        raise HTTPException(status_code=400, detail="Invalid region")

    result = tableau_service.extract_campaign_data(region=region, month=month)

    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message"))

    return result


@router.post("/download-insights-csv")
async def download_insights_backend_csv():
    """
    Download FY27 AMER + EMEA CFM MDP Insights Back End workbook as CSV
    Workbook: https://prod-uswest-c.online.tableau.com/#/site/salesforce/workbooks/1830767

    Returns:
        Status, file path, and available views
    """
    result = tableau_service.download_insights_backend_csv()

    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message"))

    return result


@router.get("/list-workbooks")
async def list_all_workbooks():
    """
    List ALL workbooks accessible with current token
    Useful for debugging permission issues

    Returns:
        List of workbook names and IDs
    """
    try:
        import tableauserverclient as TSC
        import os

        # Auth
        tableau_auth = TSC.PersonalAccessTokenAuth(
            os.getenv('TABLEAU_TOKEN_NAME'),
            os.getenv('TABLEAU_TOKEN_VALUE'),
            site_id=os.getenv('TABLEAU_SITE_ID')
        )

        server = TSC.Server(os.getenv('TABLEAU_SERVER_URL'), use_server_version=True)

        with server.auth.sign_in(tableau_auth):
            all_workbooks, _ = server.workbooks.get()

            workbooks = []
            for wb in all_workbooks:
                workbooks.append({
                    'id': wb.id,
                    'name': wb.name,
                    'project_name': wb.project_name,
                    'created_at': wb.created_at.isoformat() if wb.created_at else None,
                    'updated_at': wb.updated_at.isoformat() if wb.updated_at else None
                })

            return {
                'total': len(workbooks),
                'workbooks': workbooks
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list workbooks: {str(e)}")
