from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.routers import auth
from app.routes.students import router as students_router
from app.routes.teachers import router as teachers_router
from app.routes.admin import router as admin_router
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.rate_limiter import limiter

app = FastAPI(
    title="Електронний деканат",
    description="API для управління академічними даними",
    version="0.6.0"
)

# Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security Headers
app.add_middleware(SecurityHeadersMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router)
app.include_router(students_router)
app.include_router(teachers_router)
app.include_router(admin_router)

@app.get("/")
def root():
    return {"message": "Електронний деканат API v0.6.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}