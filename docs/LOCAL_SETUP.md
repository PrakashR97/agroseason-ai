# Local setup (macOS)
Requirements: Python 3.12, Node 22+, PostgreSQL 15+ (uses `NULLS NOT DISTINCT`), Redis.
```bash
brew install postgresql@17 redis && brew services start postgresql@17 && brew services start redis
psql postgres -c "create role agro login password 'agro_local_dev'" -c "create database agroseason owner agro"
cd backend && python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
cd ../frontend && npm install
cd .. && scripts/dev-up.sh      # migrations + seed + api + worker + vite
scripts/dev-down.sh
```
Environment: copy `.env.example` to `.env`; for non-Docker runs uncomment `DATABASE_URL`/`REDIS_URL`. Without API keys the app works; research/sketch jobs fail gracefully with "not configured".
Migrations: `cd backend && .venv/bin/alembic upgrade head`; new: `alembic revision --autogenerate -m msg`.
Tests need extra databases (see TESTING.md): `agroseason_test`, `agroseason_e2e`.
Troubleshooting: `pg_isready`; `redis-cli -h 127.0.0.1 ping`; logs in `.run/`.
