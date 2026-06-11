"""
Analytics API Endpoints
Track and report user activity
"""
from fastapi import APIRouter, Query, Body
from pydantic import BaseModel
from typing import Optional
from app.services.analytics import analytics

router = APIRouter()


class TrackEventRequest(BaseModel):
    event_type: str
    page: Optional[str] = None
    data: Optional[dict] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    session_id: Optional[str] = None


class UserIdentifyRequest(BaseModel):
    user_id: str
    user_name: Optional[str] = None
    email: Optional[str] = None
    metadata: Optional[dict] = None


@router.post("/track")
async def track_event(request: TrackEventRequest):
    """Track a user event"""
    analytics.track_event(
        event_type=request.event_type,
        user_id=request.user_id,
        metadata={
            'page': request.page,
            'data': request.data,
            'user_name': request.user_name,
            'session_id': request.session_id
        }
    )
    return {"success": True}


@router.post("/identify")
async def identify_user(request: UserIdentifyRequest):
    """Identify or update a user"""
    analytics.track_event(
        event_type='user_identified',
        user_id=request.user_id,
        metadata={
            'user_name': request.user_name,
            'email': request.email,
            **request.metadata
        }
    )
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
        "active_users": users
    }


@router.get("/engagement")
async def get_engagement():
    """Get engagement metrics"""
    stats = analytics.get_stats()
    events = analytics.get_events(limit=1000)

    # Calculate average session duration (simplified)
    session_durations = []
    sessions = {}

    for event in events:
        session_id = event.get('metadata', {}).get('session_id')
        if session_id:
            if session_id not in sessions:
                sessions[session_id] = {
                    'start': event['timestamp'],
                    'end': event['timestamp']
                }
            else:
                sessions[session_id]['end'] = event['timestamp']

    # Calculate durations
    from datetime import datetime
    for session in sessions.values():
        try:
            start = datetime.fromisoformat(session['start'])
            end = datetime.fromisoformat(session['end'])
            duration = (end - start).total_seconds() / 60  # minutes
            if duration < 120:  # Ignore >2h sessions
                session_durations.append(duration)
        except:
            pass

    avg_duration = sum(session_durations) / len(session_durations) if session_durations else 0

    return {
        'avg_session_duration_minutes': round(avg_duration, 1),
        'total_sessions': len(sessions),
        'events_per_session': round(len(events) / len(sessions), 1) if sessions else 0
    }


@router.get("/recent-events")
async def get_recent_events(
    limit: int = Query(50, description="Number of events to return")
):
    """Get recent events"""
    events = analytics.get_events(limit=limit)
    return {"events": events}
