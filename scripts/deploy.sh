#!/usr/bin/env bash
# Deploy/update AgroSeason AI on the VPS over SSH from your Mac. Safe for shared hosts: only touches the
# agroseason compose project in $REMOTE_DIR. Never prunes, never stops other containers.
# Usage: scripts/deploy.sh user@host [git-ref]       (REMOTE_DIR default /opt/agroseason-ai)
set -euo pipefail
TARGET="${1:?usage: deploy.sh user@host [git-ref]}"; REF="${2:-main}"
REMOTE_DIR="${REMOTE_DIR:-/opt/agroseason-ai}"
read -r -p "Deploy ref '$REF' to $TARGET:$REMOTE_DIR ? Type 'deploy' to confirm: " ok
[ "$ok" = "deploy" ] || { echo aborted; exit 1; }
ssh "$TARGET" "REMOTE_DIR='$REMOTE_DIR' REF='$REF' bash -s" <<'REMOTE'
set -euo pipefail
cd "$REMOTE_DIR"
[ -f .env ] || { echo ".env missing on server (see docs/DEPLOYMENT.md)"; exit 1; }
git rev-parse HEAD > .previous_release 2>/dev/null || true
git fetch --all --prune && git checkout "$REF" && git pull --ff-only origin "$REF" || true
F="-f docker-compose.yml -f docker-compose.prod.yml"
export TAG="$(git rev-parse --short HEAD)"
docker compose $F build
docker compose $F up -d
docker compose $F ps
REMOTE
echo "Deployed. Verify with: scripts/health-check.sh https://<domain>"
