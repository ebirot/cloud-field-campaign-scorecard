"""
Cloud Field Campaign Scorecard Platform
FastAPI Backend Application
Updated: 2026-05-29 - Added automated CSV refresh scheduler
"""
# Load environment variables FIRST before any other imports
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from app.core.config import settings
from app.api import tableau, slack, scorecard, export, data, insights, analytics, refresh, campaign, lead_scorecard, lead_cockpit, email, mappings
from app.services.scheduler import scheduler, init_scheduler, shutdown_scheduler
import os
import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Starting Cloud Field Campaign Scorecard...")
    init_scheduler()
    logger.info("✅ Application startup complete")

    yield

    # Shutdown
    logger.info("🛑 Shutting down application...")
    shutdown_scheduler()
    logger.info("✅ Application shutdown complete")


app = FastAPI(
    title="Cloud Field Campaign Scorecard API",
    description="Automated scorecard system for EMEA + AMER combined reporting",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tableau.router, prefix="/api/tableau", tags=["Tableau"])
app.include_router(slack.router, prefix="/api/slack", tags=["Slack"])
app.include_router(scorecard.router, prefix="/api/scorecard", tags=["Scorecard"])
# Data APIs - Now enabled with CSV files included in Git
app.include_router(export.router, prefix="/api/export", tags=["Export"])
app.include_router(data.router, prefix="/api/data", tags=["Data"])
app.include_router(insights.router, prefix="/api/insights", tags=["AI Insights"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(refresh.router, prefix="/api/refresh", tags=["Data Refresh"])
app.include_router(campaign.router, prefix="/api/campaign", tags=["Campaign Scorecard"])
app.include_router(email.router, prefix="/api/email", tags=["Email Scorecard"])
app.include_router(lead_scorecard.router, prefix="/api/lead", tags=["Lead Scorecard"])
app.include_router(lead_cockpit.router, prefix="/api/lead-cockpit", tags=["Lead Cockpit"])
app.include_router(mappings.router, prefix="/api/mappings", tags=["Mappings"])

@app.get("/")
async def root():
    """Serve the Health of Cloud scorecard V2"""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "frontend", "health_of_cloud_v2.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return {
        "message": "Cloud Field Campaign Scorecard API",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

@app.get("/overview")
async def overview():
    """Serve the overview dashboard"""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "frontend", "index_rob_design.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return {"error": "Overview page not found"}

@app.get("/admin")
async def admin():
    """Serve the unified admin dashboard"""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "frontend", "admin_unified.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    # Fallback to old admin
    frontend_path_old = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "frontend", "admin.html")
    if os.path.exists(frontend_path_old):
        return FileResponse(frontend_path_old)
    return {"error": "Admin page not found"}

@app.get("/admin_mappings.html")
async def admin_mappings():
    """Serve the standalone mappings interface (loaded in iframe)"""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "frontend", "admin_mappings.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return {"error": "Admin mappings page not found"}

@app.get("/email_scorecard")
async def email_scorecard():
    """Serve the email scorecard page"""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "frontend", "email_scorecard.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return {"error": "Email scorecard page not found"}

# Mount static files for frontend assets
# For Heroku: frontend should be at the same level as backend
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "frontend")
if os.path.exists(frontend_dir):
    # Mount js directory
    js_dir = os.path.join(frontend_dir, "js")
    if os.path.exists(js_dir):
        app.mount("/js", StaticFiles(directory=js_dir), name="js")

    # Mount css directory (only if exists and not empty)
    css_dir = os.path.join(frontend_dir, "css")
    if os.path.exists(css_dir) and os.listdir(css_dir):
        app.mount("/css", StaticFiles(directory=css_dir), name="css")

    # Mount public directory for images, etc.
    public_dir = os.path.join(frontend_dir, "public")
    if os.path.exists(public_dir):
        app.mount("/public", StaticFiles(directory=public_dir), name="public")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
# Reload Thu Jun 11 12:07:36 RDT 2026
