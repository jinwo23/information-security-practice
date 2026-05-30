# app/routers/auth.py
# Антон: роутер автентифікації з інтеграцією системи аудиту

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from jose import JWTError
from datetime import datetime, timezone

from app.database import get_db
from app.models import User
from app.schemas import (
    UserCreate,
    UserResponse,
    LoginRequest,
    TokenResponse,
    TokenRefreshRequest,
)
from app.security import hash_password, verify_password
from app.auth.jwt_handler import create_access_token, create_refresh_token, verify_token
from app.auth.dependencies import get_current_user
from app.middleware.rate_limiter import limiter

# Богдан: імпортуємо функції аудиту для логування подій входу
from app.audit.logger import log_login_success, log_login_failed
from app.audit.detector import check_brute_force, check_off_hours_access


router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_user_role(user: User) -> str:
    if hasattr(user, "roles") and user.roles:
        return user.roles[0].name
    if hasattr(user, "role") and user.role:
        return user.role
    return "student"


@router.get("/test")
def test_auth():
    return {"message": "auth працює"}


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Реєстрація нового користувача"
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        User.username == user_data.username
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Користувач '{user_data.username}' вже існує"
        )

    existing_email = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{user_data.email}' вже зареєстровано"
        )

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        password_hash=hash_password(user_data.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(request: Request, data: LoginRequest, db: Session = Depends(get_db)):
    ip = request.client.host if request.client else "unknown"

    # Влад: перевірка Brute Force ДО перевірки пароля — важливий порядок!
    if check_brute_force(db, ip):
        log_login_failed(db, data.username, ip, reason="brute_force_blocked")
        raise HTTPException(
            status_code=429,
            detail="Забагато невдалих спроб. Спробуйте через 5 хвилин."
        )

    user = db.query(User).filter(User.username == data.username).first()

    if not user or not verify_password(data.password, user.password_hash):
        # Артем: логуємо невдалу спробу — підвищує лічильник Brute Force
        log_login_failed(db, data.username, ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний логін або пароль"
        )

    # Антон: перевіряємо нічний вхід — деканат не працює між 00:00 і 06:00
    current_hour = datetime.now(timezone.utc).hour
    check_off_hours_access(db, user.id, user.username, ip, current_hour)

    # Богдан: логуємо успішний вхід
    log_login_success(db, user.id, user.username, ip)

    role = get_user_role(user)
    access_token = create_access_token(user.id, role)
    refresh_token = create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(body: TokenRefreshRequest, db: Session = Depends(get_db)):
    try:
        payload = verify_token(body.refresh_token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалідний refresh token"
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Потрібен refresh token"
        )

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token не містить id користувача"
        )

    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Користувача не знайдено"
        )

    role = get_user_role(user)
    access_token = create_access_token(user.id, role)
    refresh_token = create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": get_user_role(current_user)
    }