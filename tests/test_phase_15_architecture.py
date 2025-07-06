
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Part 1: Test-Driven Development Setup

@pytest.mark.xfail(reason="Fails because the current implementation executes tools instead of treating them as configuration.")
def test_tool_selection_as_configuration():
    """
    Tests that tool selection is treated as a configuration parameter,
    not an executable action. The response should indicate the tool was
    selected, not that it was executed.
    """
    response = client.post("/chat", json={"message": "What is 2+2?", "selected_tools": ["calculator"]})
    assert response.status_code == 200
    # Instead of a calculated answer, we expect a confirmation of the tool being ready.
    assert "tool:selected calculator" in response.text
    assert "4" not in response.text

@pytest.mark.xfail(reason="Fails because the system prompt is not yet modified by tool selection.")
def test_system_prompt_modification_with_tool_selection():
    """
    Tests that the system prompt is modified when a tool is selected.
    This test will require a way to inspect the system prompt used by the LLM.
    For now, we'll check for a side effect in the response that indicates
    the modified prompt was used.
    """
    response = client.post("/chat", json={"message": "What is the capital of France?", "selected_tools": ["search"]})
    assert response.status_code == 200
    # A mock response should indicate the search tool's context was added.
    assert "Using search tool to find information." in response.text

@pytest.mark.xfail(reason="Fails because the dual LLM call pattern is still in use.")
def test_single_streaming_response_pattern():
    """
    Tests that the entire interaction is a single streaming response,
    eliminating the dual LLM call pattern.
    """
    with client.stream("POST", "/chat", json={"message": "Stream test"}) as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        # A single, continuous stream should be received.
        # This is harder to assert directly without a more complex test setup,
        # but we can check for a continuous stream of chunks.
        for chunk in response.iter_bytes():
            assert isinstance(chunk, bytes)

@pytest.mark.xfail(reason="Fails because the API does not yet handle llm_name.")
def test_alpinejs_integration_contract_model_selection():
    """
    Tests the API contract for Alpine.js integration, specifically for model selection.
    The frontend should be able to pass the selected model to the backend.
    """
    response = client.post("/chat", json={"message": "Hello", "llm_name": "test-model"})
    assert response.status_code == 200
    assert "llm:selected test-model" in response.text

@pytest.mark.xfail(reason="Fails because the API does not yet handle selected_data_sources.")
def test_alpinejs_integration_contract_data_source_selection():
    """
    Tests the API contract for Alpine.js integration, for data source selection.
    """
    response = client.post("/chat", json={"message": "Query from my data", "selected_data_sources": ["my_data.csv"]})
    assert response.status_code == 200
    assert "datasource:selected my_data.csv" in response.text

@pytest.mark.xfail(reason="Fails because the API does not yet handle combined selections.")
def test_tool_and_data_source_combination():
    """
    Tests that both tools and data sources can be selected simultaneously
    and are reflected in the response.
    """
    response = client.post("/chat", json={
        "message": "Analyze this data and search for trends",
        "selected_tools": ["analyzer"],
        "selected_data_sources": ["sales_data.csv"]
    })
    assert response.status_code == 200
    assert "tool:selected analyzer" in response.text
    assert "datasource:selected sales_data.csv" in response.text

@pytest.mark.xfail(reason="Fails because tool execution is still present in streaming responses.")
def test_no_tool_execution_on_streaming_response():
    """
    Ensures that even with a tool selected, the response is a single stream
    and no tool execution takes place.
    """
    with client.stream("POST", "/chat", json={"message": "Calculate 5*5", "selected_tools": ["calculator"]}) as response:
        assert response.status_code == 200
        full_response = ""
        for chunk in response.iter_text():
            full_response += chunk
        assert "tool:selected calculator" in full_response
        assert "25" not in full_response

# This test should pass as the API should already be backward compatible.
def test_api_backward_compatibility():
    """
    Tests that the API remains backward compatible for requests that do not
    include the new parameters.
    """
    response = client.post("/chat", json={"message": "Just a simple chat message."})
    assert response.status_code == 200
    assert "tool:selected" not in response.text
    assert "datasource:selected" not in response.text

@pytest.mark.xfail(reason="Fails because the API does not yet handle multiple tool selections.")
def test_multiple_tools_selection():
    """
    Tests that multiple tools can be selected and are acknowledged.
    """
    response = client.post("/chat", json={"message": "...", "selected_tools": ["calculator", "search"]})
    assert response.status_code == 200
    assert "tool:selected calculator" in response.text
    assert "tool:selected search" in response.text

@pytest.mark.xfail(reason="Fails due to lack of a predictable mock response for the default prompt.")
def test_system_prompt_for_no_tool_selection():
    """
    Tests that a default system prompt is used when no tools are selected.
    This requires a way to inspect the prompt or a predictable response.
    """
    response = client.post("/chat", json={"message": "Tell me a joke."})
    assert response.status_code == 200
    # This assertion is a placeholder and likely to fail without a proper mock setup.
    # It's marked as xfail because the exact response is unpredictable.
    assert "Why don't scientists trust atoms?" in response.text
