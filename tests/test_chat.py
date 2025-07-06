from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import requests
from app.main import app
from app.config import settings
from app.services.session_manager import session_manager

client = TestClient(app)

def test_chat_message_llm_disabled():
    settings.disable_llm_calls = True
    response = client.post("/chat", headers={"X-EMAIL-USER": "test@example.com"})
    session_id = response.json()["session_id"]

    message_payload = {"content": "Hello"}
    chat_response = client.post(f"/chat/{session_id}/message", json=message_payload, headers={"X-EMAIL-USER": "test@example.com"})
    assert chat_response.status_code == 200
    assert chat_response.json() == {"response": "LLM calls are disabled."}
    settings.disable_llm_calls = False

@patch('app.routers.chat.llm_client')
def test_get_llms_endpoint(mock_llm_client):
    mock_llm_client.get_available_llms.return_value = ["LLM A", "LLM B", "LLM C"]
    response = client.get("/llms")
    assert response.status_code == 200
    assert response.json() == ["LLM A", "LLM B", "LLM C"]

@patch('app.routers.chat.llm_client')
def test_download_chat_session(mock_llm_client):
    # Mock current_llm_name
    mock_llm_client.current_llm_name = "Test LLM"

    # 1. Create a session
    response = client.post("/chat", headers={"X-EMAIL-USER": "download_test@example.com"})
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    assert session_id is not None

    # 2. Add some messages and selected tools to the session
    session_manager.update_session_messages(session_id, [
        {"role": "user", "content": "Hello, AI!"},
        {"role": "assistant", "content": "Hi there! How can I help you?"}
    ])
    session_manager.update_session_tools(session_id, ["calculator"])

    # 3. Request to download the chat session
    download_response = client.get(f"/chat/{session_id}/download")
    assert download_response.status_code == 200
    assert "text/plain" in download_response.headers["Content-Type"]
    assert f"filename=\"chat_session_{session_id}.txt\"" in download_response.headers["Content-Disposition"]

    # 4. Verify the content of the downloaded file
    downloaded_content = download_response.text
    assert f"Chat Session ID: {session_id}" in downloaded_content
    assert "Selected LLM: Test LLM" in downloaded_content
    assert "Selected Tools: calculator" in downloaded_content
    assert "User: Hello, AI!" in downloaded_content
    assert "Assistant: Hi there! How can I help you?" in downloaded_content

    # Clean up the session
    session_manager.delete_session(session_id)
    assert session_manager.get_session(session_id) is None