#!/usr/bin/env bash
# Start local dev: API (8000), worker, Vite (5173). Requires local PostgreSQL + Redis (see docs/LOCAL_SETUP.md).
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .run
(cd backend && .venv/bin/alembic upgrade head && .venv/bin/python -m app.seed.run)
(cd backend && nohup .venv/bin/uvicorn app.main:app --port 8000 --reload > ../.run/api.log 2>&1 & echo $! > ../.run/api.pid)
(cd backend && nohup .venv/bin/python worker.py > ../.run/worker.log 2>&1 & echo $! > ../.run/worker.pid)
(cd frontend && nohup npx vite > ../.run/web.log 2>&1 & echo $! > ../.run/web.pid)
echo "API http://localhost:8000/docs | Web http://localhost:5173 | logs in .run/"
