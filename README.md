# AgroSeason AI

Crop-season and cultivation guidance for all 38 Tamil Nadu districts. React + Tailwind frontend (strict two-colour UI: `#166534` + white), FastAPI backend, PostgreSQL, Redis worker, evidence-validated research (Serper.dev + GPT-4o-mini) and OpenCV pencil sketches.

**Principle:** nothing is shown as verified unless a stored source quote backs it. Gaps display *"Insufficient verified information."*

## Status: software vs. research coverage
- **Software:** complete (catalog, multilingual search, calendar, guides, research pipeline, sketches, cost controls).
- **Research coverage:** intentionally small. The catalog has 95 crops and 38 districts (names/aliases only). Only 3 *unverified* sample paddy seasons are seeded. Verified data accumulates only when research jobs run on demand.

## Quick start (local)
See [docs/LOCAL_SETUP.md](docs/LOCAL_SETUP.md). Short form: `scripts/dev-up.sh` → http://localhost:5173.
Docker: `docker compose -f docker-compose.yml -f docker-compose.local.yml up -d --build` → http://localhost:8088.

## Docs
[Architecture](docs/ARCHITECTURE.md) · [API](docs/API_DOCUMENTATION.md) · [Database](docs/DATABASE_SCHEMA.md) · [Research](docs/RESEARCH_WORKFLOW.md) · [Sketches](docs/SKETCH_ENGINE.md) · [Security](docs/SECURITY.md) · [Deployment](docs/DEPLOYMENT.md) · [Testing](docs/TESTING.md) · [Cost control](docs/COST_CONTROL.md)
