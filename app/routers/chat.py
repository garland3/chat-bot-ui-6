import json
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from app.services.session_manager import session_manager
from app.utils.session_logger import log_session_event
from app.services.llm_client import llm_client
from app.services.system_prompt_engine import system_prompt_engine
from app.config import settings
from datetime import datetime
import os
from typing import List, Optional

router = APIRouter()

# LLMs endpoint moved to llm_configs.py

@router.post("/chat")
async def create_chat_session(request: Request):
    user_email = request.state.user_email
    session_id = session_manager.create_session(user_email)
    # Send session_id to the client via WebSocket
    await session_manager.send_websocket_message(session_id, {"type": "session_id", "session_id": session_id})
    return {"session_id": session_id}

@router.get("/chat/{session_id}/download")
async def download_chat_session(session_id: str):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    chat_history = session.get("messages", [])
    selected_tools = session.get("selected_tools", [])
    selected_data_sources = session.get("selected_data_sources", [])

    # Format the chat history
    formatted_content = f"Chat Session ID: {session_id}\n"
    formatted_content += f"Timestamp: {datetime.now().isoformat()}\n"
    formatted_content += f"Selected LLM: {llm_client.current_llm_name}\n"
    formatted_content += f"Selected Tools: {', '.join(selected_tools) if selected_tools else 'None'}\n"
    formatted_content += f"Selected Data Sources: {', '.join(selected_data_sources) if selected_data_sources else 'None'}\n\n"

    for msg in chat_history:
        role = msg.get("role", "unknown").capitalize()
        content = msg.get("content", "")
        formatted_content += f"{role}: {content}\n\n"

    # Create a temporary file to store the content
    file_name = f"chat_session_{session_id}.txt"
    file_path = os.path.join("logs", file_name)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(formatted_content)

    return FileResponse(path=file_path, filename=file_name, media_type="text/plain")

@router.post("/chat/{session_id}/message")
async def chat_message(session_id: str, request: Request, message: dict):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Extract parameters - supporting both old and new API formats
    selected_tools = message.get("selected_tools", message.get("tools", []))
    selected_data_sources = message.get("selected_data_sources", message.get("data_sources", []))
    llm_name = message.get("llm_name")
    user_content = message.get("content", "")

    # Validate parameters
    if not isinstance(selected_tools, list):
        raise HTTPException(status_code=400, detail="selected_tools must be a list")
    if not isinstance(selected_data_sources, list):
        raise HTTPException(status_code=400, detail="selected_data_sources must be a list")

    # Store selections in session
    session_manager.update_session_tools(session_id, selected_tools)
    session_manager.update_session_data_sources(session_id, selected_data_sources)
    
    # Handle LLM selection
    if llm_name:
        try:
            llm_client.set_llm(llm_name)
            log_session_event(session_id, {"event": "llm_changed", "llm_name": llm_name})
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid LLM selection: {e}")

    # Log parameter updates
    log_session_event(session_id, {
        "event": "parameters_updated", 
        "selected_tools": selected_tools, 
        "selected_data_sources": selected_data_sources, 
        "llm_name": llm_name
    })

    # Handle disabled LLM calls
    if settings.disable_llm_calls:
        return JSONResponse({"response": "LLM calls are disabled."})

    # Prepare messages
    user_message = {"role": "user", "content": user_content}
    session_messages = session.get("messages", [])
    
    # Generate dynamic system prompt for this conversation
    system_prompt = system_prompt_engine.generate_system_prompt(
        selected_tools=selected_tools,
        selected_data_sources=selected_data_sources
    )
    
    # Log system prompt for debugging
    log_session_event(session_id, {
        "event": "system_prompt_generated",
        "system_prompt": system_prompt,
        "selected_tools": selected_tools,
        "selected_data_sources": selected_data_sources
    })
    
    # Add system message if this is the first user message or update existing one
    if not session_messages:
        system_message = {"role": "system", "content": system_prompt}
        session_messages.append(system_message)
    else:
        # Update system message to reflect current selections
        for msg in session_messages:
            if msg["role"] == "system":
                msg["content"] = system_prompt
                break
    
    # Add user message
    session_messages.append(user_message)
    log_session_event(session_id, {"event": "user_message", "message": user_message})

    # Prepare messages for LLM (copy for thread safety)
    llm_messages = list(session_messages)

    def generate_response():
        """Generator for streaming response with tool selection feedback."""
        # Stream tool selection feedback
        for tool_name in selected_tools:
            log_session_event(session_id, {"event": "tool_selected", "tool_name": tool_name})
            yield f"data: {json.dumps({'type': 'tool_selected', 'tool': tool_name})}\n\n"

        # Stream data source selection feedback  
        for data_source in selected_data_sources:
            log_session_event(session_id, {"event": "data_source_selected", "data_source": data_source})
            yield f"data: {json.dumps({'type': 'data_source_selected', 'data_source': data_source})}\n\n"

        # Single streaming LLM call
        full_content = ""
        try:
            for chunk in llm_client.chat_completion(messages=llm_messages, stream=True):
                if chunk.startswith(b'data:'):
                    chunk = chunk[len(b'data:'):].strip()
                if chunk == b'[DONE]':
                    break
                if chunk:
                    try:
                        data = json.loads(chunk)
                        content = data["choices"][0]["delta"].get("content", "")
                        if content:
                            full_content += content
                            yield f"data: {json.dumps({'content': content})}\n\n"
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            error_msg = f"Error during streaming: {str(e)}"
            log_session_event(session_id, {"event": "streaming_error", "error": error_msg})
            yield f"data: {json.dumps({'error': error_msg})}\n\n"
        finally:
            # Store assistant response
            if full_content:
                assistant_response = {"role": "assistant", "content": full_content}
                session_messages.append(assistant_response)
                log_session_event(session_id, {"event": "assistant_response", "response": assistant_response})
                session_manager.update_session_messages(session_id, session_messages)
            
            # Signal completion
            yield f"data: [DONE]\n\n"

    return StreamingResponse(generate_response(), media_type="text/event-stream")