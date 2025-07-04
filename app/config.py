
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    llm_provider: str = "openai"  # "openai" or "anthropic"
    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str = "your-api-key"
    llm_model_name: str = "gpt-3.5-turbo"
    test_mode: bool = False
    test_email: str = "test@test.com"
    disable_websocket: bool = False
    disable_llm_calls: bool = False
    system_prompt_override: Optional[str] = None
    app_name: str = "Galaxy Chat"
    llm_config_file: str = "config/llms.yml"
    background_color: str = "#0f0f0f"  # Pure dark background (no blue tint)
    accent_primary: str = "#00d4aa"  # Primary accent color (green highlight)
    accent_secondary: str = "#0099cc"  # Secondary accent color (blue)
    bg_secondary: str = "#1a1a1a"  # Secondary background color (dark gray)
    bg_tertiary: str = "#242424"  # Tertiary background color (lighter gray)
    bg_hover: str = "#2a2a2a"  # Hover state background (gray)
    bg_active: str = "#333333"  # Active state background (lighter gray)
    text_primary: str = "#ffffff"  # Primary text color
    text_secondary: str = "#b8b8b8"  # Secondary text color (neutral gray)
    text_muted: str = "#888888"  # Muted text color (darker gray)
    border_color: str = "#404040"  # Default border color (gray)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
