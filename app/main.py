
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse
from starlette.routing import Mount
from starlette.middleware.base import BaseHTTPMiddleware
from app.middleware.auth import AuthMiddleware
from app.routers import chat, websocket, data, llm_configs
from app.services.llm_client import llm_client
from app.config import settings
import os

SYSTEM_PROMPT_CONTENT = ""

class CSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Set Content Security Policy header
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
            "font-src 'self' data: https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
            "connect-src 'self' ws: wss:; "
            "img-src 'self' data: https:; "
            "object-src 'none'; "
            "base-uri 'self'"
        )
        
        # response.headers["Content-Security-Policy"] = csp_policy
        response.headers["Content-Security-Policy-Report-Only"] = csp_policy
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    global SYSTEM_PROMPT_CONTENT
    print(f"Lifespan starting: system_prompt_override = {settings.system_prompt_override}")
    print(f"Lifespan starting: disable_llm_calls = {settings.disable_llm_calls}")
    
    if settings.system_prompt_override:
        print("Using system_prompt_override")
        SYSTEM_PROMPT_CONTENT = settings.system_prompt_override
    else:
        print("Trying to read system_prompt.md file")
        try:
            with open("system_prompt.md", "r", encoding="utf-8") as f:
                SYSTEM_PROMPT_CONTENT = f.read()
                print(f"Successfully read file, content: {SYSTEM_PROMPT_CONTENT[:50]}...")
        except FileNotFoundError:
            print("File not found, using default")
            SYSTEM_PROMPT_CONTENT = "You are a helpful AI assistant."
    
    print(f"Final SYSTEM_PROMPT_CONTENT: '{SYSTEM_PROMPT_CONTENT}'")

    if not settings.disable_llm_calls:
        try:
            print("Performing LLM health check...")
            messages = [{"role": "user", "content": "hi"}]
            # Temporarily set max_tokens for health check if the LLMClient supported it
            # For now, we'll just make a basic call
            response = llm_client.chat_completion(messages=messages)
            # In a real scenario, you'd check the response for validity
            print("LLM health check successful.")
        except Exception as e:
            print(f"LLM health check failed: {e}")
            # Continue startup even if health check fails (e.g., rate limits)
            print("Continuing startup despite health check failure...")
    else:
        print("LLM health check disabled")
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(CSPMiddleware)
app.add_middleware(AuthMiddleware)
app.include_router(chat.router)
app.include_router(websocket.router)
app.include_router(data.router)
app.include_router(llm_configs.router)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/test-auth")
def test_auth(request: Request):
    return {"user_email": request.state.user_email}

import json

@app.get("/{full_path:path}", response_class=HTMLResponse)
async def serve_frontend():
    with open("static/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Inject dynamic configuration values
    html_content = html_content.replace(
        "appName: \"Chat Data MCP Tools\"",
        f"appName: {json.dumps(settings.app_name)}"
    )
    html_content = html_content.replace(
        "llmConfigFile: \"config/llms.yml\"",
        f"llmConfigFile: {json.dumps(settings.llm_config_file)}"
    )
    return html_content
