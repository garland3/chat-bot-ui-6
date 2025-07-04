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
def create_chat_session(request: Request):
    user_email = request.state.user_email
    session_id = session_manager.create_session(user_email)
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

    llm_name = message.get("llm_name")
    if llm_name:
        try:
            llm_client.set_llm(llm_name)
            log_session_event(session_id, {"event": "llm_changed", "llm_name": llm_name})
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid LLM selection: {e}")

    if settings.disable_llm_calls:
        return {"response": "LLM calls are disabled."}

    user_message = {"role": "user", "content": message.get("content", "")}
    session_messages = session.get("messages", [])
    
    # Add system message to session if this is the first user message
    if not session_messages:
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
    if selected_tool_names:
        # Filter tools to only include selected ones
        all_tools = tool_manager.get_all_tool_definitions()
        available_tools = [tool for tool in all_tools if tool["function"]["name"] in selected_tool_names]
    else:
        # No tools selected, provide all tools to the LLM
        available_tools = tool_manager.get_all_tool_definitions()

    try:
        # First call to LLM to check for tool calls (not streaming initially)
        llm_response = llm_client.chat_completion(messages=messages, tools=available_tools, stream=False)
        response_message = llm_response.json()["choices"][0]["message"]

        # Check if the LLM wants to call a tool
        if response_message.get("tool_calls"):
            tool_calls = response_message["tool_calls"]
            log_session_event(session_id, {"event": "tool_call", "tool_calls": tool_calls})
            messages.append(response_message) # Add assistant's tool call to messages

            for tool_call in tool_calls:
                tool_name = tool_call["function"]["name"]
                tool_args = json.loads(tool_call["function"]["arguments"])

                tool = tool_manager.get_tool(tool_name)
                if tool:
                    tool_output = tool.execute(**tool_args)
                    tool_output_message = {
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": tool_name,
                        "content": json.dumps(tool_output)
                    }
                    messages.append(tool_output_message)
                    log_session_event(session_id, {"event": "tool_output", "output": tool_output_message})
                else:
                    tool_output_message = {
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": tool_name,
                        "content": "Tool not found."
                    }
                    messages.append(tool_output_message)
                    log_session_event(session_id, {"event": "tool_error", "error": tool_output_message})
            
            # Second call to LLM with tool output, this time streaming
            def generate_tool_response():
                full_content = ""
                try:
                    for chunk in llm_client.chat_completion(messages=messages, tools=available_tools, stream=True):
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
                    # Append LLM's response to session messages after streaming is complete
                    if full_content:
                        assistant_response = {"role": "assistant", "content": full_content}
                        session_messages.append(assistant_response)
                        log_session_event(session_id, {"event": "assistant_response", "response": assistant_response})
                        session_manager.update_session_messages(session_id, session_messages)
            return StreamingResponse(generate_tool_response(), media_type="text/event-stream")
        else:
            # If not a tool call, use the response content from the first call and stream additional content if needed
            initial_content = response_message.get("content", "")
            
            def generate_response():
                full_content = initial_content
                # First yield the initial content
                if initial_content:
                    yield initial_content
                
                # Then stream additional content if the LLM has more to say
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
                    # Append LLM's response to session messages after streaming is complete
                    if full_content:
                        assistant_response = {"role": "assistant", "content": full_content}
                        session_messages.append(assistant_response)
                        log_session_event(session_id, {"event": "assistant_response", "response": assistant_response})
                        session_manager.update_session_messages(session_id, session_messages)
            return StreamingResponse(generate_response(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")
