
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse
from starlette.routing import Mount
from app.middleware.auth import AuthMiddleware
from app.routers import chat, websocket, data
from app.services.llm_client import llm_client
from app.config import settings

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
            # Depending on criticality, you might want to raise an exception here
    yield

app = FastAPI(lifespan=lifespan)

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
    with open("static/index.html", "r") as f:
        return f.read()
