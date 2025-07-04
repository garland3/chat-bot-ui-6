from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from unittest.mock import patch

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch('app.services.llm_client.LLMClient.chat_completion')
def test_llm_health_check_success(mock_chat_completion):
    mock_chat_completion.return_value.json.return_value = {"choices": [{"message": {"content": "hi"}}]}
    with TestClient(app) as client:
        # The startup event is triggered when the TestClient is initialized
        pass
    mock_chat_completion.assert_called_once_with(messages=[{"role": "user", "content": "hi"}])

@patch('app.services.llm_client.LLMClient.chat_completion')
def test_llm_health_check_failure(mock_chat_completion):
    mock_chat_completion.side_effect = Exception("LLM connection error")
    with TestClient(app) as client:
        # The startup event is triggered when the TestClient is initialized
        pass
    mock_chat_completion.assert_called_once_with(messages=[{"role": "user", "content": "hi"}])

def test_llm_health_check_disabled():
    settings.disable_llm_calls = True
    with patch('app.services.llm_client.LLMClient.chat_completion') as mock_chat_completion:
        with TestClient(app) as client:
            pass
        mock_chat_completion.assert_not_called()
    settings.disable_llm_calls = False