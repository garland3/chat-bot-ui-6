from fastapi import APIRouter
from app.config import settings

router = APIRouter(prefix="/api/theme", tags=["theme"])

@router.get("/config")
async def get_theme_config():
    """
    Get the current theme configuration including colors and styling options.
    This endpoint provides all the configurable theme values for the frontend.
    """
    return {
        "app_name": settings.app_name,
        "background_color": settings.background_color,
        "accent_primary": settings.accent_primary,
        "accent_secondary": settings.accent_secondary,
        "bg_secondary": settings.bg_secondary,
        "bg_tertiary": settings.bg_tertiary,
        "bg_hover": settings.bg_hover,
        "bg_active": settings.bg_active,
        "text_primary": settings.text_primary,
        "text_secondary": settings.text_secondary,
        "text_muted": settings.text_muted,
        "border_color": settings.border_color
    }
