import os
import subprocess
import sys
from pathlib import Path

TEST_DB = "postgresql+psycopg://agro:agro_local_dev@localhost:5432/agroseason_test"
os.environ["DATABASE_URL"] = TEST_DB
os.environ["ALEMBIC_DATABASE_URL"] = TEST_DB
os.environ["REDIS_URL"] = ""  # in-memory rate limiting, no queue in tests
os.environ["OPENAI_API_KEY"] = ""
os.environ["SERPER_API_KEY"] = ""
os.environ["MEDIA_DIR"] = str(Path(__file__).parent / "_media")
os.environ["RATE_LIMIT_PER_MINUTE"] = "10000"

import pytest  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.config import get_settings  # noqa: E402

get_settings.cache_clear()
BACKEND = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session", autouse=True)
def migrated_db():
    """Rebuild the test DB from migrations (this is also the migration test)."""
    from app.db import Base, get_engine
    eng = get_engine()
    with eng.begin() as c:
        c.execute(text("drop schema public cascade; create schema public"))
    r = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=BACKEND,
                       capture_output=True, text=True, env=os.environ)
    assert r.returncode == 0, r.stderr
    yield
    Base.metadata.clear() if False else None


@pytest.fixture()
def db(migrated_db):
    from app.db import session_factory
    from app.seed.run import seed
    s = session_factory()()
    seed(s)
    yield s
    s.rollback()
    # clean mutable tables between tests, keep seeded catalog
    for t in ("research_evidence", "research_cache", "research_jobs", "api_usage_log", "sketches",
              "cultivation_guides", "farming_diagrams"):
        s.execute(text(f"delete from {t}"))
    s.execute(text("delete from crop_district_seasons where notes is distinct from 'Representative sample record pending source verification. Not an agronomic recommendation.'"))
    s.execute(text("delete from research_sources"))
    s.commit()
    s.close()


@pytest.fixture()
def client(db):
    from fastapi.testclient import TestClient
    from app.main import create_app
    from app.services.ratelimit import limiter
    limiter.reset()
    return TestClient(create_app())
