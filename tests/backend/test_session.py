from fastapi.testclient import TestClient
from app.main import app
from app.services.session_manager import session_manager

client = TestClient(app)

def test_create_chat_session():
    response = client.post("/chat", headers={"X-EMAIL-USER": "test@example.com"})
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    assert session_id is not None
    session = session_manager.get_session(session_id)
    assert session is not None
    assert session["user_email"] == "test@example.com"

def test_rate_limiting():
    user_email = "rate_limit_test@example.com"
    # First session
    response1 = client.post("/chat", headers={"X-EMAIL-USER": user_email})
    assert response1.status_code == 200
    session_id1 = response1.json()["session_id"]

    # Second session should return the same session ID
    response2 = client.post("/chat", headers={"X-EMAIL-USER": user_email})
    assert response2.status_code == 200
    session_id2 = response2.json()["session_id"]
    assert session_id1 == session_id2

    # Clean up the session
    session_manager.delete_session(session_id1)
    assert session_manager.get_session(session_id1) is None

def test_update_session_tools():
    user_email = "tool_update_test@example.com"
    session_id = session_manager.create_session(user_email)
    
    tools_to_add = ["BasicMathTool", "UserLookupTool"]
    session_manager.update_session_tools(session_id, tools_to_add)
    
    session = session_manager.get_session(session_id)
    assert session is not None
    assert "selected_tools" in session
    assert session["selected_tools"] == tools_to_add

    # Test updating with an empty list
    session_manager.update_session_tools(session_id, [])
    session = session_manager.get_session(session_id)
    assert session["selected_tools"] == []

    # Clean up the session
    session_manager.delete_session(session_id)
    assert session_manager.get_session(session_id) is None