# app/audit/middleware.py
# Влад: middleware — автоматичне логування КОЖНОГО HTTP-запиту без змін у роутерах

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.database import SessionLocal
from app.audit.models import AuditLog

# Антон: ці шляхи пропускаємо — не засмічуємо лог технічними перевірками
SKIP_PATHS = {"/health", "/docs", "/openapi.json", "/redoc", "/favicon.ico"}


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Богдан: middleware перехоплює кожен запит ПІСЛЯ його виконання.
    Логуємо реальний статус-код відповіді — це чесніше ніж логувати до виконання.

    Важливо: middleware НЕ має доступу до user_id з JWT —
    токен розшифровується пізніше у залежностях FastAPI.
    User_id логується окремо у самих ендпоінтах.
    """

    async def dispatch(self, request: Request, call_next):
        # Артем: пропускаємо технічні ендпоінти без логування
        if request.url.path in SKIP_PATHS:
            return await call_next(request)

        ip = request.client.host if request.client else "unknown"
        start_time = time.time()

        # Виконуємо оригінальний запит
        response = await call_next(request)

        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        # Влад: окрема сесія БД — не перетинаємось з сесією ендпоінта
        db = SessionLocal()
        try:
            status_code = response.status_code

            # Антон: визначаємо статус за HTTP-кодом відповіді
            if status_code < 400:
                status = "success"
            elif status_code == 403:
                status = "failure"
            elif status_code == 429:
                status = "warning"
            else:
                status = "failure"

            log_entry = AuditLog(
                ip_address=ip,
                action="http_request",
                http_method=request.method,
                endpoint=request.url.path,
                status_code=status_code,
                status=status,
                # Богдан: зберігаємо час відповіді — корисно для виявлення аномалій
                details=f'{{"elapsed_ms": {elapsed_ms}}}',
            )
            db.add(log_entry)
            db.commit()
        except Exception:
            # Артем: помилка логування НЕ повинна ламати основний запит
            db.rollback()
        finally:
            db.close()

        return response