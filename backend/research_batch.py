"""Manual, budget-capped batch research (never runs automatically).

  python research_batch.py --crops okra brinjal chilli --yes
  python research_batch.py --crops okra --district salem --yes

Each crop = one normal research job (DB-first, cache, dedupe, daily/monthly budgets all apply).
Estimated cost: roughly $0.005-0.02 per crop.
"""
import argparse
import sys

from sqlalchemy import select

from app.db import session_factory
from app.models import Crop
from app.services import costcontrol, research
from app.services.search import resolve_crop, resolve_district


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--crops", nargs="+", required=True, help="crop names/slugs (any language)")
    ap.add_argument("--district", help="optional district for every crop")
    ap.add_argument("--max", type=int, default=15, help="safety cap on number of crops")
    ap.add_argument("--yes", action="store_true", help="confirm that paid API calls are intended")
    a = ap.parse_args()
    if len(a.crops) > a.max:
        print(f"Refusing: {len(a.crops)} crops > --max {a.max}")
        return 2
    with session_factory()() as db:
        district = resolve_district(db, a.district) if a.district else None
        crops = []
        for name in a.crops:
            c = resolve_crop(db, name)
            print(("OK   " if c else "MISS ") + name + (f" -> {c.slug}" if c else ""))
            if c:
                crops.append(c)
        print(f"{len(crops)} crops, estimated cost ${len(crops) * 0.01:.2f}; usage so far: {costcontrol.usage_summary(db)}")
        if not a.yes:
            print("Dry run. Add --yes to run.")
            return 0
        for c in crops:
            res = research.request_research(db, c, district, None, lambda _id: None)
            if res["state"] != "queued":
                print(f"{c.slug}: skipped ({res['state']}: {res.get('reason')})")
                if res["state"] == "budget_exhausted":
                    break
                continue
            job = research.process_job(db, res["job"].id)
            r = job.result or {}
            print(f"{c.slug}: {job.status} verified_sections={r.get('sections_verified')} "
                  f"review={r.get('sections_review')} seasons={r.get('seasons_stored')} err={job.error}")
        print("usage:", costcontrol.usage_summary(db))
    return 0


if __name__ == "__main__":
    sys.exit(main())
