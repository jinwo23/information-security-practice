from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime

from app.database import Base


# Артем: реалізація моделі користувача для бази даних.
# У цьому файлі описується таблиця users через SQLAlchemy.
# Модель User використовується для збереження логіна, email,
# хешованого пароля, ПІБ, статусу активності та дати створення.
# Ця структура потрібна для реєстрації, логіну та роботи JWT-автентифікації.


class User(Base):
    tablename = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True, index=True, nullable=False)

    email = Column(String, unique=True, index=True, nullable=False)

    password_hash = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)

    full_name = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
