# app/audit/logger.py
# Артем: центральний модуль запису подій — і в БД, і в stdout для Docker/SIEM

import json
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.audit.models import AuditLog

# Антон: JSON-форматер — кожен рядок логу є валідним JSON
# Це дозволяє SIEM-системам парсити логи автоматично
logger = logging.getLogger("security_audit")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    '{"timestamp":"%(asctime)s","level":"%(levelname)s","message":%(message)s}'
))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def log_event(
    db: Session,
    action: str,
    status: str,
    ip_address: str,
    user_id=None,
    username=None,
    http_method=None,
    endpoint=None,
    status_code=None,
    resource=None,
    details=None,
):
    """
    Богдан: універсальна функція запису події.
    Записує одночасно у БД та у stdout (docker logs).
    """

    # 1. Запис у БД
    # Влад: details серіалізуємо у JSON-рядок
    log_entry = AuditLog(
        user_id=user_id,
        username=username,
        ip_address=ip_address,
        action=action,
        status=status,
        http_method=http_method,
        endpoint=endpoint,
        status_code=status_code,
        resource=resource,
        details=json.dumps(details, ensure_ascii=False) if details else None,
    )
    db.add(log_entry)
    db.commit()

    # 2. Вивід у stdout у JSON-форматі
    # Антон: failure/warning → WARNING рівень для SIEM фільтрації
    log_data = {
        "event_type": action,
        "status": status,
        "user_id": user_id,
        "username": username,
        "ip_address": ip_address,
        "endpoint": endpoint,
        "details": details,
    }
    level = logging.WARNING if status in ("failure", "warning") else logging.INFO
    logger.log(level, json.dumps(log_data, ensure_ascii=False))


# ── Хелпери для типових подій ─────────────────────────────────────────────────

def log_login_success(db: Session, user_id: int, username: str, ip: str):
    """Артем: логуємо успішний вхід."""
    log_event(
        db=db, action="login_success", status="success",
        ip_address=ip, user_id=user_id, username=username,
        http_method="POST", endpoint="/auth/login", status_code=200,
    )


def log_login_failed(db: Session, username: str, ip: str, reason: str = "invalid_credentials"):
    """Богдан: кожна невдала спроба — потенційний початок Brute Force."""
    log_event(
        db=db, action="login_failed", status="failure",
        ip_address=ip, username=username,
        http_method="POST", endpoint="/auth/login",
        status_code=401, details={"reason": reason},
    )


def log_access_denied(db: Session, user_id: int, username: str, ip: str, endpoint: str, method: str):
    """Влад: 403 — спроба доступу до забороненого ресурсу."""
    log_event(
        db=db, action="access_denied", status="failure",
        ip_address=ip, user_id=user_id, username=username,
        http_method=method, endpoint=endpoint, status_code=403,
    )


def log_grade_update(db: Session, user_id: int, username: str, ip: str,
                     grade_id: int, old_value, new_value):
    """Антон: зміна оцінки — зберігаємо old → new для розслідування."""
    log_event(
        db=db, action="grade_update", status="success",
        ip_address=ip, user_id=user_id, username=username,
        http_method="PUT", endpoint=f"/api/grades/{grade_id}",
        status_code=200, resource=f"grade:{grade_id}",
        details={"grade_id": grade_id, "old_value": old_value, "new_value": new_value},
    )