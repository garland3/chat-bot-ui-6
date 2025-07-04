from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from unittest.mock import patch, MagicMock
import json
import requests
from app.services.session_manager import session_manager
import pytest

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

@patch('app.routers.chat.log_session_event')
@patch('app.services.llm_client.LLMClient.chat_completion')
@patch('app.routers.chat.tool_manager')
def test_chat_message_llm_enabled_streaming(mock_tool_manager, mock_chat_completion, mock_log_session_event):
    # Configure the log_session_event mock to accept multiple calls
    mock_log_session_event.return_value = None
    
    # Ensure no tools are passed for this test
    mock_tool_manager.get_all_tool_definitions.return_value = []

    # Mock the first LLM response (non-streaming, no tool call)
    mock_llm_response_no_tool = MagicMock(spec=requests.Response)
    mock_llm_response_no_tool.json.return_value = {"choices": [{"message": {"content": "Hello"}}]}

    # Mock the second LLM response (streaming) - now a synchronous generator
    def mock_iter_lines():
        yield b'data: {"choices": [{"delta": {"content": " world"}}]}'
        yield b'data: {"choices": [{"delta": {"content": "!"}}]}'
        yield b'data: [DONE]'

    mock_chat_completion.side_effect = [mock_llm_response_no_tool, mock_iter_lines()]

    response = client.post("/chat", headers={"X-EMAIL-USER": "test@example.com"})
    session_id = response.json()["session_id"]

    message_payload = {"content": "Hello"}
    chat_response = client.post(f"/chat/{session_id}/message", json=message_payload, headers={"X-EMAIL-USER": "test@example.com"})
    assert chat_response.status_code == 200
    
    # Manually consume the streaming response
    full_response_content = ""
    for chunk in chat_response.iter_bytes():
        full_response_content += chunk.decode('utf-8')

    assert full_response_content == "Hello world!"
    
    # Assertions for LLM calls - account for system message being added
    assert mock_chat_completion.call_count == 2
    # First call includes system message
    expected_system_message = {"role": "system", "content": "You are a helpful AI assistant. You provide accurate, helpful, and concise responses to user questions. You can use tools when available to enhance your responses with real-time data and functionality."}
    expected_messages_first = [
        expected_system_message,
        {"role": "user", "content": "Hello"}
    ]
    mock_chat_completion.assert_any_call(messages=expected_messages_first, tools=[], stream=False)
    mock_chat_completion.assert_any_call(messages=expected_messages_first, stream=True)

@patch('app.routers.chat.log_session_event')
@patch('app.services.llm_client.LLMClient.chat_completion')
@patch('app.routers.chat.tool_manager')  # Patch the tool_manager instance in the router
def test_chat_message_tool_call(mock_tool_manager, mock_chat_completion, mock_log_session_event):
    # Configure the log_session_event mock to accept multiple calls
    mock_log_session_event.return_value = None
    
    # Ensure tools are passed for this test
    mock_tool_manager.get_all_tool_definitions.return_value = [
        # Add a dummy tool definition for the mock to return
        {"type": "function", "function": {"name": "BasicMathTool", "description": "", "parameters": {}}}
    ]

    # Mock the tool execution
    mock_math_tool = MagicMock()
    mock_math_tool.execute.return_value = {"result": 8}
    mock_tool_manager.get_tool.return_value = mock_math_tool

    # Mock the first LLM response (non-streaming, tool call)
    mock_llm_response_tool_call = MagicMock(spec=requests.Response)
    mock_llm_response_tool_call.json.return_value = {
        "choices": [{
            "message": {
                "role": "assistant",
                "tool_calls": [{
                    "id": "call_123",
                    "function": {
                        "name": "BasicMathTool",
                        "arguments": "{\"operation\": \"add\", \"num1\": 5, \"num2\": 3}"
                    }
                }]
            }
        }]
    }

    # Mock the second LLM response (after tool execution, streaming) - now a synchronous generator
    def mock_iter_lines_final():
        yield b'data: {"choices": [{"delta": {"content": "The result is 8."}}]}'
        yield b'data: [DONE]'

    mock_chat_completion.side_effect = [mock_llm_response_tool_call, mock_iter_lines_final()]

    # Create a session inside the test function
    response = client.post("/chat", headers={"X-EMAIL-USER": "test@example.com"})
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    assert session_id is not None

    message_payload = {"content": "What is 5 + 3?"}
    chat_response = client.post(f"/chat/{session_id}/message", json=message_payload, headers={"X-EMAIL-USER": "test@example.com"})

    assert chat_response.status_code == 200
    
    # Manually consume the streaming response
    full_response_content = ""
    for chunk in chat_response.iter_bytes():
        full_response_content += chunk.decode('utf-8')

    assert full_response_content == "The result is 8."

    # Assertions for LLM calls and tool execution
    assert mock_chat_completion.call_count == 2
    mock_tool_manager.get_tool.assert_called_once_with("BasicMathTool")
    mock_math_tool.execute.assert_called_once_with(operation="add", num1=5, num2=3)

