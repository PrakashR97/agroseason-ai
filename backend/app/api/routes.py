from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app import queue
from app.config import get_settings
from app.db import get_db
from app.models import (
    VERIFIED, Crop, CropAlias, CropCategory, CropDistrictSeason, District, ResearchJob, Sketch,
)
from app.schemas import (
    CategoryOut, CropDetail, CropInDistrict, CropOut, CropSearchHit, DistrictForCrop, DistrictOut,
    JobOut, Page, ResearchRequest, ResearchResponse, VarietyOut,
)
from app.services import costcontrol, research, sketch
from app.services.calendar import build_calendar, season_phases
from app.services.guide import get_guide
from app.services.ratelimit import general_limit, research_limit
from app.services.search import resolve_crop, resolve_district, search_crops

router = APIRouter(prefix="/api", dependencies=[Depends(general_limit)])


def _crop_or_404(db: Session, crop_id: int) -> Crop:
    crop = db.scalar(select(Crop).options(joinedload(Crop.category)).where(Crop.id == crop_id))
    if crop is None:
        raise HTTPException(404, "Crop not found")
    return crop


def _district_or_404(db: Session, district_id: int) -> District:
    d = db.get(District, district_id)
    if d is None:
        raise HTTPException(404, "District not found")
    return d


def _suitability(db: Session, crop: Crop, district_id: int | None, month: int) -> str:
    return build_calendar(db, crop, district_id, month)["selected_month"]["suitability"]


@router.get("/districts", response_model=list[DistrictOut])
def list_districts(db: Session = Depends(get_db)):
    return db.scalars(select(District).order_by(District.name_en)).all()


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.scalars(select(CropCategory).order_by(CropCategory.sort_order)).all()


@router.get("/crops", response_model=Page[CropOut])
def list_crops(category: str | None = None, q: str | None = Query(None, max_length=100),
               page: int = Query(1, ge=1), page_size: int = Query(24, ge=1, le=100),
               db: Session = Depends(get_db)):
    stmt = select(Crop).options(joinedload(Crop.category))
    if category:
        stmt = stmt.join(CropCategory).where(CropCategory.slug == category)
    if q:  # ranked by match quality, not alphabetically
        ranked = [c.id for c, _, _ in search_crops(db, q, limit=100)]
        allowed = set(db.scalars(stmt.with_only_columns(Crop.id)).unique().all())
        ranked = [i for i in ranked if i in allowed]
        total = len(ranked)
        page_ids = ranked[(page - 1) * page_size: page * page_size]
        by_id = {c.id: c for c in db.scalars(stmt.where(Crop.id.in_(page_ids or [-1]))).unique()}
        return Page(items=[by_id[i] for i in page_ids if i in by_id], total=total, page=page, page_size=page_size)
    total = db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery()))
    items = db.scalars(stmt.order_by(Crop.name_en).offset((page - 1) * page_size).limit(page_size)).unique().all()
    return Page(items=items, total=total or 0, page=page, page_size=page_size)


@router.get("/crops/search", response_model=list[CropSearchHit])
def crops_search(q: str = Query(..., min_length=1, max_length=100), district_id: int | None = None,
                 month: int | None = Query(None, ge=1, le=12), limit: int = Query(10, ge=1, le=25),
                 db: Session = Depends(get_db)):
    hits = search_crops(db, q, limit)
    out = []
    for crop, score, alias in hits:
        _ = crop.category
        out.append(CropSearchHit(
            crop=CropOut.model_validate(crop), score=round(score, 3), matched_alias=alias,
            month_suitability=_suitability(db, crop, district_id, month) if month else None))
    return out


@router.get("/crops/{crop_id}", response_model=CropDetail)
def crop_detail(crop_id: int, db: Session = Depends(get_db)):
    crop = _crop_or_404(db, crop_id)
    seasons = db.scalars(select(CropDistrictSeason).where(CropDistrictSeason.crop_id == crop.id)).all()
    return CropDetail(
        **CropOut.model_validate(crop).model_dump(),
        description_en=crop.description_en, description_ta=crop.description_ta,
        aliases=sorted({a.alias for a in crop.aliases}),
        varieties=[VarietyOut.model_validate(v) for v in sorted(crop.varieties, key=lambda v: v.name)],
        season_records=len(seasons),
        verified_season_records=sum(1 for s in seasons if s.verification_status == VERIFIED))


@router.get("/districts/{district_id}/crops", response_model=Page[CropInDistrict])
def district_crops(district_id: int, month: int | None = Query(None, ge=1, le=12),
                   category: str | None = None, page: int = Query(1, ge=1),
                   page_size: int = Query(24, ge=1, le=100), db: Session = Depends(get_db)):
    _district_or_404(db, district_id)
    rows = db.scalars(select(CropDistrictSeason).where(
        (CropDistrictSeason.district_id == district_id) | (CropDistrictSeason.district_id.is_(None)))).all()
    by_crop: dict[int, list[CropDistrictSeason]] = {}
    for r in rows:
        by_crop.setdefault(r.crop_id, []).append(r)
    stmt = select(Crop).options(joinedload(Crop.category)).where(Crop.id.in_(by_crop or [-1]))
    if category:
        stmt = stmt.join(CropCategory).where(CropCategory.slug == category)
    crops = db.scalars(stmt.order_by(Crop.name_en)).unique().all()
    items = []
    for c in crops:
        recs = by_crop[c.id]
        dist_recs = [r for r in recs if r.district_id == district_id]
        use = dist_recs or recs
        suit = _suitability(db, c, district_id, month) if month else None
        if month and suit == "not_documented":
            continue
        status = VERIFIED if all(r.verification_status == VERIFIED for r in use) else (
            "review_required" if any(r.verification_status != "unverified" for r in use) else "unverified")
        items.append(CropInDistrict(crop=CropOut.model_validate(c), scope="district" if dist_recs else "state",
                                    verification_status=status, seasons=sorted({r.season_name for r in use}),
                                    month_suitability=suit))
    total = len(items)
    return Page(items=items[(page - 1) * page_size: page * page_size], total=total, page=page, page_size=page_size)


