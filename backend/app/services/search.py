from __future__ import annotations

import difflib

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Crop, CropAlias, District
from app.seed.districts import DISTRICT_ALIASES
from app.services.textnorm import is_tamil, normalize, skeleton


def _like_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace("%", r"\%").replace("_", r"\_")


def search_crops(db: Session, q: str, limit: int = 10) -> list[tuple[Crop, float, str]]:
    """Return (crop, score, matched_alias). Exact > prefix > substring > phonetic > fuzzy."""
    n = normalize(q)
    if not n:
        return []
    sk = skeleton(q)
    best: dict[int, tuple[float, str]] = {}

    def put(alias: CropAlias, score: float) -> None:
        cur = best.get(alias.crop_id)
        if cur is None or score > cur[0]:
            best[alias.crop_id] = (score, alias.alias)

    esc = _like_escape(n)
    rows = db.scalars(
        select(CropAlias).where(or_(
            CropAlias.alias_norm == n,
            CropAlias.alias_norm.like(esc + "%", escape="\\"),
            CropAlias.alias_norm.like("%" + esc + "%", escape="\\") if len(n) >= 3 else CropAlias.alias_norm == n,
            CropAlias.alias_skel == sk,
        ))
    ).all()
    for a in rows:
        if a.alias_norm == n:
            put(a, 1.0)
        elif a.alias_norm.startswith(n):
            put(a, 0.9)
        elif n in a.alias_norm:
            put(a, 0.75)
        elif a.alias_skel == sk:
            put(a, 0.8)

    if len(best) < limit and not is_tamil(n) and len(n) >= 3:
        # fuzzy fallback over phonetic skeletons (small table, indexed read)
        for a in db.scalars(select(CropAlias).where(CropAlias.lang != "ta")).all():
            if a.crop_id in best and best[a.crop_id][0] >= 0.7:
                continue
            ratio = difflib.SequenceMatcher(None, sk, a.alias_skel).ratio()
            if ratio >= 0.78:
                put(a, 0.5 + ratio * 0.2)

    ids = list(best)
    if not ids:
        return []
    crops = {c.id: c for c in db.scalars(select(Crop).where(Crop.id.in_(ids)))}
    out = [(crops[i], s, al) for i, (s, al) in best.items() if i in crops]
    out.sort(key=lambda t: (-t[1], t[0].name_en))
    return out[:limit]


def resolve_crop(db: Session, q: str) -> Crop | None:
    res = search_crops(db, q, limit=1)
    if res and res[0][1] >= 0.75:
        return res[0][0]
    return None


def resolve_district(db: Session, q: str) -> District | None:
    n = normalize(q)
    if not n:
        return None
    n = DISTRICT_ALIASES.get(n, n)
    for d in db.scalars(select(District)):
        if n in (normalize(d.name_en), normalize(d.name_ta), d.slug):
            return d
    sk = skeleton(n)
    for d in db.scalars(select(District)):
        if skeleton(d.name_en) == sk:
            return d
    return None
