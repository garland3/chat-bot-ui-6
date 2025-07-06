import json
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from app.services.session_manager import session_manager
from app.utils.session_logger import log_session_event
from app.services.llm_client import llm_client
from app.services.tool_manager import tool_manager
from app.config import settings
import app.main
import os
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from datetime import datetime

router = APIRouter()

@router.get("/llms")
async def get_llms():
    return llm_client.get_available_llms()

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

    # Format the chat history
    formatted_content = f"Chat Session ID: {session_id}\n"
    formatted_content += f"Timestamp: {datetime.now().isoformat()}\n"
    formatted_content += f"Selected LLM: {llm_client.current_llm_name}\n"
    formatted_content += f"Selected Tools: {', '.join(selected_tools) if selected_tools else 'None'}\n\n"

    for msg in chat_history:
        role = msg.get("role", "unknown").capitalize()
        content = msg.get("content", "")
        formatted_content += f"{role}: {content}\n\n"

    # Create a temporary file to store the content
    file_name = f"chat_session_{session_id}.txt"
    file_path = os.path.join("logs", file_name) # Using logs directory for temporary storage

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(formatted_content)

    return FileResponse(path=file_path, filename=file_name, media_type="text/plain")

@router.post("/chat/{session_id}/message")
async def chat_message(session_id: str, request: Request, message: dict):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Extract new parameters
    selected_tool_names = message.get("selected_tools", [])
    selected_data_sources = message.get("selected_data_sources", [])
    llm_name = message.get("llm_name")

    # Store in session
    session_manager.update_session_tools(session_id, selected_tool_names)
    session_manager.update_session_data_sources(session_id, selected_data_sources)
    if llm_name:
        try:
            llm_client.set_llm(llm_name)
            log_session_event(session_id, {"event": "llm_changed", "llm_name": llm_name})
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid LLM selection: {e}")

    # Log the selections
    log_session_event(session_id, {"event": "parameters_updated", "selected_tools": selected_tool_names, "selected_data_sources": selected_data_sources, "llm_name": llm_name})


    if settings.disable_llm_calls:
        return {"response": "LLM calls are disabled."}

    user_message = {"role": "user", "content": message.get("content", "")}
    session_messages = session.get("messages", [])
    
    # Add system message to session if this is the first user message
    if not session_messages:
        system_prompt_content = settings.system_prompt_override
        if not system_prompt_content:
            try:
                with open("system_prompt.md", "r", encoding="utf-8") as f:
                    system_prompt_content = f.read()
            except FileNotFoundError:
                system_prompt_content = "You are a helpful AI assistant."
        
        if selected_data_sources:
            system_prompt_content += "\n\nThe user has access to the following data sources: " + ", ".join(selected_data_sources)

        if 'calculator' in selected_tool_names:
            system_prompt_content += "\n\nYou have access to a calculator and should use it for any mathematical calculations. Frame your thinking process in calculations."

        system_message = {"role": "system", "content": system_prompt_content}
        session_messages.append(system_message)

    
    session_messages.append(user_message)
    log_session_event(session_id, {"event": "user_message", "message": user_message})

    messages = list(session_messages) # Create a copy to send to LLM

    # Add a system message to guide the LLM if not already present
    if not messages or messages[0]["role"] != "system":
        system_prompt_content = settings.system_prompt_override
        if not system_prompt_content:
            system_prompt_content = app.main.SYSTEM_PROMPT_CONTENT
        if not system_prompt_content:
            # Fallback if global isn't set (e.g., in tests)
            try:
                with open("system_prompt.md", "r", encoding="utf-8") as f:
                    system_prompt_content = f.read()
            except FileNotFoundError:
                system_prompt_content = "You are a helpful AI assistant."
        system_message = {"role": "system", "content": system_prompt_content}
        messages.insert(0, system_message)
    
    # Get selected tools from the request, or use all tools if none specified
    selected_tool_names = message.get("tools", [])
    session_manager.update_session_tools(session_id, selected_tool_names)

    selected_data_sources = message.get("data_sources", [])
    session_manager.update_session_data_sources(session_id, selected_data_sources)
    # System prompt modification based on tool selection
    system_message = next((m for m in messages if m['role'] == 'system'), None)
    if system_message:
        if 'calculator' in selected_tool_names:
            system_message['content'] += "\n\nYou have access to a calculator and should use it for any mathematical calculations. Frame your thinking process in calculations."

    
    def generate_response():
        # Log and stream tool selection
        for tool_name in selected_tool_names:
            log_session_event(session_id, {"event": "tool_selected", "tool_name": tool_name})
            yield f"tool:selected {tool_name}\n"

        
        full_content = ""
        try:
            for chunk in llm_client.chat_completion(messages=messages, stream=True):
                if chunk.startswith(b'data:'):
                    chunk = chunk[len(b'data:'):].strip()
                if chunk == b'[DONE]':
                    break
                if chunk:
                    try:
                        data = json.loads(chunk)
                        content = data["choices"][0]["delta"].get("content", "")
                        full_content += content
                        yield content
                    except json.JSONDecodeError:
                        continue
        finally:
            if full_content:
                assistant_response = {"role": "assistant", "content": full_content}
                session_messages.append(assistant_response)
                log_session_event(session_id, {"event": "assistant_response", "response": assistant_response})
                session_manager.update_session_messages(session_id, session_messages)

    return StreamingResponse(generate_response(), media_type="text/event-stream")
