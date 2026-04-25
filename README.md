# Doremi326

娛樂 × 教學平台，部署於 GCP 免費方案 (e2-micro)。

## 技術棧

| 層 | 技術 |
|---|---|
| 後端 | Python + FastAPI + SQLAlchemy |
| 前端 | Vue 3 + Vite |
| 資料庫 | PostgreSQL |
| 部署 | GCP e2-micro (us-west1-b) |
| 認證 | Google OAuth 2.0 |
| HTTPS | Let's Encrypt + nip.io |

## 環境資訊

- **VM**: `35.212.198.32` (us-west1-b, e2-micro)
- **Domain**: `https://35.212.198.32.nip.io`
- **SSH**: `ssh rekam@35.212.198.32 -i ~/.ssh/google_compute_engine`

## 本地開發

```bash
# Backend
cd backend
cp .env.example .env    # 填入 GOOGLE_CLIENT_ID 等
uv sync
uv run uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## 部署

```bash
bash deploy/deploy.sh
```

## 專案結構

```
doremi326/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI 入口
│   │   ├── core/
│   │   │   ├── config.py    # 設定
│   │   │   └── database.py  # DB 連線
│   │   ├── api/routes/      # API 路由
│   │   └── models/          # SQLAlchemy models
│   ├── pyproject.toml
│   └── .env.example
├── frontend/                # Vue 3 + Vite
├── deploy/
│   └── deploy.sh            # 部署腳本
└── README.md
```