@patch('app.routers.chat.log_session_event')
@patch('app.services.llm_client.LLMClient.chat_completion')
@patch('app.routers.chat.tool_manager')
def test_conversation_persistence(mock_tool_manager, mock_chat_completion, mock_log_session_event):
    # Configure the log_session_event mock to accept multiple calls
    mock_log_session_event.return_value = None
    
    # Ensure no tools are passed for this test
    mock_tool_manager.get_all_tool_definitions.return_value = []

    # Mock LLM responses
    mock_llm_response1 = MagicMock(spec=requests.Response)
    mock_llm_response1.json.return_value = {"choices": [{"message": {"content": "Hello there!"}}]}

    def mock_iter_lines2():
        yield b'data: {"choices": [{"delta": {"content": "How can I help you further?"}}]}'
        yield b'data: [DONE]'

    mock_llm_response2 = MagicMock(spec=requests.Response)
    mock_llm_response2.json.return_value = {"choices": [{"message": {"content": "I am doing great!"}}]}

    def mock_iter_lines3():
        yield b'data: {"choices": [{"delta": {"content": "That\'s wonderful to hear!"}}]}'
        yield b'data: [DONE]'

    mock_chat_completion.side_effect = [
        mock_llm_response1, mock_iter_lines2(),
        mock_llm_response2, mock_iter_lines3()
    ]

    # 1. Create a session
    response = client.post("/chat", headers={"X-EMAIL-USER": "persistence_test@example.com"})
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    assert session_id is not None

    # 2. Send first message
    message_payload1 = {"content": "Hi"}
    chat_response1 = client.post(f"/chat/{session_id}/message", json=message_payload1, headers={"X-EMAIL-USER": "persistence_test@example.com"})
    assert chat_response1.status_code == 200
    
    full_response_content1 = ""
    for chunk in chat_response1.iter_bytes():
        full_response_content1 += chunk.decode('utf-8')

    assert full_response_content1 == "Hello there!How can I help you further?"

    # Verify session messages after first interaction
    session_data = session_manager.get_session(session_id)
    expected_system_message = {"role": "system", "content": "You are a helpful AI assistant. You provide accurate, helpful, and concise responses to user questions. You can use tools when available to enhance your responses with real-time data and functionality."}
    assert len(session_data["messages"]) == 3
    assert session_data["messages"][0] == expected_system_message
    assert session_data["messages"][1]["role"] == "user"
    assert session_data["messages"][1]["content"] == "Hi"
    assert session_data["messages"][2]["role"] == "assistant"
    assert session_data["messages"][2]["content"] == "Hello there!How can I help you further?"

    # 3. Send second message in the same session
    message_payload2 = {"content": "How are you?"}
    chat_response2 = client.post(f"/chat/{session_id}/message", json=message_payload2, headers={"X-EMAIL-USER": "persistence_test@example.com"})
    assert chat_response2.status_code == 200
    
    full_response_content2 = ""
    for chunk in chat_response2.iter_bytes():
        full_response_content2 += chunk.decode('utf-8')

    assert full_response_content2 == "I am doing great!That's wonderful to hear!"

    # Verify session messages after second interaction
    session_data = session_manager.get_session(session_id)
    assert len(session_data["messages"]) == 5
    assert session_data["messages"][3]["role"] == "user"
    assert session_data["messages"][3]["content"] == "How are you?"
    assert session_data["messages"][4]["role"] == "assistant"
    assert session_data["messages"][4]["content"] == "I am doing great!That's wonderful to hear!"

    # Clean up the session
    session_manager.delete_session(session_id)
    assert session_manager.get_session(session_id) is None