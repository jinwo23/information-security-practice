from fastapi import FastAPI
from app.routers import auth
from app.routes.students import router as students_router
from app.routes.teachers import router as teachers_router
from app.routes.admin import router as admin_router

app = FastAPI(
    title="Електронний деканат",
    description="API для управління академічними даними",
    version="0.5.0"
)

app.include_router(auth.router)
app.include_router(students_router)
app.include_router(teachers_router)
app.include_router(admin_router)

@app.get("/")
def root():
    return {"message": "Електронний деканат API v0.5.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}