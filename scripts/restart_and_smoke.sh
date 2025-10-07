#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

wait_ok() {
  local url="$1" name="$2" max="$3" sleep_s="${4:-1}"
  echo "==> Waiting for ${name} at ${url} ..."
  for i in $(seq 1 "${max}"); do
    code="$(curl -s -o /dev/null -w '%{http_code}' -m 3 "${url}" || true)"
    if [[ "${code}" == "200" ]]; then
      echo "    ${name} ready (HTTP 200)"
      return 0
    fi
    sleep "${sleep_s}"
  done
  echo "    ${name} not ready after ${max} attempts (last code=${code})"
  return 1
}

echo "==> Releasing ports (9002, 9003)"
bash "${ROOT_DIR}/scripts/release_ports.sh"

echo "==> Starting services (backend:9003, frontend:9002)"
bash "${ROOT_DIR}/scripts/start_services.sh"

# Readiness checks
wait_ok "http://localhost:9003/api/v1/health" "backend" 20 1
wait_ok "http://localhost:9002/" "frontend" 20 1

echo "==> Running smoke test (via frontend proxy)"
bash "${ROOT_DIR}/scripts/smoke_test.sh"

echo "==> Done."