"""Prepare an isolated E2E database: migrations + seed + clearly-labelled TEST fixtures.

Never run against a real database: fixtures contain fake 'verified' records.
"""
import os
import subprocess
import sys

url = os.environ["DATABASE_URL"]
assert url.endswith("agroseason_e2e"), "refusing to run fixtures on a non-e2e database"

from sqlalchemy import create_engine, text  # noqa: E402

# database 'agroseason_e2e' must exist (see docs/TESTING.md)
eng = create_engine(url)
with eng.begin() as c:
    c.execute(text("drop schema public cascade; create schema public"))
subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], check=True, env=os.environ)

import cv2  # noqa: E402
import numpy as np  # noqa: E402
from pathlib import Path  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.models import Crop, CropDistrictSeason, CultivationGuide, District, ResearchSource, Sketch  # noqa: E402
from app.seed.run import seed  # noqa: E402
from app.services.sketch import make_pencil_sketch  # noqa: E402

with Session(eng) as db:
    seed(db)
    tomato = db.query(Crop).filter_by(slug="tomato").one()
    salem = db.query(District).filter_by(slug="salem").one()
    src = ResearchSource(url="https://agritech.tnau.ac.in/e2e-test-fixture", title="E2E TEST FIXTURE (not real data)",
                         domain="agritech.tnau.ac.in", is_trusted=True)
    db.add(src); db.flush()
    db.add(CropDistrictSeason(crop_id=tomato.id, district_id=salem.id, season_name="Rabi (test)", sow_start_month=10,
                              sow_end_month=11, harvest_start_month=1, harvest_end_month=3,
                              verification_status="verified", source_id=src.id))
    db.add(CultivationGuide(crop_id=tomato.id, district_id=None, verification_status="verified", sections={
        "soil": {"value": "TEST FIXTURE soil text", "status": "verified", "source_ids": [src.id]}}))
    media = Path(get_settings().media_dir) / "sketches"
    media.mkdir(parents=True, exist_ok=True)
    img = np.full((400, 400, 3), 255, np.uint8)
    cv2.circle(img, (200, 200), 120, (40, 40, 220), -1)
    cv2.imwrite(str(media / "tomato-produce.png"), make_pencil_sketch(img))
    db.add(Sketch(crop_id=tomato.id, kind="produce", status="generated", file_path="sketches/tomato-produce.png",
                  attribution="Test Author, CC BY-SA 4.0, via Wikimedia Commons", license_name="CC BY-SA 4.0",
                  license_url="https://creativecommons.org/licenses/by-sa/4.0/"))
    db.commit()
print("e2e fixture ready")
