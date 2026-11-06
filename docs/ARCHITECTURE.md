# Architecture

```
Browser ── Traefik ─┬─ web (nginx, static React build)
                    └─ api (FastAPI)  /api /media /health
                          │   ├─ PostgreSQL (internal network only)
                          │   └─ Redis (internal network only) ── worker (python worker.py)
                          └─ outbound: Serper.dev, OpenAI, Wikimedia Commons (api + worker only)
```
- `backend/app/models.py` – SQLAlchemy models; `alembic/` – migrations; `app/seed/` – idempotent seeds.
- `app/services/`: `search` (aliases + phonetic skeleton), `calendar`, `guide`, `research`, `sketch`, `costcontrol`, `ratelimit`, `safenet` (SSRF-safe fetch), `providers` (Serper/OpenAI clients).
- Jobs: DB rows (`research_jobs`) are authoritative; Redis list `agro:jobs` only wakes the worker. The worker re-enqueues queued jobs on start and every idle 15s sweep, retries with exponential backoff (max 3 attempts).
- Frontend: Vite + React Router + Tailwind v4. Two colours only; states use text, borders and SVG patterns.
- Verification statuses: `verified`, `review_required`, `unverified` (plus `missing`/`catalog` in guide output).
