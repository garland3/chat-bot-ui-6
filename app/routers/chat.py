import json
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from app.services.session_manager import session_manager
from app.services.llm_client import llm_client
from app.services.tool_manager import tool_manager
from app.config import settings

router = APIRouter()

@router.post("/chat")
def create_chat_session(request: Request):
    user_email = request.state.user_email
    session_id = session_manager.create_session(user_email)
    return {"session_id": session_id}

@router.post("/chat/{session_id}/message")
async def chat_message(session_id: str, request: Request, message: dict):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if settings.disable_llm_calls:
        return {"response": "LLM calls are disabled."}

    session_messages = session.get("messages", [])
    session_messages.append({"role": "user", "content": message.get("content", "")})

    messages = list(session_messages) # Create a copy to send to LLM

    # Add a system message to guide the LLM
    system_message = {"role": "system", "content": "You are a helpful AI assistant with access to various tools. Use the available tools to answer questions or perform tasks. If a user asks a question that can be answered by a tool, use the tool. If you cannot answer a question with a tool, respond normally."}
    messages.insert(0, system_message)
    
    # Get selected tools from the request, or use all tools if none specified
    selected_tool_names = message.get("tools", [])
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
            messages.append(response_message) # Add assistant's tool call to messages

            for tool_call in tool_calls:
                tool_name = tool_call["function"]["name"]
                tool_args = json.loads(tool_call["function"]["arguments"])

                tool = tool_manager.get_tool(tool_name)
                if tool:
                    tool_output = tool.execute(**tool_args)
                    messages.append({
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": tool_name,
                        "content": json.dumps(tool_output)
                    })
                else:
                    messages.append({
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": tool_name,
                        "content": "Tool not found."
                    })
            
            # Second call to LLM with tool output, this time streaming
            def generate_tool_response():
                full_content = ""
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
                # Append LLM's response to session messages after streaming is complete
                session_messages.append({"role": "assistant", "content": full_content})
                session_manager.update_session_messages(session_id, session_messages)
            return StreamingResponse(generate_tool_response(), media_type="text/event-stream")
        else:
            # If not a tool call, stream the response directly
            def generate_llm_response():
                full_content = ""
                # Make a streaming call directly instead of using the non-streaming response
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
                # Append LLM's response to session messages after streaming is complete
                session_messages.append({"role": "assistant", "content": full_content})
                session_manager.update_session_messages(session_id, session_messages)
            return StreamingResponse(generate_llm_response(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")
