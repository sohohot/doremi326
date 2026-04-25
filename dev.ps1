# dev.ps1 - 一鍵啟動本地開發環境
# 用法: .\dev.ps1
# 會開啟：SSH Tunnel (DB) + FastAPI backend + Vite frontend

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$SSH_KEY = "$env:USERPROFILE\.ssh\google_compute_engine"
$VM = "rekam@35.212.198.32"

Write-Host "==============================" -ForegroundColor Cyan
Write-Host " Doremi326 本地開發環境啟動" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""

# ⚠️ 安全提示
Write-Host "⚠️  安全提示：" -ForegroundColor Yellow
Write-Host "   - 此模式連接雲端 PostgreSQL，請勿在公用網路使用" -ForegroundColor Yellow
Write-Host "   - DEV_BYPASS_AUTH=true，OAuth 已停用，僅限本地測試" -ForegroundColor Yellow
Write-Host "   - .env.local 不會 commit 到 git，請妥善保管" -ForegroundColor Yellow
Write-Host ""

# 1. 開啟 SSH Tunnel（雲端 DB → 本機 5432）
Write-Host "[1/3] 建立 SSH Tunnel 到雲端 PostgreSQL..." -ForegroundColor Green
$tunnelJob = Start-Job -ScriptBlock {
    param($key, $vm)
    ssh -i $key -L 5432:localhost:5432 $vm -N -o StrictHostKeyChecking=no 2>&1
} -ArgumentList $SSH_KEY, $VM

Start-Sleep -Seconds 3
Write-Host "      SSH Tunnel 已建立 (localhost:5432 → GCP DB)" -ForegroundColor Gray

# 2. 啟動 FastAPI Backend
Write-Host "[2/3] 啟動 FastAPI Backend (port 8000)..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    param($root)
    Set-Location "$root\backend"
    # 使用 .env.local 覆蓋設定
    $env:ENV_FILE = ".env.local"
    & uv run uvicorn app.main:app --reload --port 8000 --env-file .env.local 2>&1
} -ArgumentList $ProjectRoot

Start-Sleep -Seconds 4

# 3. 啟動 Vue Frontend
Write-Host "[3/3] 啟動 Vue Frontend (port 5173)..." -ForegroundColor Green
$frontendJob = Start-Job -ScriptBlock {
    param($root)
    Set-Location "$root\frontend"
    & npm run dev 2>&1
} -ArgumentList $ProjectRoot

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "==============================" -ForegroundColor Cyan
Write-Host " ✅ 開發環境已啟動！" -ForegroundColor Green
Write-Host ""
Write-Host "  前端：http://localhost:5173" -ForegroundColor White
Write-Host "  後端：http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs：http://localhost:8000/api/docs" -ForegroundColor White
Write-Host "  Dev 快速登入：http://localhost:8000/api/auth/dev-login" -ForegroundColor White
Write-Host ""
Write-Host "  按 Ctrl+C 停止所有服務" -ForegroundColor Gray
Write-Host "==============================" -ForegroundColor Cyan

# 持續監控，直到 Ctrl+C
try {
    while ($true) {
        Start-Sleep -Seconds 5
        # 顯示 job 輸出
        $backendJob | Receive-Job -Keep | Select-Object -Last 2 | ForEach-Object {
            if ($_ -match "ERROR|error") { Write-Host "[Backend] $_" -ForegroundColor Red }
        }
    }
} finally {
    Write-Host "`n停止所有服務..." -ForegroundColor Yellow
    Stop-Job $tunnelJob, $backendJob, $frontendJob -ErrorAction SilentlyContinue
    Remove-Job $tunnelJob, $backendJob, $frontendJob -ErrorAction SilentlyContinue
    Write-Host "已停止。" -ForegroundColor Gray
}
