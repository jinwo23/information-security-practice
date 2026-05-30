# app/audit/models.py
# Антон: модель таблиці аудиту — серце всієї системи журналювання

from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from datetime import datetime, timezone
from app.database import Base


class AuditLog(Base):
    """
    Богдан: кожен запис відповідає правилу 5W —
    хто, що, коли, де і чому (результат дії).
    """
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)

    # WHO — хто виконав дію
    # Артем: user_id може бути None для анонімних запитів
    user_id = Column(Integer, nullable=True)
    username = Column(String(50), nullable=True)
    ip_address = Column(String(45), nullable=False)

    # WHAT — що сталося
    # Влад: action — короткий ідентифікатор події
    action = Column(String(50), nullable=False)
    resource = Column(String(100), nullable=True)

    # WHEN — коли (завжди UTC)
    # Антон: index=True важливий — більшість запитів фільтрують по часу
    timestamp = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    # WHERE — який HTTP-ендпоінт
    # Богдан: метод і шлях окремо для зручної фільтрації
    http_method = Column(String(10), nullable=True)
    endpoint = Column(String(200), nullable=True)

    # WHY — результат
    # Артем: status_code=403 одразу сигналізує про несанкціонований доступ
    status_code = Column(Integer, nullable=True)
    status = Column(String(20), nullable=False)
    details = Column(Text, nullable=True)

    # Влад: складені індекси — без них при 1М+ записів запити будуть повільними
    __table_args__ = (
        Index("ix_audit_action_ts", "action", "timestamp"),
        Index("ix_audit_user_ts", "user_id", "timestamp"),
        Index("ix_audit_ip_action", "ip_address", "action"),
    )