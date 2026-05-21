from datetime import datetime 
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database import Base


# =========================
# Зв’язкові таблиці
# =========================

# Таблиця для зв’язку користувачів і ролей (many-to-many)
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),  # ID користувача
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),  # ID ролі
)

# Таблиця для зв’язку ролей і дозволів
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),  # ID ролі
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),  # ID дозволу
)


# =========================
# User
# =========================

# Основна модель користувача
class User(Base):
    tablename = "users"

    id = Column(Integer, primary_key=True)  # Унікальний ID
    username = Column(String)  # Логін
    email = Column(String)  # Email
    password_hash = Column(String)  # Захешований пароль
    is_active = Column(Boolean, default=True)  # Статус акаунта
    group_id = Column(Integer, ForeignKey("groups.id"))  # Посилання на групу

    full_name = Column(String)  # Повне ім’я
    created_at = Column(DateTime, default=datetime.utcnow)  # Дата створення

    # Зв’язки
    roles = relationship("Role", secondary=user_roles)  # Ролі користувача
    group = relationship("Group")  # Група користувача


# =========================
# Role
# =========================

# Роль користувача (admin, student)
class Role(Base):
    tablename = "roles"

    id = Column(Integer, primary_key=True)  # ID ролі
    name = Column(String)  # Назва ролі


# =========================
# Permission
# =========================

# Дозволи для ролей
class Permission(Base):
    tablename = "permissions"

    id = Column(Integer, primary_key=True)  # ID дозволу
    name = Column(String)  # Назва дозволу


# =========================
# Group
# =========================

# Група студентів
class Group(Base):
    tablename = "groups"

    id = Column(Integer, primary_key=True)  # ID групи
    name = Column(String)  # Назва групи


# =========================
# Subject
# =========================

# Предмет
class Subject(Base):
    tablename = "subjects"

    id = Column(Integer, primary_key=True)  # ID предмета
    name = Column(String)  # Назва предмета
    credits = Column(Float)  # Кредити


# =========================
# Grade
# =========================

# Оцінка студента
class Grade(Base):
    tablename = "grades"

    id = Column(Integer, primary_key=True)  # ID оцінки
    student_id = Column(Integer, ForeignKey("users.id"))  # Студент
    subject_id = Column(Integer, ForeignKey("subjects.id"))  # Предмет
    grade = Column(Integer)  # Бал
    date_assigned = Column(DateTime, default=datetime.utcnow)  # Дата
