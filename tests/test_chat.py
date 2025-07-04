from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from unittest.mock import patch, MagicMock
import json
import requests

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

@patch('app.services.llm_client.LLMClient.chat_completion')
@patch('app.routers.chat.tool_manager')
def test_chat_message_llm_enabled_streaming(mock_tool_manager, mock_chat_completion):
    # Ensure no tools are passed for this test
    mock_tool_manager.get_all_tool_definitions.return_value = []

    # Mock the first LLM response (non-streaming, no tool call)
    mock_llm_response_no_tool = MagicMock(spec=requests.Response)
    mock_llm_response_no_tool.json.return_value = {"choices": [{"message": {"content": "Hello"}}]}

    # Mock the second LLM response (streaming)
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
    assert chat_response.text == "Hello world!"
    
    # Assertions for LLM calls
    assert mock_chat_completion.call_count == 2
    mock_chat_completion.assert_any_call(messages=[{"role": "user", "content": "Hello"}], tools=[], stream=False)
    mock_chat_completion.assert_any_call(messages=[{"role": "user", "content": "Hello"}], stream=True)

@patch('app.services.llm_client.LLMClient.chat_completion')
@patch('app.routers.chat.tool_manager') # Patch tool_manager in the router
def test_chat_message_tool_call(mock_router_tool_manager, mock_chat_completion):
    # Ensure tools are passed for this test
    mock_router_tool_manager.get_all_tool_definitions.return_value = [
        # Add a dummy tool definition for the mock to return
        {"type": "function", "function": {"name": "BasicMathTool", "description": "", "parameters": {}}}
    ]

    # Mock the tool execution
    mock_math_tool = MagicMock()
    mock_math_tool.execute.return_value = {"result": 8}
    mock_router_tool_manager.get_tool.return_value = mock_math_tool

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

    # Mock the second LLM response (after tool execution, streaming)
    def mock_iter_lines_final():
        yield b'data: {"choices": [{"delta": {"content": "The result is 8."}}]}'
        yield b'data: [DONE]'

    mock_chat_completion.side_effect = [mock_llm_response_tool_call, mock_iter_lines_final()]

    response = client.post("/chat", headers={"X-EMAIL-USER": "test@example.com"})
    session_id = response.json()["session_id"]

    message_payload = {"content": "What is 5 + 3?"}
    chat_response = client.post(f"/chat/{session_id}/message", json=message_payload, headers={"X-EMAIL-USER": "test@example.com"})

    assert chat_response.status_code == 200
    assert chat_response.text == "The result is 8."

    # Assertions for LLM calls and tool execution
    assert mock_chat_completion.call_count == 2
    mock_router_tool_manager.get_tool.assert_called_once_with("BasicMathTool")
    mock_math_tool.execute.assert_called_once_with(operation="add", num1=5, num2=3)
