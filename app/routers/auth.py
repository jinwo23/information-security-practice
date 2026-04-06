# Тестовий endpoint для перевірки роботи auth
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


# Логін користувача
@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):

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

    # Успішний вхід
    return LoginResponse(
        message="Успішний вхід",
        user_id=user.id,
        username=user.username,
        roles=[]
    )
