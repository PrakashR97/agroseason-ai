#!/usr/bin/env bash
# Start local dev: API (8000), worker, Vite (5173). Requires local PostgreSQL + Redis (see docs/LOCAL_SETUP.md).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUN="$ROOT/.run"; mkdir -p "$RUN"
"$ROOT/scripts/dev-down.sh" >/dev/null 2>&1 || true

# Local (non-Docker) settings: explicit, so a Docker-oriented .env cannot break them.
export DATABASE_URL="${DATABASE_URL:-postgresql+psycopg://agro:agro_local_dev@localhost:5432/agroseason}"
export REDIS_URL="${REDIS_URL:-redis://127.0.0.1:6379/0}"
export MEDIA_DIR="${MEDIA_DIR:-$ROOT/backend/data/media}"
export CORS_ORIGINS="http://localhost:5173,http://127.0.0.1:5173"

cd "$ROOT/backend"
.venv/bin/alembic upgrade head
.venv/bin/python -m app.seed.run
nohup .venv/bin/uvicorn app.main:app --port 8000 --reload > "$RUN/api.log" 2>&1 < /dev/null &
echo $! > "$RUN/api.pid"
nohup .venv/bin/python worker.py > "$RUN/worker.log" 2>&1 < /dev/null &
echo $! > "$RUN/worker.pid"
cd "$ROOT/frontend"
nohup npx vite --host 127.0.0.1 > "$RUN/web.log" 2>&1 < /dev/null &
echo $! > "$RUN/web.pid"

for i in $(seq 1 30); do
  curl -fsS http://127.0.0.1:8000/health >/dev/null 2>&1 && curl -fsS http://127.0.0.1:5173/ >/dev/null 2>&1 && break
  sleep 1
done
echo "API  http://localhost:8000/docs"
echo "Web  http://localhost:5173"
echo "Logs $RUN/"
