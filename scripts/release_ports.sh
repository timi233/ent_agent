#!/usr/bin/env bash
set -euo pipefail

PORTS=(9002 9003)
for p in "${PORTS[@]}"; do
  echo "Releasing TCP port ${p}..."
  fuser -k "${p}/tcp" || true
done

echo "Ports released: ${PORTS[*]}"