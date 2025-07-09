
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file explicitly
load_dotenv("/app/.env", override=True)

class Settings(BaseSettings):
    # Application Configuration
    app_name: str = "Chat Bot UI 6"
    
    # LLM Configuration  
    llm_config_file: str = "config/llms.yml"
    llm_provider: str = "openai"  # Fallback for legacy support
    llm_base_url: str = "https://api.openai.com/v1"  # Fallback for legacy support
    llm_api_key: str = "your-api-key"  # Fallback for legacy support
    llm_model_name: str = "gpt-3.5-turbo"  # Fallback for legacy support
    
    # Development & Testing
    test_mode: bool = False
    test_email: str = "test@test.com"
    disable_websocket: bool = False
    disable_llm_calls: bool = False
    system_prompt_override: Optional[str] = None

    model_config = SettingsConfigDict(extra="ignore")

settings = Settings()
