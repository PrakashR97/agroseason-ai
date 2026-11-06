"""Farming calendar: built only from documented season records."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import VERIFIED, Crop, CropDistrictSeason

PHASES = ("nursery", "sowing", "transplanting", "growth", "harvest")


def month_range(start: int | None, end: int | None) -> list[int]:
    """Inclusive month window; supports cross-year (e.g. 12 -> 2)."""
    if not start:
        return []
    end = end or start
    out, m = [], start
    for _ in range(12):
        out.append(m)
        if m == end:
            break
        m = m % 12 + 1
    return out


def _add_months(month: int, days: int) -> int:
    return (month - 1 + round(days / 30.4)) % 12 + 1


def season_phases(s: CropDistrictSeason) -> tuple[dict[int, set[str]], bool]:
    """Phase map month -> phases. Second value: harvest computed from durations (estimate)."""
    phases: dict[int, set[str]] = {m: set() for m in range(1, 13)}
    estimated = False
    for m in month_range(s.nursery_start_month, s.nursery_end_month):
        phases[m].add("nursery")
    sow = month_range(s.sow_start_month, s.sow_end_month)
    for m in sow:
        phases[m].add("sowing")
    for m in month_range(s.transplant_start_month, s.transplant_end_month):
        phases[m].add("transplanting")
    harvest = month_range(s.harvest_start_month, s.harvest_end_month)
    if not harvest and sow and s.duration_days_min:
        first = _add_months(sow[0], s.duration_days_min)
        last = _add_months(sow[-1], s.duration_days_max or s.duration_days_min)
        harvest = month_range(first, last)
        estimated = True
    for m in harvest:
        phases[m].add("harvest")
    # growth = months strictly between the last sowing/transplant month and first harvest month
    if harvest and sow:
        start_m = (month_range(s.transplant_start_month, s.transplant_end_month) or sow)[-1]
        m = start_m % 12 + 1
        guard = 0
        while m not in harvest and guard < 12:
            phases[m].add("growth")
            m = m % 12 + 1
            guard += 1
    return phases, estimated


def build_calendar(db: Session, crop: Crop, district_id: int | None, month: int | None = None,
                   variety_id: int | None = None, irrigation: str | None = None) -> dict:
    stmt = select(CropDistrictSeason).where(CropDistrictSeason.crop_id == crop.id)
    rows = db.scalars(stmt).all()
    scope = "none"
    chosen = [r for r in rows if district_id and r.district_id == district_id]
    if chosen:
        scope = "district"
    else:
        chosen = [r for r in rows if r.district_id is None]
        if chosen:
            scope = "state"
    if variety_id is not None:
        chosen = [r for r in chosen if r.variety_id in (None, variety_id)]
    if irrigation:
        chosen = [r for r in chosen if r.irrigation in ("any", irrigation)]

    months = {m: {"month": m, "phases": [], "suitability": "not_documented", "seasons": [], "all_verified": None} for m in range(1, 13)}
    seasons_out = []
    for s in chosen:
        phases, estimated = season_phases(s)
        verified = s.verification_status == VERIFIED
        seasons_out.append({
            "id": s.id, "season_name": s.season_name, "irrigation": s.irrigation,
            "verification_status": s.verification_status, "source_id": s.source_id,
            "harvest_estimated": estimated, "repeated_harvest": s.repeated_harvest, "notes": s.notes,
            "duration_days_min": s.duration_days_min, "duration_days_max": s.duration_days_max,
        })
        for m, ph in phases.items():
            if not ph:
                continue
            cell = months[m]
            for p in ph:
                if p not in cell["phases"]:
                    cell["phases"].append(p)
            cell["seasons"].append(s.season_name)
            cell["all_verified"] = verified if cell["all_verified"] is None else (cell["all_verified"] and verified)
            if "sowing" in ph or "nursery" in ph or "transplanting" in ph:
                level = "recommended" if verified else "documented_unverified"
                if cell["suitability"] != "recommended":
                    cell["suitability"] = level
    for cell in months.values():
        cell["phases"].sort(key=PHASES.index)
    result = {
        "crop_id": crop.id, "crop_type": crop.crop_type, "scope": scope,
        "district_id": district_id, "months": [months[m] for m in range(1, 13)],
        "seasons": seasons_out,
        "message": None if seasons_out else "Insufficient verified information.",
        "disclaimer": "Months show documented windows only; harvest timing is not guaranteed.",
    }
    if month:
        c = months[month]
        result["selected_month"] = {"month": month, "suitability": c["suitability"], "phases": c["phases"]}
    return result
