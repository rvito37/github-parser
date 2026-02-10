from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings


class RapidAPIMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if not settings.rapidapi_proxy_secret:
            return await call_next(request)

        proxy_secret = request.headers.get("X-RapidAPI-Proxy-Secret", "")
        if proxy_secret != settings.rapidapi_proxy_secret:
            return Response(content="Unauthorized", status_code=403)

        return await call_next(request)
