# doremi326 後端本地開發說明

## 快速啟動

```powershell
# 在專案根目錄執行（Windows PowerShell）
.\dev.ps1
```

這個腳本會自動：
1. 建立 SSH Tunnel 連接雲端 PostgreSQL（localhost:5432 → GCP）
2. 啟動 FastAPI backend（http://localhost:8000）
3. 啟動 Vue frontend（http://localhost:5173）

## 開發模式特性

- **OAuth 旁路**：`DEV_BYPASS_AUTH=true` → 不需 Google 帳號即可測試
- **快速登入**：`GET http://localhost:8000/api/auth/dev-login`
- **API 文件**：`http://localhost:8000/api/docs`（DEBUG 模式下開啟）

## ⚠️ 安全規範（第一條）

| 規則 | 說明 |
|------|------|
| 禁止在正式環境使用 `DEV_BYPASS_AUTH=true` | 任何人都能繞過登入 |
| `.env.local` 不可 commit | 包含帳號密碼 |
| 不要開啟 GCP Ops Agent Monitoring | 會產生費用 |
| 不要建立 VM Snapshot | 會產生存儲費用 |
| 雲端 DB 只透過 SSH Tunnel 存取 | 不要直接暴露 PostgreSQL port |

## 手動啟動（不用 dev.ps1）

```powershell
# 1. SSH Tunnel（開另一個 terminal）
ssh -L 5432:localhost:5432 rekam@35.212.198.32 -i ~/.ssh/google_compute_engine -N

# 2. Backend（再開一個 terminal）
cd backend
uv run uvicorn app.main:app --reload --port 8000 --env-file .env.local

# 3. Frontend（再開一個 terminal）
cd frontend
npm run dev
```
