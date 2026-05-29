"""
Health Check Routes
"""

from fastapi import APIRouter
from backend.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "phase": settings.phase,
        "live_execution": settings.live_execution,
        "active_assets": settings.get_active_assets(),
    }
