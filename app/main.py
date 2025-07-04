
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse
from starlette.routing import Mount
from starlette.middleware.base import BaseHTTPMiddleware
from app.middleware.auth import AuthMiddleware
from app.routers import chat, websocket, data
from app.services.llm_client import llm_client
from app.config import settings

class CSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Set Content Security Policy header
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdnjs.cloudflare.com; "
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
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(CSPMiddleware)
app.add_middleware(AuthMiddleware)
app.include_router(chat.router)
app.include_router(websocket.router)
app.include_router(data.router)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/test-auth")
def test_auth(request: Request):
    return {"user_email": request.state.user_email}

@app.get("/{full_path:path}", response_class=HTMLResponse)
async def serve_frontend():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()
