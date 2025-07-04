
import uuid
from typing import Dict, Any, Optional
from fastapi import WebSocket
from app.utils.session_logger import log_session_event

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.user_sessions: Dict[str, str] = {}  # Maps user_email to session_id
        self.active_websockets: Dict[str, WebSocket] = {}

    def create_session(self, user_email: str) -> str:
        # Check if user already has an active session
        if user_email in self.user_sessions:
            session_id = self.user_sessions[user_email]
            log_session_event(session_id, {"event": "session_reconnected", "user_email": user_email})
            return session_id

        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {"user_email": user_email, "messages": [], "selected_tools": []}
        self.user_sessions[user_email] = session_id
        log_session_event(session_id, {"event": "session_created", "user_email": user_email})
        return session_id

    def update_session_tools(self, session_id: str, tools: list):
        if session_id in self.sessions:
            self.sessions[session_id]["selected_tools"] = tools
            log_session_event(session_id, {"event": "tools_updated", "tools": tools})

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self.sessions.get(session_id)

    def update_session_messages(self, session_id: str, messages: list):
        if session_id in self.sessions:
            self.sessions[session_id]["messages"] = messages
            if messages:
                log_session_event(session_id, {"event": "message_added", "message": messages[-1]})

    def delete_session(self, session_id: str):
        if session_id in self.sessions:
            user_email = self.sessions[session_id]["user_email"]
            log_session_event(session_id, {"event": "session_deleted", "user_email": user_email})
            del self.sessions[session_id]
            if user_email in self.user_sessions and self.user_sessions[user_email] == session_id:
                del self.user_sessions[user_email]

    def register_websocket(self, session_id: str, websocket: WebSocket):
        self.active_websockets[session_id] = websocket

    def unregister_websocket(self, session_id: str):
        if session_id in self.active_websockets:
            del self.active_websockets[session_id]

    async def send_websocket_message(self, session_id: str, message: Dict[str, Any]):
        if session_id in self.active_websockets:
            websocket = self.active_websockets[session_id]
            try:
                await websocket.send_json(message)
            except Exception as e:
                print(f"Error sending WebSocket message to {session_id}: {e}")
                self.unregister_websocket(session_id)

session_manager = SessionManager()
