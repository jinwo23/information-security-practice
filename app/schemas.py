from datetime import datetime
import re

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Логін"
    )
    email: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Пароль"
    )
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=150,
        description="Повне ім'я"
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Пароль має містити хоча б одну велику літеру")
        if not re.search(r"[a-z]", v):
            raise ValueError("Пароль має містити хоча б одну малу літеру")
        if not re.search(r"[0-9]", v):
            raise ValueError("Пароль має містити хоча б одну цифру")
        return v


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    message: str
    user_id: int
    username: str
    roles: list[str] = []