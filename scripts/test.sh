#!/usr/bin/env bash
# Run all local tests: backend (pytest), frontend (vitest + build), E2E (Playwright). Paid APIs are mocked.
set -euo pipefail
cd "$(dirname "$0")/.."
echo "== backend"; (cd backend && .venv/bin/python -m pytest -q)
echo "== frontend unit"; (cd frontend && npx vitest run)
echo "== frontend build"; (cd frontend && npx vite build >/dev/null && echo build ok)
if [ "${SKIP_E2E:-0}" != "1" ]; then echo "== e2e"; (cd frontend && npx playwright test); fi
