from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_users():
    """列出使用者（TODO: 需要 admin 權限）"""
    return {"users": []}
