from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.auth.dependencies import require_role


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/")
def admin_home(
    current_user: User = Depends(require_role("admin"))
):
    return {
        "message": "Admin route works",
        "user": current_user.username
    }


@router.get("/users")
def list_users(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    users = db.query(User).all()

    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name
        }
        for user in users
    ]