
from app.config import settings

def test_config_loading():
    assert settings.llm_base_url is not None
    assert settings.llm_api_key is not None
    assert settings.llm_model_name is not None
