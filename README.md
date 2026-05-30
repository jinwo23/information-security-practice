# Electronic Dean's Office

## Опис

REST API на FastAPI + Docker + Nginx HTTPS.

Проєкт створено для практичних робіт з безпеки інформаційних систем.

## Запуск

docker compose up --build

## Доступ

https://localhost  
https://localhost/docs  

Або напряму до API:

http://localhost:8000  
http://localhost:8000/docs  

## Студенти

Пугач Антон  
Журавський Богдан  
Козаченко Владислав  
Молодоженя Артем  

## Безпека

У проєкті реалізовано базові механізми захисту:

- Автентифікація: Bcrypt-хешування паролів, JWT access та refresh tokens
- Авторизація: RBAC з ролями admin, teacher, student
- Валідація: Pydantic-схеми, ORM-захист від SQL Injection
- Шифрування: Field-Level Encryption для email та телефону
- Audit Log: фіксація подій входу, помилок та дій користувачів
- Brute Force Protection: обмеження кількості спроб входу
- Security Headers: CSP, HSTS, X-Frame-Options, X-Content-Type-Options
- Docker Hardening: non-root user, no-new-privileges
- DevSecOps-перевірки: Bandit, pip-audit, Trivy

Повний звіт аудиту безпеки: [SECURITY_AUDIT.md](./SECURITY_AUDIT.md)