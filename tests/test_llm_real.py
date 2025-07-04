
import pytest
from app.services.llm_client import llm_client
from app.config import settings

@pytest.mark.real_llm
def test_real_llm_call():
    if settings.llm_api_key == "your-api-key" or not settings.llm_api_key:
        pytest.skip("LLM API key not configured. Skipping real LLM test.")

    try:
        messages = [{"role": "user", "content": "Hello, what is your name?"}]
        response = llm_client.chat_completion(messages=messages, stream=False)
        response_json = response.json()

        assert response_json is not None
        assert "choices" in response_json
        assert len(response_json["choices"]) > 0
        assert "message" in response_json["choices"][0]
        assert "content" in response_json["choices"][0]["message"]
        assert len(response_json["choices"][0]["message"]["content"]) > 0

    except Exception as e:
        pytest.fail(f"Real LLM call failed: {e}")
