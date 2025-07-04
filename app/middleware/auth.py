from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.config import settings

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
             return await call_next(request)

        user_email = request.headers.get("X-EMAIL-USER")
        if user_email:
            request.state.user_email = user_email
        elif settings.test_mode:
            request.state.user_email = settings.test_email
        else:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

        response = await call_next(request)
        return response