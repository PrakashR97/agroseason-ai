# Database schema (PostgreSQL 15+)
Core: `districts`, `crop_categories`, `crops`, `crop_aliases` (indexed `alias_norm`, `alias_skel`), `crop_varieties`, `crop_district_seasons` (`district_id` NULL = Tamil Nadu level), `cultivation_guides` (JSONB `sections`, one row per crop+district), `research_sources`, `research_evidence`, `farming_diagrams`, `research_jobs`, `research_cache`.
Operational: `sketches` (license + attribution), `api_usage_log` (per-call tokens/cost), `alembic_version`.
Constraints: unique slugs; `uq_crop_alias_norm`; `uq_season_scope` and `uq_guide_scope` use `NULLS NOT DISTINCT` so state-level rows are unique too; FKs with cascade for crop children.
Seed (`python -m app.seed.run`, idempotent): 38 districts, 16 categories, 95 crops, ~500 aliases, cultivar *names* (unverified), 3 unverified sample paddy seasons.
