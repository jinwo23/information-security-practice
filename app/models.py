from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship

from app.database import Base
from app.crypto.encryption import encrypt_field, decrypt_field


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
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)  # Унікальний ID
    username = Column(String)  # Логін

    # У БД зберігається не відкритий email/phone, а зашифровані значення
    encrypted_email = Column(String)  # Зашифрований email
    encrypted_phone = Column(String, nullable=True)  # Зашифрований телефон

    password_hash = Column(String)  # Захешований пароль
    is_active = Column(Boolean, default=True)  # Статус акаунта
    group_id = Column(Integer, ForeignKey("groups.id"))  # Посилання на групу

    full_name = Column(String)  # Повне ім’я
    created_at = Column(DateTime, default=datetime.utcnow)  # Дата створення

    # Прозоре розшифрування email при читанні
    @property
    def email(self):
        return decrypt_field(self.encrypted_email)

    # Прозоре шифрування email при записі
    @email.setter
    def email(self, value):
        self.encrypted_email = encrypt_field(value)

    # Прозоре розшифрування телефону при читанні
    @property
    def phone(self):
        if self.encrypted_phone:
            return decrypt_field(self.encrypted_phone)
        return None

    # Прозоре шифрування телефону при записі
    @phone.setter
    def phone(self, value):
        if value:
            self.encrypted_phone = encrypt_field(value)
        else:
            self.encrypted_phone = None

    # Зв’язки
    roles = relationship("Role", secondary=user_roles)  # Ролі користувача
    group = relationship("Group")  # Група користувача


# =========================
# Role
# =========================

# Роль користувача (admin, student)
class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)  # ID ролі
    name = Column(String)  # Назва ролі


# =========================
# Permission
# =========================

# Дозволи для ролей
class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)  # ID дозволу
    name = Column(String)  # Назва дозволу


# =========================
# Group
# =========================

# Група студентів
class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)  # ID групи
    name = Column(String)  # Назва групи


# =========================
# Subject
# =========================

# Предмет
class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True)  # ID предмета
    name = Column(String)  # Назва предмета
    credits = Column(Float)  # Кредити


# =========================
# Grade
# =========================

# Оцінка студента
class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True)  # ID оцінки
    student_id = Column(Integer, ForeignKey("users.id"))  # Студент
    subject_id = Column(Integer, ForeignKey("subjects.id"))  # Предмет
    grade = Column(Integer)  # Бал
    date_assigned = Column(DateTime, default=datetime.utcnow)  # Дата