#!/usr/bin/env bash
set -euo pipefail

BASE="http://localhost:9002"

echo "[HOME]"
curl -sS -m 8 -o /tmp/home.html -w 'code=%{http_code} size=%{size_download}\n' "${BASE}/"
sed -n '1,20p' /tmp/home.html | sed 's/<[^>]*>//g' | head -n 10
echo

echo "[HEALTH VIA PROXY]"
curl -sS -m 8 -o /tmp/health.json -w 'code=%{http_code} size=%{size_download}\n' "${BASE}/api/v1/health"
tail -c 300 /tmp/health.json || true
echo

echo "[PROGRESSIVE VIA PROXY]"
curl -sS -m 12 -o /tmp/prog.json -w 'code=%{http_code} size=%{size_download}\n' -X POST "${BASE}/api/v1/company/process/progressive" \
  -H 'Content-Type: application/json' \
  -d '{"input_text":"查询海尔集团","disable_cache":true,"enable_network":false}'
head -c 800 /tmp/prog.json || true
echo