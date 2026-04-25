from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.core.config import settings

router = APIRouter()


class GoogleTokenRequest(BaseModel):
    token: str  # Google ID token from frontend


class AuthResponse(BaseModel):
    access_token: str
    user_email: str
    user_name: str


@router.post("/google", response_model=AuthResponse)
async def google_login(body: GoogleTokenRequest):
    """Google 登入。本地開發模式可用 DEV_BYPASS_AUTH 跳過實際驗證。"""

    # ⚠️ 本地開發模式：跳過 Google 驗證
    if settings.DEV_BYPASS_AUTH:
        return AuthResponse(
            access_token="dev-mock-token",
            user_email=settings.DEV_MOCK_USER_EMAIL,
            user_name=settings.DEV_MOCK_USER_NAME,
        )

    # 正式流程：驗證 Google ID token
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests

        idinfo = id_token.verify_oauth2_token(
            body.token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid Google token: {e}")

    email = idinfo.get("email")
    name = idinfo.get("name", "")

    # TODO: 存入 DB 建立/更新 user record

    return AuthResponse(
        access_token=body.token,  # placeholder - 之後替換成正式 JWT
        user_email=email,
        user_name=name,
    )


@router.get("/dev-login")
async def dev_login():
    """
    ⚠️ 僅限本地開發！訪問此路由可直接登入為 mock user。
    正式環境務必確保 DEV_BYPASS_AUTH=false。
    """
    if not settings.DEV_BYPASS_AUTH:
        raise HTTPException(status_code=403, detail="Dev login only available in DEV_BYPASS_AUTH mode")

    return AuthResponse(
        access_token="dev-mock-token",
        user_email=settings.DEV_MOCK_USER_EMAIL,
        user_name=settings.DEV_MOCK_USER_NAME,
    )


@router.get("/me")
async def get_current_user():
    """TODO: 實作 JWT 驗證"""
    raise HTTPException(status_code=401, detail="Not authenticated")

