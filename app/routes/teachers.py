from fastapi import APIRouter

router = APIRouter(
    prefix="/teachers",
    tags=["Teachers"]
)

@router.get("/")
async def get_teachers():
    return {"message": "Teachers route works"}