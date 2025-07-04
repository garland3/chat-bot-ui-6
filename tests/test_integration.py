from fastapi.testclient import TestClient
from app.main import app
from app.services.session_manager import session_manager
from unittest.mock import patch, MagicMock
import json
import requests

client = TestClient(app)

@patch('app.services.llm_client.LLMClient.chat_completion')
def test_full_chat_interaction_with_math_tool(mock_chat_completion):
    # Mock the first LLM response (non-streaming, tool call)
    mock_llm_response_tool_call = MagicMock(spec=requests.Response)
    mock_llm_response_tool_call.json.return_value = {
        "choices": [{
            "message": {
                "role": "assistant",
                "tool_calls": [{
                    "id": "call_math_123",
                    "function": {
                        "name": "BasicMathTool",
                        "arguments": "{\"operation\": \"add\", \"num1\": 10, \"num2\": 5}"
                    }
                }]
            }
        }]
    }

    # Mock the second LLM response (after tool execution, streaming)
    def mock_iter_lines_final():
        yield b'data: {"choices": [{"delta": {"content": "The result of 10 plus 5 is 15."}}]}'
        yield b'data: [DONE]'

    mock_chat_completion.side_effect = [mock_llm_response_tool_call, mock_iter_lines_final()]

    # 1. Create a session
    response = client.post("/chat", headers={"X-EMAIL-USER": "integration_test@example.com"})
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    assert session_id is not None

    # 2. Send a message that triggers the BasicMathTool
    message_payload = {"content": "What is 10 plus 5?"}
    chat_response = client.post(f"/chat/{session_id}/message", json=message_payload, headers={"X-EMAIL-USER": "integration_test@example.com"})
    assert chat_response.status_code == 200

    # Expect a streamed response with the tool output
    full_response_content = ""
    for chunk in chat_response.iter_bytes():
        full_response_content += chunk.decode('utf-8')
    
    # The actual LLM response will vary, but we expect the tool output to be part of it
    assert "15" in full_response_content # Assuming the LLM will state the result

    # 3. Clean up the session
    session_manager.delete_session(session_id)
    assert session_manager.get_session(session_id) is None

@patch('app.services.llm_client.LLMClient.chat_completion')
def test_full_chat_interaction_with_user_lookup_tool(mock_chat_completion):
    # Mock the first LLM response (non-streaming, tool call)
    mock_llm_response_tool_call = MagicMock(spec=requests.Response)
    mock_llm_response_tool_call.json.return_value = {
        "choices": [{
            "message": {
                "role": "assistant",
                "tool_calls": [{
                    "id": "call_user_lookup_123",
                    "function": {
                        "name": "UserLookupTool",
                        "arguments": "{\"email\": \"jane.smith@example.com\"}"
                    }
                }]
            }
        }]
    }

    # Mock the second LLM response (after tool execution, streaming)
    def mock_iter_lines_final():
        yield b'data: {"choices": [{"delta": {"content": "I found the user information for jane.smith@example.com. Jane Smith is a Product Manager in the Product department."}}]}'
        yield b'data: [DONE]'

    mock_chat_completion.side_effect = [mock_llm_response_tool_call, mock_iter_lines_final()]

    # 1. Create a session
    response = client.post("/chat", headers={"X-EMAIL-USER": "integration_test_user@example.com"})
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    assert session_id is not None

    # 2. Send a message that triggers the UserLookupTool
    message_payload = {"content": "Look up user jane.smith@example.com"}
    chat_response = client.post(f"/chat/{session_id}/message", json=message_payload, headers={"X-EMAIL-USER": "integration_test_user@example.com"})
    assert chat_response.status_code == 200

    # Expect a streamed response with the tool output
    full_response_content = ""
    for chunk in chat_response.iter_bytes():
        full_response_content += chunk.decode('utf-8')
    
    # The actual LLM response will vary, but we expect the tool output to be part of it
    assert "Jane Smith" in full_response_content
    assert "Product Manager" in full_response_content

    # 3. Clean up the session
    session_manager.delete_session(session_id)
    assert session_manager.get_session(session_id) is None

