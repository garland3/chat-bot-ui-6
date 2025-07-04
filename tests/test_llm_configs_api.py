from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_llm_configs():
    response = client.get("/api/llm_configs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    # Check for expected keys in at least one LLM config
    first_llm = response.json()[0]
    assert "name" in first_llm
    assert "provider" in first_llm
    assert "base_url" in first_llm
    assert "model_name" in first_llm