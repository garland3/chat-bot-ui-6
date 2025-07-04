
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
                session_id = data.get('session_id')
                if session_id:
                    session_manager.register_websocket(session_id, websocket)
                    await websocket.send_json({"type": "session_id", "session_id": session_id})
                    print(f"WebSocket registered for session: {session_id}")
                else:
                    print("Received session_init without session_id")
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