@patch('app.services.llm_client.LLMClient.chat_completion')
def test_full_chat_interaction_with_sql_query_tool(mock_chat_completion):
    # Mock the first LLM response (non-streaming, tool call)
    mock_llm_response_tool_call = MagicMock(spec=requests.Response)
    mock_llm_response_tool_call.json.return_value = {
        "choices": [{
            "message": {
                "role": "assistant",
                "tool_calls": [{
                    "id": "call_sql_123",
                    "function": {
                        "name": "SQLQueryTool",
                        "arguments": "{\"query\": \"SELECT * FROM customers\"}"
                    }
                }]
            }
        }]
    }

    # Mock the second LLM response (after tool execution, streaming)
    def mock_iter_lines_final():
        yield b'data: {"choices": [{"delta": {"content": "Here are all the customers: Alice Smith, Bob Johnson, and others from the database query results."}}]}'
        yield b'data: [DONE]'

    mock_chat_completion.side_effect = [mock_llm_response_tool_call, mock_iter_lines_final()]

    # 1. Create a session
    response = client.post("/chat", headers={"X-EMAIL-USER": "integration_test_sql@example.com"})
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    assert session_id is not None

    # 2. Send a message that triggers the SQLQueryTool
    message_payload = {"content": "Show me all customers"}
    chat_response = client.post(f"/chat/{session_id}/message", json=message_payload, headers={"X-EMAIL-USER": "integration_test_sql@example.com"})
    assert chat_response.status_code == 200

    # Expect a streamed response with the tool output
    full_response_content = ""
    for chunk in chat_response.iter_bytes():
        full_response_content += chunk.decode('utf-8')
    
    # The actual LLM response will vary, but we expect the tool output to be part of it
    assert "Alice Smith" in full_response_content
    assert "Bob Johnson" in full_response_content

    # 3. Clean up the session
    session_manager.delete_session(session_id)
    assert session_manager.get_session(session_id) is None

@patch('app.services.llm_client.LLMClient.chat_completion')
def test_full_chat_interaction_with_code_execution_tool(mock_chat_completion):
    # Mock the first LLM response (non-streaming, tool call)
    mock_llm_response_tool_call = MagicMock(spec=requests.Response)
    mock_llm_response_tool_call.json.return_value = {
        "choices": [{
            "message": {
                "role": "assistant",
                "tool_calls": [{
                    "id": "call_code_123",
                    "function": {
                        "name": "CodeExecutionTool",
                        "arguments": "{\"language\": \"python\", \"code\": \"print('Hello from code!')\"}"
                    }
                }]
            }
        }]
    }

    # Mock the second LLM response (after tool execution, streaming)
    def mock_iter_lines_final():
        yield b'data: {"choices": [{"delta": {"content": "I executed the code and got the output: Hello from code!"}}]}'
        yield b'data: [DONE]'

    mock_chat_completion.side_effect = [mock_llm_response_tool_call, mock_iter_lines_final()]

    # 1. Create a session
    response = client.post("/chat", headers={"X-EMAIL-USER": "integration_test_code@example.com"})
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    assert session_id is not None

    # 2. Send a message that triggers the CodeExecutionTool
    message_payload = {"content": "Execute python print('Hello from code!')"}
    chat_response = client.post(f"/chat/{session_id}/message", json=message_payload, headers={"X-EMAIL-USER": "integration_test_code@example.com"})
    assert chat_response.status_code == 200

    # Expect a streamed response with the tool output
    full_response_content = ""
    for chunk in chat_response.iter_bytes():
        full_response_content += chunk.decode('utf-8')
    
    # The actual LLM response will vary, but we expect the tool output to be part of it
    assert "Hello from code!" in full_response_content

    # 3. Clean up the session
    session_manager.delete_session(session_id)
    assert session_manager.get_session(session_id) is None
