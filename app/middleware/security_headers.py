# app/middleware/security_headers.py
# ПР6: Артем — Middleware для захисних HTTP-заголовків

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Забороняє завантаження ресурсів з інших доменів
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "frame-ancestors 'none'"
        )
        # Захист від Clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        # Забороняє браузеру визначати тип контенту самостійно
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Контролює дані у заголовку Referer
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # Вмикає XSS-фільтр браузера
        response.headers["X-XSS-Protection"] = "1; mode=block"

        return response
