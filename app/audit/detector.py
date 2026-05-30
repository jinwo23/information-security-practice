# app/audit/detector.py
# Артем: модуль детектування аномалій — автоматичний захист від атак

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.audit.models import AuditLog
from app.audit.logger import log_event


def check_brute_force(
    db: Session,
    ip_address: str,
    threshold: int = 5,
    window_minutes: int = 5,
) -> bool:
    """
    Богдан: перевіряє чи є 5+ невдалих входів з однієї IP за 5 хвилин.
    Повертає True якщо поріг перевищено — тоді login повертає 429.
    """
    since = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)

    failed_count = (
        db.query(func.count(AuditLog.id))
        .filter(
            AuditLog.action == "login_failed",
            AuditLog.ip_address == ip_address,
            AuditLog.timestamp >= since,
        )
        .scalar()
    )

    if failed_count >= threshold:
        # Влад: фіксуємо сам факт виявлення атаки окремим записом у лозі
        log_event(
            db=db,
            action="brute_force_detected",
            status="warning",
            ip_address=ip_address,
            details={
                "failed_attempts": failed_count,
                "window_minutes": window_minutes,
                "threshold": threshold,
            },
        )
        return True

    return False


def check_off_hours_access(
    db: Session,
    user_id: int,
    username: str,
    ip: str,
    hour: int,
) -> bool:
    """
    Антон: вхід між 00:00 і 06:00 — підозріла активність для деканату.
    НЕ блокує — тільки позначає у лозі як warning.
    """
    if 0 <= hour < 6:
        log_event(
            db=db,
            action="off_hours_login",
            status="warning",
            ip_address=ip,
            user_id=user_id,
            username=username,
            details={"login_hour": hour, "note": "Підозрілий нічний вхід"},
        )
        return True

    return False


def get_security_stats(db: Session, hours: int = 24) -> dict:
    """
    Богдан: зведена статистика безпеки — KPI для адміністратора.
    Відповідає метрикам MTTD/MTTR з лекції 10.
    """
    since = datetime.now(timezone.utc) - timedelta(hours=hours)

    def count_action(action_name: str) -> int:
        # Артем: хелпер щоб не повторювати однотипні запити
        return (
            db.query(func.count(AuditLog.id))
            .filter(AuditLog.action == action_name, AuditLog.timestamp >= since)
            .scalar()
        )

    total = (
        db.query(func.count(AuditLog.id))
        .filter(AuditLog.timestamp >= since)
        .scalar()
    )

    return {
        "period_hours": hours,
        "total_events": total,
        "failed_logins": count_action("login_failed"),
        "successful_logins": count_action("login_success"),
        "access_denied": count_action("access_denied"),
        "brute_force_alerts": count_action("brute_force_detected"),
        "grade_changes": count_action("grade_update"),
        "off_hours_logins": count_action("off_hours_login"),
    }