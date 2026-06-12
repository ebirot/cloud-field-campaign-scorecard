"""
Insights API - Serve auto-generated insights + editable next steps
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from pathlib import Path

router = APIRouter()

# Password for editing next steps
EDIT_PASSWORD = "cloud"

# Path to insights storage
INSIGHTS_DIR = Path(__file__).parent.parent.parent / "data" / "insights"
INSIGHTS_DIR.mkdir(parents=True, exist_ok=True)


class NextStepsEdit(BaseModel):
    """Request to edit next steps"""
    password: str
    next_steps: List[str]


class InsightsResponse(BaseModel):
    """Insights response"""
    cloud: str
    ou: Optional[str]
    quarter: str
    highlights: List[str]
    areas_to_watch: List[str]
    next_steps: List[str]
    next_steps_editable: bool
    generated_at: str


@router.get("/{cloud}", response_model=InsightsResponse)
async def get_insights(cloud: str, ou: Optional[str] = None, quarter: str = "Q2"):
    """
    Get insights for a specific cloud/ou/quarter

    Auto-generated highlights and areas to watch
    Editable next steps (with password)
    """
    # Construct filename
    ou_slug = ou or "global"
    filename = f"insights_{cloud}_{ou_slug}_{quarter}.json"
    filepath = INSIGHTS_DIR / filename

    if not filepath.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Insights not yet generated for {cloud} {ou_slug} {quarter}. "
                   f"Trigger generation from admin panel."
        )

    # Load insights
    with open(filepath, 'r') as f:
        data = json.load(f)

    return {
        "cloud": data["cloud"],
        "ou": data.get("ou"),
        "quarter": data["quarter"],
        "highlights": data["insights"]["highlights"],
        "areas_to_watch": data["insights"]["areas_to_watch"],
        "next_steps": data["insights"]["next_steps"],
        "next_steps_editable": True,
        "generated_at": data.get("generated_at", "unknown")
    }


@router.post("/{cloud}/next-steps")
async def update_next_steps(
    cloud: str,
    edit: NextStepsEdit,
    ou: Optional[str] = None,
    quarter: str = "Q2"
):
    """
    Update next steps for a cloud/ou/quarter
    Requires password = 'cloud'
    """
    # Verify password
    if edit.password != EDIT_PASSWORD:
        raise HTTPException(status_code=403, detail="Invalid password")

    # Construct filename
    ou_slug = ou or "global"
    filename = f"insights_{cloud}_{ou_slug}_{quarter}.json"
    filepath = INSIGHTS_DIR / filename

    if not filepath.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Insights not found for {cloud} {ou_slug} {quarter}"
        )

    # Load current insights
    with open(filepath, 'r') as f:
        data = json.load(f)

    # Update next steps
    data["insights"]["next_steps"] = edit.next_steps
    data["next_steps_edited_at"] = str(Path(__file__).stat().st_mtime)

    # Save
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

    return {"message": "Next steps updated successfully"}


@router.post("/{cloud}/generate")
async def trigger_generation(
    cloud: str,
    ou: Optional[str] = None,
    quarter: str = "Q2"
):
    """
    Trigger insights generation for a cloud/ou/quarter
    This will run the insights generator script
    """
    from app.services.insights_generator import insights_generator

    try:
        insights = insights_generator.generate_insights(
            cloud=cloud,
            ou=ou,
            quarter=quarter
        )

        # Save to file
        ou_slug = ou or "global"
        filename = f"insights_{cloud}_{ou_slug}_{quarter}.json"
        filepath = INSIGHTS_DIR / filename

        output_data = {
            "cloud": cloud,
            "ou": ou,
            "quarter": quarter,
            "generated_at": str(Path(__file__).stat().st_mtime),
            "insights": insights
        }

        with open(filepath, 'w') as f:
            json.dump(output_data, f, indent=2)

        return {
            "message": "Insights generated successfully",
            "insights": insights
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate insights: {str(e)}"
        )


@router.get("/")
async def list_insights():
    """List all available insights"""
    insights_files = list(INSIGHTS_DIR.glob("insights_*.json"))

    insights_list = []
    for filepath in insights_files:
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                insights_list.append({
                    "cloud": data["cloud"],
                    "ou": data.get("ou"),
                    "quarter": data["quarter"],
                    "generated_at": data.get("generated_at")
                })
        except:
            pass

    return {"insights": insights_list}
