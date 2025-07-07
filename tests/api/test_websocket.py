
from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)

def test_websocket_connection():
    with client.websocket_connect("/ws") as websocket:
        # Simulate session creation and sending session_init message
        session_id = "test_session_id"
        websocket.send_json({"type": "session_init", "session_id": session_id})
        
        # Expect to receive session_id back
        data = websocket.receive_json()
        assert data == {"type": "session_id", "session_id": session_id}

        # Test sending a regular message
        test_message = {"type": "chat_message", "content": "Hello, world!"}
        websocket.send_json(test_message)
        received_message = websocket.receive_text()
        # The server echoes the message as a string, so we need to parse it back to JSON
        expected_echo = f"Message for session {session_id}: {json.dumps(test_message, separators=(',', ':'))}"
        assert received_message == expected_echo
