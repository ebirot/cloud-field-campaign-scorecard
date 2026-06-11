"""
Analytics API Endpoints
Track and report user activity
"""
from fastapi import APIRouter, Query, Body
from typing import Optional
from app.services.analytics import analytics

router = APIRouter()


@router.post("/track")
async def track_event(
    event_type: str = Body(...),
    user_id: Optional[str] = Body(None),
    metadata: Optional[dict] = Body(None)
):
    """Track a user event"""
    analytics.track_event(event_type, user_id, metadata)
    return {"success": True}


@router.get("/events")
async def get_events(
    limit: int = Query(100, description="Number of events to return"),
    event_type: Optional[str] = Query(None, description="Filter by event type")
):
    """Get recent events"""
    events = analytics.get_events(limit=limit, event_type=event_type)
    return {
        "count": len(events),
        "events": events
    }


@router.get("/stats")
async def get_stats():
    """Get analytics statistics"""
    return analytics.get_stats()


@router.get("/active-users")
async def get_active_users(
    minutes: int = Query(5, description="Time window in minutes")
):
    """Get users active in last N minutes"""
    users = analytics.get_active_users(minutes=minutes)
    return {
        "count": len(users),
        "users": users
    }
