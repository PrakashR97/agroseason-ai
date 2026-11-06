# API
Interactive docs: `/docs` (OpenAPI at `/openapi.json`) when running the API directly. Errors: `{"detail": ...}`; validation errors 422 `{"detail":"Validation failed","errors":[{field,message}]}`; rate limit 429 with `Retry-After`.

| Endpoint | Notes |
|---|---|
| `GET /health` | DB + Redis status (503 if DB down) |
| `GET /api/districts` | 38 districts |
| `GET /api/categories` | crop categories |
| `GET /api/crops?q&category&page&page_size` | paginated; `q` ranked by match quality |
| `GET /api/crops/search?q&district_id&month&limit` | suggestions (English/Tamil/Thanglish, fuzzy); `month_suitability` when month given |
| `GET /api/crops/{id}` | names, aliases, varieties, record counts |
| `GET /api/districts/{id}/crops?month&category` | crops with documented seasons (district or state scope) |
| `GET /api/crops/{id}/districts` | districts with district-level records |
| `GET /api/calendar?crop_id&district_id&month&variety_id&irrigation` | 12 months × phases; `scope` = district/state/none |
| `GET /api/cultivation-guide?crop_id&district_id` | 32 sections, each verified/review_required/missing/catalog with sources |
| `GET /api/sketches/{crop_id}?kind&generate` | cached sketch or placeholder; `generate=true` queues a job (deduped, budget-checked) |
| `POST /api/research` `{crop,district?,month?}` | DB-first → cache → dedupe → queue. `state`: cached/queued/existing_job/budget_exhausted. 5/hour/IP by default |
| `GET /api/research/jobs`, `/jobs/{id}`, `/usage` | job tracking and budget status |
