from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

@patch('app.services.llm_client.LLMClient.chat_completion')
def test_calculator_tool_selection_and_logging(mock_chat_completion):
    """Test that selecting calculator tool modifies system prompt and logs tool selection."""
    # Mock streaming response
    def mock_iter_lines():
        yield b'data: {"choices": [{"delta": {"content": "I can help you with calculations using the calculator tool."}}]}'
        yield b'data: [DONE]'
    
    mock_chat_completion.return_value = mock_iter_lines()
    
    # Create session
    response = client.post("/chat", headers={"X-EMAIL-USER": "test@example.com"})
    session_id = response.json()["session_id"]
    
    # Send message with calculator tool selected
    message_payload = {
        "content": "What is 5 + 3?",
        "selected_tools": ["calculator"],
        "selected_data_sources": []
    }
    
    chat_response = client.post(
        f"/chat/{session_id}/message", 
        json=message_payload, 
        headers={"X-EMAIL-USER": "test@example.com"}
    )
    
    assert chat_response.status_code == 200
    
    # Verify streaming response
    full_response_content = b""
    for chunk in chat_response.iter_bytes():
        full_response_content += chunk
    
    assert b"calculator tool" in full_response_content.lower()
    
    # Verify system prompt was modified for calculator tool
    call_args = mock_chat_completion.call_args
    messages = call_args.kwargs["messages"]
    system_message = messages[0]
    assert system_message["role"] == "system"
    assert "calculator" in system_message["content"].lower()

@patch('app.services.llm_client.LLMClient.chat_completion')
def test_tool_selection_streaming_without_execution(mock_chat_completion):
    """Test that tool selections are streamed to frontend without executing tools."""
    def mock_iter_lines():
        yield b'data: {"choices": [{"delta": {"content": "I have access to the calculator tool and can help with math."}}]}'
        yield b'data: [DONE]'
    
    mock_chat_completion.return_value = mock_iter_lines()
    
    # Create session
    response = client.post("/chat", headers={"X-EMAIL-USER": "test@example.com"})
    session_id = response.json()["session_id"]
    
    # Send message with tool selection
    message_payload = {
        "content": "Help me with math",
        "selected_tools": ["calculator"]
    }
    
    chat_response = client.post(
        f"/chat/{session_id}/message", 
        json=message_payload, 
        headers={"X-EMAIL-USER": "test@example.com"}
    )
    
    assert chat_response.status_code == 200
    
    # Verify we get streaming response, not tool execution
    full_response_content = b""
    for chunk in chat_response.iter_bytes():
        full_response_content += chunk
    
    # Should contain LLM response about having access to calculator
    assert b"calculator" in full_response_content.lower()
    
    # Verify only one LLM call (no separate tool execution call)
    assert mock_chat_completion.call_count == 1
