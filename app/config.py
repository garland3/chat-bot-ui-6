
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    llm_provider: str = "openai"  # "openai" or "anthropic"
    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str = "your-api-key"
    llm_model_name: str = "gpt-3.5-turbo"
    test_mode: bool = False
    test_email: str = "test@test.com"
    disable_websocket: bool = False
    disable_llm_calls: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
