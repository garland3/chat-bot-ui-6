"""
API endpoints for application configuration.
"""
from fastapi import APIRouter
from typing import Dict, Any
from app.config import settings

router = APIRouter()

@router.get("/api/config")
async def get_app_config() -> Dict[str, Any]:
    """Get application configuration."""
    return {
        "app_name": settings.app_name,
        "version": "1.0.0",  # You can add version to settings if needed
    }