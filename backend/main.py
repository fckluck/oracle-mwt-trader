"""
FastAPI Application

Oracle MWT Trader Phase 1 - Observation and Paper Trading
"""

import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.routes import health, demo, signals

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Create app
app = FastAPI(
    title=settings.app_name,
    description="Phase 1: Multi-wallet tracking, conviction detection, paper trading",
    version="0.1.0",
)

# Include routers
app.include_router(health.router)
app.include_router(demo.router)
app.include_router(signals.router)


@app.on_event("startup")
async def startup():
    """Startup event"""
    logger.info(f"🚀 {settings.app_name} starting...")
    logger.info(f"Phase: {settings.phase}")
    logger.info(f"Live execution: {settings.live_execution}")


@app.on_event("shutdown")
async def shutdown():
    """Shutdown event"""
    logger.info(f"🛑 {settings.app_name} shutting down...")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.app_name,
        "version": "0.1.0",
        "phase": settings.phase,
        "live_execution": settings.live_execution,
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
