#!/bin/bash
set -e

VM="rekam@35.212.198.32"
SSH_KEY="$HOME/.ssh/google_compute_engine"
REMOTE_DIR="~/doremi326"
LOCAL_DIR="$(dirname "$0")/.."

echo "=== Deploying doremi326 to GCP ==="

# 1. rsync 同步（排除不需要的）
rsync -avz --delete \
  --exclude='.venv' \
  --exclude='node_modules' \
  --exclude='dist' \
  --exclude='.git' \
  --exclude='__pycache__' \
  --exclude='data/' \
  --exclude='.env' \
  --exclude='certs/' \
  -e "ssh -i $SSH_KEY" \
  "$LOCAL_DIR/" "$VM:$REMOTE_DIR/"

# 2. 在 VM 上 build + 重啟
ssh -i "$SSH_KEY" "$VM" << 'REMOTE'
set -e
cd ~/doremi326
export PATH="$HOME/.local/bin:$PATH"

echo "--- Python 依賴 ---"
cd backend && uv sync && cd ..

echo "--- 前端 build ---"
cd frontend && npm ci && npm run build && cd ..

echo "--- 重啟服務 ---"
sudo systemctl restart doremi326 || echo "Service not set up yet"

echo "=== Deploy 完成! ==="
REMOTE

# 3. 驗證
echo "=== 驗證 ==="
sleep 3
curl -sk https://35.212.198.32.nip.io/api/health || echo "Service starting..."
echo ""
echo "=== Done ==="
