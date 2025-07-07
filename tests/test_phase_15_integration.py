"""
Integration tests for Phase 15 architecture - streaming-only approach with tool configuration.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_session_based_tool_configuration():
    """Test that tools are treated as configuration in the session-based API."""
    # Create session
    response = client.post("/chat", headers={"X-EMAIL-USER": "test@example.com"})
    assert response.status_code == 200
    session_data = response.json()
    session_id = session_data["session_id"]
    
    # Send message with tool selection
    response = client.post(f"/chat/{session_id}/message", json={
        "content": "What is 2+2?",
        "selected_tools": ["calculator"],
        "selected_data_sources": []
    })
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
    
    # Check that tool selection is streamed
    response_text = response.text
    assert '"type": "tool_selected"' in response_text
    assert '"tool": "calculator"' in response_text

def test_system_prompt_generation():
    """Test that system prompt is properly generated with tool selection."""
    # Create session
    response = client.post("/chat", headers={"X-EMAIL-USER": "test@example.com"})
    assert response.status_code == 200
    session_data = response.json()
    session_id = session_data["session_id"]
    
    # Send message with calculator tool
    response = client.post(f"/chat/{session_id}/message", json={
        "content": "Help with math",
        "selected_tools": ["calculator"],
        "selected_data_sources": ["products"]
    })
    
    assert response.status_code == 200
    # The system prompt generation should be logged in session events
    # This test verifies the API accepts the parameters without error

def test_streaming_response_format():
    """Test that streaming response follows the new format."""
    # Create session
    response = client.post("/chat", headers={"X-EMAIL-USER": "test@example.com"})
    assert response.status_code == 200
    session_data = response.json()
    session_id = session_data["session_id"]
    
    # Send message
    response = client.post(f"/chat/{session_id}/message", json={
        "content": "Hello",
        "selected_tools": [],
        "selected_data_sources": []
    })
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
    
    # Should end with [DONE]
    response_text = response.text
    assert "data: [DONE]" in response_text

def test_backward_compatibility():
    """Test that the API maintains backward compatibility."""
    # Create session
    response = client.post("/chat", headers={"X-EMAIL-USER": "test@example.com"})
    assert response.status_code == 200
    session_data = response.json()
    session_id = session_data["session_id"]
    
    # Send message without new parameters (should default to empty lists)
    response = client.post(f"/chat/{session_id}/message", json={
        "content": "Hello"
    })
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

def test_parameter_validation():
    """Test parameter validation in the new API."""
    # Create session
    response = client.post("/chat", headers={"X-EMAIL-USER": "test@example.com"})
    assert response.status_code == 200
    session_data = response.json()
    session_id = session_data["session_id"]
    
    # Send message with invalid selected_tools (not a list)
    response = client.post(f"/chat/{session_id}/message", json={
        "content": "Hello",
        "selected_tools": "not_a_list"
    })
    
    assert response.status_code == 400
    assert "selected_tools must be a list" in response.json()["detail"]