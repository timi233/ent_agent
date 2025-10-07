#!/usr/bin/env bash
set -euo pipefail

CODE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Backend (9003)
echo "[Backend] Starting uvicorn on 0.0.0.0:9003 ..."
nohup bash -c "cd '${CODE_DIR}/city_brain_system_refactored' && python -m uvicorn main:app --host 0.0.0.0 --port 9003 --reload" >/tmp/backend-uvicorn.log 2>&1 &
sleep 1

# Frontend (9002) strictPort=true
echo "[Frontend] Starting Vite dev server on 0.0.0.0:9002 ..."
nohup bash -c "cd '${CODE_DIR}/city_brain_frontend' && npm run dev -- --host 0.0.0.0 --port 9002" >/tmp/frontend-dev.log 2>&1 &
sleep 2

echo "Services started."
echo "Backend log: /tmp/backend-uvicorn.log"
echo "Frontend log: /tmp/frontend-dev.log"