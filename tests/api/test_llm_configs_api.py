from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_llm_configs():
    response = client.get("/api/llm_configs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    # Check for expected keys in at least one LLM config (public format)
    first_llm = response.json()[0]
    assert "name" in first_llm
    assert "provider" in first_llm
    assert "model" in first_llm  # Updated from model_name
    assert "description" in first_llm
    # base_url is not exposed in public API for security