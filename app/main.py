"""
QKREW Backend - Main Application
FastAPI + Supabase
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import db
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Import routers
from app.api.v1 import auth, users, projects, tasks, teams, leaves, incidents, events, notes, chatbot
from app.api.v1.operations import software_requests_router, notice_period_router, business_trips_router
from app.api.v1.features import dashboard_router, analytics_router, profile_router
from app.api.v1.leave_conflicts import leave_conflicts_router
from app.api.v1.leave_manager import leave_manager_router
from app.api.v1.employees import employees_router
from app.api.v1.esp_manager import esp_manager_router
from app.api.v1.esp_simulator import router as esp_simulator_router

# ============================================================================
# CREATE FASTAPI APP
# ============================================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Employee Resource Management & Project Tracking Platform",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ============================================================================
# CORS MIDDLEWARE - Support for local development and production deployment
# ============================================================================

import os

# Get allowed origins from environment variable or use defaults
ALLOWED_ORIGINS_ENV = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = []

# Add production origins from environment variable (comma-separated)
if ALLOWED_ORIGINS_ENV:
    production_origins = [origin.strip() for origin in ALLOWED_ORIGINS_ENV.split(",") if origin.strip()]
    allowed_origins.extend(production_origins)

# Always include local development origins
local_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8000",
]
allowed_origins.extend(local_origins)

# Remove duplicates while preserving order
allowed_origins = list(dict.fromkeys(allowed_origins))

print(f"🌐 CORS Allowed Origins: {allowed_origins}")

# When using credentials, cannot use wildcard "*"
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ============================================================================
# REQUEST LOGGING MIDDLEWARE
# ============================================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and responses"""
    # Skip logging for OPTIONS requests (CORS preflight)
    if request.method == "OPTIONS":
        return await call_next(request)
    
    start_time = time.time()
    
    # Log request
    logger.info(f"🔵 {request.method} {request.url.path}")
    if request.query_params:
        logger.info(f"   Query: {dict(request.query_params)}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log response
    status_emoji = "✅" if response.status_code < 400 else "❌"
    logger.info(f"{status_emoji} {request.method} {request.url.path} - Status: {response.status_code} - Duration: {duration:.2f}s")
    
    return response

# ============================================================================
# STARTUP & SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    print("=" * 60)
    print("Starting QKREW Backend...")
    print("=" * 60)
    db.connect()
    print(f"[OK] Server running on http://localhost:8000")
    print(f"[OK] API Docs: http://localhost:8000/docs")
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("Shutting down QKREW Backend...")


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected" if db.client else "disconnected",
    }


# ============================================================================
# API ROUTERS
# ============================================================================

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])
app.include_router(teams.router, prefix="/api/v1/teams", tags=["Teams"])
app.include_router(leaves.router, prefix="/api/v1/leaves", tags=["Leaves"])
app.include_router(incidents.router, prefix="/api/v1/incidents", tags=["Incidents"])
app.include_router(events.router, prefix="/api/v1/events", tags=["Events"])
app.include_router(notes.router, prefix="/api/v1", tags=["Notes"])

# Operations
app.include_router(software_requests_router, prefix="/api/v1/software-requests", tags=["Software Requests"])
app.include_router(notice_period_router, prefix="/api/v1/notice-period", tags=["Notice Period"])
app.include_router(business_trips_router, prefix="/api/v1/business-trips", tags=["Business Trips"])

# Features
app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(chatbot.router, prefix="/api/v1/chatbot", tags=["Chatbot"])
app.include_router(profile_router, prefix="/api/v1/profile", tags=["Profile"])
app.include_router(leave_conflicts_router, prefix="/api/v1/leave-conflicts", tags=["Leave Conflicts"])
app.include_router(leave_manager_router, prefix="/api/v1/leave-manager", tags=["Leave Manager"])
app.include_router(employees_router, prefix="/api/v1/employees", tags=["Employees"])
app.include_router(esp_manager_router, prefix="/api/v1/esp", tags=["ESP Manager"])
app.include_router(esp_simulator_router, prefix="/api/v1/esp-simulator", tags=["ESP Simulator"])
# app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
# app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
# app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])
# app.include_router(teams.router, prefix="/api/v1/teams", tags=["Teams"])
# app.include_router(employees.router, prefix="/api/v1/employees", tags=["Employees"])
# app.include_router(leaves.router, prefix="/api/v1/leaves", tags=["Leaves"])
# app.include_router(incidents.router, prefix="/api/v1/incidents", tags=["Incidents"])
# app.include_router(esp.router, prefix="/api/v1/esp", tags=["ESP"])
# app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
# app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])


# ============================================================================
# RUN SERVER (for development)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
