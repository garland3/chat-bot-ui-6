
import uuid
from typing import Dict, Any, Optional

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.user_sessions: Dict[str, str] = {}  # Maps user_email to session_id

    def create_session(self, user_email: str) -> str:
        # Check if user already has an active session
        if user_email in self.user_sessions:
            return self.user_sessions[user_email]

        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {"user_email": user_email}
        self.user_sessions[user_email] = session_id
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self.sessions.get(session_id)

    def delete_session(self, session_id: str):
        if session_id in self.sessions:
            user_email = self.sessions[session_id]["user_email"]
            del self.sessions[session_id]
            if user_email in self.user_sessions and self.user_sessions[user_email] == session_id:
                del self.user_sessions[user_email]

session_manager = SessionManager()
