
import pytest
from app.services.llm_client import llm_client
from app.config import settings

@pytest.mark.real_llm
def test_real_llm_call():
    # Check if we have a valid API key configured
    if (llm_client.api_key == "your-api-key" or 
        not llm_client.api_key or 
        llm_client.api_key.startswith("sk-ant-api03-x34nNubDVCmJRLjEN4j6b7VWrzD7gdY08drya5j322RhvKDInJsGFnEiVpeTwP1XMsgJeIFkVRqKFUPu1WVsHQ")):
        pytest.skip("LLM API key not configured or is a placeholder. Skipping real LLM test.")

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
