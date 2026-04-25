from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "Doremi326"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production"

    DATABASE_URL: str = "postgresql+asyncpg://rekam:doremi326@localhost/doremi326"

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    FRONTEND_URL: str = "http://localhost:5173"
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    # ⚠️ 本地開發用：跳過 OAuth，自動以 mock 帳號登入
    # 正式環境務必設為 false！
    DEV_BYPASS_AUTH: bool = False
    DEV_MOCK_USER_EMAIL: str = "dev@doremi326.local"
    DEV_MOCK_USER_NAME: str = "Dev User"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
