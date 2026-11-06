# Testing
One-time: `psql postgres -c "create database agroseason_test owner agro" -c "create database agroseason_e2e owner agro"`; `cd frontend && npx playwright install chromium`.
Run everything: `scripts/test.sh` (`SKIP_E2E=1` to skip browsers).
- Backend (`pytest`, 82 tests): migrations (test DB rebuilt via Alembic), search (English/Tamil/Thanglish), API, calendar, guide honesty, research pipeline (mocked Serper/OpenAI), cache/dedupe/budget, sketch (OpenCV, license rules), rate limits, SSRF, CORS, SQLi.
- Frontend unit (`vitest`, 10) and Playwright E2E (13, desktop + mobile viewport) against an isolated DB seeded by `backend/e2e_fixture.py` (labelled TEST fixtures – never run on real data).
- Docker: `scripts/docker-smoke.sh` (health, routing, search, port exposure, worker job, restart persistence). Note: it submits one research request; with real keys configured that costs a few cents.
All paid APIs are mocked in automated tests.