@router.get("/crops/{crop_id}/districts", response_model=list[DistrictForCrop])
def crop_districts(crop_id: int, db: Session = Depends(get_db)):
    _crop_or_404(db, crop_id)
    rows = db.scalars(select(CropDistrictSeason).where(
        CropDistrictSeason.crop_id == crop_id, CropDistrictSeason.district_id.is_not(None))).all()
    grouped: dict[int, list[CropDistrictSeason]] = {}
    for r in rows:
        grouped.setdefault(r.district_id, []).append(r)
    districts = {d.id: d for d in db.scalars(select(District).where(District.id.in_(grouped or [-1])))}
    out = []
    for did, recs in grouped.items():
        status = VERIFIED if all(r.verification_status == VERIFIED for r in recs) else "review_required"
        out.append(DistrictForCrop(district=DistrictOut.model_validate(districts[did]), verification_status=status,
                                   seasons=sorted({r.season_name for r in recs})))
    return sorted(out, key=lambda x: x.district.name_en)


@router.get("/calendar")
def calendar(crop_id: int, district_id: int | None = None, month: int | None = Query(None, ge=1, le=12),
             variety_id: int | None = None, irrigation: str | None = Query(None, pattern="^(irrigated|rainfed)$"),
             db: Session = Depends(get_db)):
    crop = _crop_or_404(db, crop_id)
    if district_id:
        _district_or_404(db, district_id)
    return build_calendar(db, crop, district_id, month, variety_id, irrigation)


@router.get("/cultivation-guide")
def cultivation_guide(crop_id: int, district_id: int | None = None, db: Session = Depends(get_db)):
    crop = _crop_or_404(db, crop_id)
    if district_id:
        _district_or_404(db, district_id)
    return get_guide(db, crop, district_id)


@router.get("/sketches/{crop_id}")
def get_sketch(crop_id: int, kind: str = Query("produce", pattern="^(produce|plant|seed|seedling|stage)$"),
               generate: bool = False, db: Session = Depends(get_db)):
    crop = _crop_or_404(db, crop_id)
    sk = db.scalar(select(Sketch).where(Sketch.crop_id == crop.id, Sketch.kind == kind))
    out = sketch.sketch_to_dict(sk, crop, kind)
    out["job_id"] = None
    if out["status"] == "generated" or not generate:
        return out
    key = f"sketch:{crop.id}:{kind}"
    active = db.scalar(select(ResearchJob).where(ResearchJob.dedupe_key == key, ResearchJob.status.in_(research.ACTIVE)))
    if active:
        out["job_id"] = active.id
        return out
    # do not retry a failed lookup more than once a week
    import datetime as dt
    from app.models import utcnow
    if sk is not None and sk.updated_at > utcnow() - dt.timedelta(days=7):
        return out
    if not get_settings().serper_api_key:
        out["reason"] = "Sketch generation is not configured"
        return out
    try:
        costcontrol.ensure_budget(db, "serper")
    except costcontrol.BudgetExhausted as e:
        out["reason"] = str(e)
        return out
    job = ResearchJob(kind="sketch", crop_id=crop.id, dedupe_key=key, status="queued")
    db.add(job)
    db.commit()
    queue.enqueue(job.id)
    out["job_id"] = job.id
    return out


@router.post("/research", response_model=ResearchResponse, dependencies=[Depends(research_limit)])
def post_research(body: ResearchRequest, db: Session = Depends(get_db)):
    crop = resolve_crop(db, body.crop)
    if crop is None:
        raise HTTPException(404, "Crop not recognised. Try the Tamil, English or Thanglish name.")
    district = None
    if body.district:
        district = resolve_district(db, body.district)
        if district is None:
            raise HTTPException(404, "District not recognised.")
    res = research.request_research(db, crop, district, body.month, queue.enqueue)
    job = res.get("job")
    message = {
        "budget_exhausted": "Research budget reached. Showing existing verified data only.",
        "cached": "Existing data is available; no new research needed.",
    }.get(res["state"])
    return ResearchResponse(state=res["state"], reason=res.get("reason"),
                            job=JobOut.model_validate(job) if job else None,
                            summary=res.get("summary"), cache=res.get("cache"), message=message)


@router.get("/research/jobs", response_model=list[JobOut])
def list_jobs(limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    return db.scalars(select(ResearchJob).order_by(ResearchJob.created_at.desc()).limit(limit)).all()


@router.get("/research/usage")
def research_usage(db: Session = Depends(get_db)):
    return costcontrol.usage_summary(db)


@router.get("/research/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.get(ResearchJob, job_id)
    if job is None:
        raise HTTPException(404, "Job not found")
    return job
