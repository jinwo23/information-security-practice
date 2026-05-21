from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError

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


router = APIRouter(prefix="/auth", tags=["Authentication"])

<<<<<<< HEAD

def get_user_role(user: User) -> str:
    if hasattr(user, "roles") and user.roles:
        return user.roles[0].name

    if hasattr(user, "role") and user.role:
        return user.role

    return "student"


=======
# Тестовий endpoint для перевірки роботи auth
>>>>>>> 66b99151b6a7664ca4c6f797fb149ef5b12802d3
@router.get("/test")
def test_auth():
    return {"message": "auth працює"}


# Реєстрація користувача
@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):

    # Перевіряємо чи існує користувач з таким username
    existing_user = db.query(User).filter(
        User.username == user_data.username
    ).first()

    if existing_user:
        # Якщо існує — повертаємо помилку
        raise HTTPException(
            status_code=409,
            detail="Користувач вже існує"
        )

    # Перевірка email
    existing_email = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=409,
            detail="Email вже існує"
        )

    # Створюємо нового користувача
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        password_hash=hash_password(user_data.password),  # Хешуємо пароль
    )

    # Зберігаємо в БД
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Повертаємо створеного користувача
    return new_user


<<<<<<< HEAD
@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.username == data.username
    ).first()
=======
# Логін користувача
@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
>>>>>>> 66b99151b6a7664ca4c6f797fb149ef5b12802d3

    # Шукаємо користувача
    user = db.query(User).filter(
        User.username == data.username
    ).first()

    # Перевіряємо пароль
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Невірний логін або пароль"
        )

<<<<<<< HEAD
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
=======
    # Успішний вхід
    return LoginResponse(
        message="Успішний вхід",
        user_id=user.id,
        username=user.username,
        roles=[]
    )
    
    @router.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
>>>>>>> 66b99151b6a7664ca4c6f797fb149ef5b12802d3
