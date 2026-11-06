#!/usr/bin/env bash
# Backup PostgreSQL + media volume of the AgroSeason stack. Run on the host that runs Docker.
# Usage: COMPOSE_FILES="-f docker-compose.yml -f docker-compose.prod.yml" scripts/backup.sh [dest_dir]
set -euo pipefail
cd "$(dirname "$0")/.."
DEST="${1:-./backups}"; STAMP=$(date +%Y%m%d-%H%M%S); mkdir -p "$DEST"
FILES=${COMPOSE_FILES:-"-f docker-compose.yml"}
docker compose $FILES exec -T db pg_dump -U agro -Fc agroseason > "$DEST/db-$STAMP.dump"
docker compose $FILES exec -T api tar -C /data -cf - media > "$DEST/media-$STAMP.tar"
find "$DEST" -name 'db-*.dump' -mtime +14 -delete; find "$DEST" -name 'media-*.tar' -mtime +14 -delete
echo "Backup written: $DEST/db-$STAMP.dump, $DEST/media-$STAMP.tar"
