#!/usr/bin/env bash
# Restore a pg_dump backup into the AgroSeason database (DESTRUCTIVE for that database only).
# Usage: scripts/restore.sh backups/db-YYYYMMDD-HHMMSS.dump
set -euo pipefail
cd "$(dirname "$0")/.."
DUMP="${1:?usage: restore.sh <dump file>}"; FILES=${COMPOSE_FILES:-"-f docker-compose.yml"}
read -r -p "This REPLACES data in the agroseason database. Type 'restore' to continue: " ok
[ "$ok" = "restore" ] || { echo aborted; exit 1; }
docker compose $FILES exec -T db pg_restore -U agro -d agroseason --clean --if-exists --no-owner < "$DUMP"
echo "Restore complete"
