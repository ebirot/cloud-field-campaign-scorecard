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


class InsightsEdit(BaseModel):
    """Request to edit insights (highlights, areas, or next steps)"""
    password: str
    highlights: Optional[List[str]] = None
    areas_to_watch: Optional[List[str]] = None
    next_steps: Optional[List[str]] = None


class InsightsResponse(BaseModel):
    """Insights response"""
    cloud: str
    ou: Optional[str]
    quarter: str
    highlights: List[str]
    areas_to_watch: List[str]
    next_steps: List[str]
    manually_edited: bool
    last_auto_generated: Optional[str]
    last_manually_edited: Optional[str]
    edited_by: Optional[str]


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
        "manually_edited": data.get("manually_edited", False),
        "last_auto_generated": data.get("last_auto_generated"),
        "last_manually_edited": data.get("last_manually_edited"),
        "edited_by": data.get("edited_by")
    }


@router.post("/{cloud}/edit")
async def update_insights(
    cloud: str,
    edit: InsightsEdit,
    ou: Optional[str] = None,
    quarter: str = "Q2"
):
    """
    Edit insights (highlights, areas to watch, or next steps)
    Requires password = 'cloud'

    Once edited, insights are LOCKED and won't be overwritten by auto-refresh
    Use POST /{cloud}/reset to unlock and return to auto-generation
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

    # Update insights (only non-None fields)
    if edit.highlights is not None:
        data["insights"]["highlights"] = edit.highlights
    if edit.areas_to_watch is not None:
        data["insights"]["areas_to_watch"] = edit.areas_to_watch
    if edit.next_steps is not None:
        data["insights"]["next_steps"] = edit.next_steps

    # Mark as manually edited (LOCKS auto-refresh)
    data["manually_edited"] = True
    data["last_manually_edited"] = str(Path(__file__).stat().st_mtime)
    data["edited_by"] = "Campaign Manager"

    # Save
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

    return {
        "message": "Insights updated successfully",
        "locked": True,
        "note": "Auto-refresh will NOT overwrite these insights. Use /reset to unlock."
    }


@router.post("/{cloud}/generate")
async def trigger_generation(
    cloud: str,
    ou: Optional[str] = None,
    quarter: str = "Q2",
    force: bool = False
):
    """
    Trigger insights generation for a cloud/ou/quarter

    If insights are manually edited, they won't be regenerated UNLESS force=true
    """
    from app.services.insights_generator import insights_generator
    from datetime import datetime

    ou_slug = ou or "global"
    filename = f"insights_{cloud}_{ou_slug}_{quarter}.json"
    filepath = INSIGHTS_DIR / filename

    # Check if manually edited
    if filepath.exists() and not force:
        with open(filepath, 'r') as f:
            existing = json.load(f)

        if existing.get("manually_edited", False):
            return {
                "message": "Insights are manually edited and locked",
                "locked": True,
                "note": "Use force=true to regenerate, or use /reset first"
            }

    try:
        insights = insights_generator.generate_insights(
            cloud=cloud,
            ou=ou,
            quarter=quarter
        )

        output_data = {
            "cloud": cloud,
            "ou": ou,
            "quarter": quarter,
            "manually_edited": False,
            "last_auto_generated": datetime.now().isoformat(),
            "last_manually_edited": None,
            "edited_by": None,
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


@router.post("/{cloud}/reset")
async def reset_to_auto(
    cloud: str,
    password: str,
    ou: Optional[str] = None,
    quarter: str = "Q2"
):
    """
    Reset insights to auto-generation mode
    Removes manual lock - next auto-refresh will regenerate insights
    Requires password = 'cloud'
    """
    # Verify password
    if password != EDIT_PASSWORD:
        raise HTTPException(status_code=403, detail="Invalid password")

    ou_slug = ou or "global"
    filename = f"insights_{cloud}_{ou_slug}_{quarter}.json"
    filepath = INSIGHTS_DIR / filename

    if not filepath.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Insights not found for {cloud} {ou_slug} {quarter}"
        )

    # Load and unlock
    with open(filepath, 'r') as f:
        data = json.load(f)

    data["manually_edited"] = False
    data["last_manually_edited"] = None
    data["edited_by"] = None

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

    return {
        "message": "Insights unlocked - auto-refresh will now regenerate them",
        "locked": False
    }


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
