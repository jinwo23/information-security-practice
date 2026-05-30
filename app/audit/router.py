# app/audit/router.py
# Богдан: адмін-ендпоінти для перегляду та аналізу журналу аудиту

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.database import get_db
from app.auth.dependencies import require_role
from app.audit.models import AuditLog
from app.audit.detector import get_security_stats

router = APIRouter()


@router.get("/audit-log")
async def get_audit_log(
    # Влад: усі параметри — Query для зручного тестування через curl
    action: Optional[str] = Query(None, description="Тип події (login_failed, grade_update...)"),
    username: Optional[str] = Query(None, description="Ім'я користувача"),
    status: Optional[str] = Query(None, description="success / failure / warning"),
    ip_address: Optional[str] = Query(None, description="IP-адреса клієнта"),
    hours: int = Query(24, ge=1, le=720, description="Глибина пошуку в годинах"),
    limit: int = Query(50, ge=1, le=200, description="Записів на сторінку"),
    offset: int = Query(0, ge=0, description="Зміщення для пагінації"),
    db: Session = Depends(get_db),
    # Антон: тільки адміністратори мають право переглядати логи
    current_user=Depends(require_role("admin")),
):
    """
    Артем: повертає журнал аудиту з фільтрацією та пагінацією.

    Приклади:
    GET /admin/audit-log?action=login_failed&hours=1
    GET /admin/audit-log?status=warning&limit=20
    GET /admin/audit-log?ip_address=192.168.1.100
    """
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    query = db.query(AuditLog).filter(AuditLog.timestamp >= since)

    # Богдан: динамічно додаємо фільтри — тільки якщо передані
    if action:
        query = query.filter(AuditLog.action == action)
    if username:
        query = query.filter(AuditLog.username == username)
    if status:
        query = query.filter(AuditLog.status == status)
    if ip_address:
        query = query.filter(AuditLog.ip_address == ip_address)

    total = query.count()

    # Влад: сортування DESC — свіжіші події першими
    logs = (
        query.order_by(AuditLog.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "logs": [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "action": log.action,
                "status": log.status,
                "user_id": log.user_id,
                "username": log.username,
                "ip_address": log.ip_address,
                "http_method": log.http_method,
                "endpoint": log.endpoint,
                "status_code": log.status_code,
                "resource": log.resource,
                "details": log.details,
            }
            for log in logs
        ],
    }


@router.get("/security-stats")
async def security_statistics(
    hours: int = Query(24, ge=1, le=720, description="Період аналізу в годинах"),
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin")),
):
    """
    Антон: зведена статистика безпеки за вказаний період.

    GET /admin/security-stats?hours=1   → за останню годину
    GET /admin/security-stats?hours=168 → за тиждень
    """
    return get_security_stats(db, hours)


@router.get("/suspicious-ips")
async def get_suspicious_ips(
    hours: int = Query(1, ge=1, le=24),
    threshold: int = Query(5, ge=1, description="Мінімум невдалих спроб"),
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin")),
):
    """
    Богдан: список підозрілих IP — тих що мають 5+ невдалих входів.
    Корисно для ручного блокування або аналізу атак.
    """
    from sqlalchemy import func as sa_func

    since = datetime.now(timezone.utc) - timedelta(hours=hours)

    # Артем: GROUP BY ip + COUNT — знаходимо IP з найбільшою кількістю промахів
    results = (
        db.query(
            AuditLog.ip_address,
            sa_func.count(AuditLog.id).label("failed_count"),
        )
        .filter(
            AuditLog.action == "login_failed",
            AuditLog.timestamp >= since,
        )
        .group_by(AuditLog.ip_address)
        .having(sa_func.count(AuditLog.id) >= threshold)
        .order_by(sa_func.count(AuditLog.id).desc())
        .all()
    )

    return {
        "period_hours": hours,
        "threshold": threshold,
        "suspicious_ips": [
            {"ip_address": row.ip_address, "failed_attempts": row.failed_count}
            for row in results
        ],
    }