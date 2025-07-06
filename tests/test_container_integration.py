import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.session_manager import session_manager
from unittest.mock import MagicMock
import json
import requests

client = TestClient(app)

@pytest.fixture
def mock_chat_completion_fixture(mocker):
    mock_chat_completion = mocker.patch('app.services.llm_client.LLMClient.chat_completion')
    # Default mock for chat_completion to return a simple response
    mock_chat_completion.return_value = iter([b'data: {"choices": [{"delta": {"content": "Mocked LLM response."}}]}'])
    return mock_chat_completion

def test_health_endpoint_container():
    """Test the health endpoint of the container."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_chat_session_container():
    """Test creating a chat session in the containerized environment."""
    response = client.post("/chat", headers={"X-EMAIL-USER": "container_test@example.com"})
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    assert session_id is not None
    assert session_manager.get_session(session_id) is not None

def test_chat_message_flow_container(mock_chat_completion_fixture):
    """Test a basic chat message flow in the containerized environment."""
    # Create a session
    response = client.post("/chat", headers={"X-EMAIL-USER": "container_chat_test@example.com"})
    session_id = response.json()["session_id"]

    # Send a message
    message_payload = {"content": "Hello, container!"}
    chat_response = client.post(f"/chat/{session_id}/message", json=message_payload, headers={"X-EMAIL-USER": "container_chat_test@example.com"})
    assert chat_response.status_code == 200

    # Expect a streamed response
    full_response_content = ""
    for chunk in chat_response.iter_bytes():
        full_response_content += chunk.decode('utf-8')
    
    assert "Mocked LLM response." in full_response_content

def test_llm_selection_container(mock_chat_completion_fixture):
    """Test LLM selection in the containerized environment."""
    # Create a session
    response = client.post("/chat", headers={"X-EMAIL-USER": "container_llm_test@example.com"})
    session_id = response.json()["session_id"]

    # Get available LLMs
    llm_response = client.get("/llms")
    assert llm_response.status_code == 200
    llm_names = llm_response.json()
    assert len(llm_names) > 0

    # Select an LLM and send a message
    selected_llm = llm_names[0] # Select the first available LLM
    message_payload = {"content": "Hello with specific LLM!", "llm_name": selected_llm}
    chat_response = client.post(f"/chat/{session_id}/message", json=message_payload, headers={"X-EMAIL-USER": "container_llm_test@example.com"})
    assert chat_response.status_code == 200

    full_response_content = ""
    for chunk in chat_response.iter_bytes():
        full_response_content += chunk.decode('utf-8')
    
    assert "Mocked LLM response." in full_response_content

def test_chat_download_container():
    """Test chat session download in the containerized environment."""
    # Create a session
    response = client.post("/chat", headers={"X-EMAIL-USER": "container_download_test@example.com"})
    session_id = response.json()["session_id"]

    # Add some messages to the session
    session_manager.update_session_messages(session_id, [
        {"role": "user", "content": "First message."},
        {"role": "assistant", "content": "First response."}
    ])

    # Download the chat session
    download_response = client.get(f"/chat/{session_id}/download")
    assert download_response.status_code == 200
    assert "text/plain" in download_response.headers["Content-Type"]
    assert f"filename=\"chat_session_{session_id}.txt\"" in download_response.headers["Content-Disposition"]

    downloaded_content = download_response.text
    assert "First message." in downloaded_content
    assert "First response." in downloaded_content
