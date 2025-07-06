
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.session_manager import session_manager
import json

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = None
    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)

            if data.get('type') == 'session_init':
                requested_session_id = data.get('session_id')
                if requested_session_id:
                    session_id = requested_session_id
                    session_manager.register_websocket(session_id, websocket)
                    print(f"WebSocket re-registered for session: {session_id}")
                else:
                    # Create a new session if no session_id is provided
                    user_email = "websocket_user" # Default user for websocket initiated sessions
                    session_id = session_manager.create_session(user_email)
                    session_manager.register_websocket(session_id, websocket)
                    print(f"New session created and WebSocket registered: {session_id}")
                
                await websocket.send_json({"type": "session_id", "session_id": session_id})
            else:
                # Handle other messages as before, or pass to session manager
                if session_id:
                    # Example: echo message back if session is known
                    await websocket.send_text(f"Message for session {session_id}: {message}")
                else:
                    await websocket.send_text(f"Message received before session init: {message}")

    except WebSocketDisconnect:
        if session_id:
            session_manager.unregister_websocket(session_id)
            print(f"WebSocket disconnected for session: {session_id}")
        else:
            print("WebSocket disconnected before session init")
    except Exception as e:
        print(f"WebSocket error: {e}")
        if session_id:
            session_manager.unregister_websocket(session_id)
