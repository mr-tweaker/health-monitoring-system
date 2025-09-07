"""
Health Monitoring System - Main FastAPI Application
Day 1: Foundation & Data Pipeline
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from datetime import datetime
import logging

# Import our modules
from app.api import patients, alerts, dashboard
from app.api import integrations
from app.database import init_db
from app.utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Health Monitoring System",
    description="Real-time health monitoring with AI-powered anomaly detection",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(patients.router, prefix="/api/patients", tags=["patients"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(integrations.router)

# Bind OAuth callback paths at root (providers often require exact paths)
app.add_api_route("/oauth/callback/withings", integrations.withings_callback, methods=["GET"])
app.add_api_route("/oauth/callback/fitbit", integrations.fitbit_callback, methods=["GET"])

@app.on_event("startup")
async def startup_event():
    """Initialize database and other startup tasks"""
    logger.info("Starting Health Monitoring System...")
    try:
        # Initialize database
        init_db()
        logger.info("Database initialized successfully")
        
        # Create data directories if they don't exist
        os.makedirs("data", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        os.makedirs("ml/models", exist_ok=True)
        
        logger.info("Health Monitoring System started successfully")
    except Exception as e:
        logger.error(f"Failed to start system: {e}")
        raise

@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "AI Health Monitoring System",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "patients": "/api/patients",
            "alerts": "/api/alerts",
            "dashboard": "/api/dashboard"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        from app.database import get_db
        db = next(get_db())
        
        # Check if data directory exists
        data_dir_exists = os.path.exists("data")
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected",
            "data_directory": "available" if data_dir_exists else "missing",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/api/status")
async def system_status():
    """Detailed system status for monitoring"""
    try:
        from app.database import get_db
        db = next(get_db())
        
        # Get basic stats
        stats = {
            "system": {
                "status": "operational",
                "uptime": "running",
                "timestamp": datetime.now().isoformat()
            },
            "database": {
                "status": "connected",
                "type": "sqlite"
            },
            "services": {
                "api": "running",
                "ml_models": "ready",
                "alert_system": "active"
            }
        }
        
        return stats
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "error", "message": str(e)}
        )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
