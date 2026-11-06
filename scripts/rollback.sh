#!/usr/bin/env bash
# Roll back to the release recorded before the last deploy. Usage: scripts/rollback.sh user@host
set -euo pipefail
TARGET="${1:?usage: rollback.sh user@host}"; REMOTE_DIR="${REMOTE_DIR:-/opt/agroseason-ai}"
ssh "$TARGET" "REMOTE_DIR='$REMOTE_DIR' bash -s" <<'REMOTE'
set -euo pipefail
cd "$REMOTE_DIR"; PREV=$(cat .previous_release); echo "Rolling back to $PREV"
git checkout "$PREV"; F="-f docker-compose.yml -f docker-compose.prod.yml"
export TAG="$(git rev-parse --short HEAD)"; docker compose $F build && docker compose $F up -d
REMOTE
