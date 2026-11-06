"""Idempotent seed: python -m app.seed.run"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import session_factory
from app.models import (
    UNVERIFIED, Crop, CropAlias, CropCategory, CropDistrictSeason, CropVariety, District,
)
from app.seed.crops import CATEGORIES, CROPS, SAMPLE_NOTE, SAMPLE_SEASONS, VARIETIES
from app.seed.districts import DISTRICTS
from app.services.textnorm import is_tamil, normalize, skeleton


def _split(s: str) -> list[str]:
    return [p.strip() for p in s.split(",") if p.strip()]


def seed(db: Session) -> dict:
    for slug, en, ta, region in DISTRICTS:
        d = db.scalar(select(District).where(District.slug == slug))
        if d is None:
            db.add(District(slug=slug, name_en=en, name_ta=ta, region=region))
    for i, (slug, en, ta) in enumerate(CATEGORIES):
        if db.scalar(select(CropCategory).where(CropCategory.slug == slug)) is None:
            db.add(CropCategory(slug=slug, name_en=en, name_ta=ta, sort_order=i))
    db.flush()
    cats = {c.slug: c for c in db.scalars(select(CropCategory))}

    for slug, cat, en, ta, sci, ctype, en_aliases, tg_aliases in CROPS:
        crop = db.scalar(select(Crop).where(Crop.slug == slug))
        if crop is None:
            crop = Crop(slug=slug, category_id=cats[cat].id, name_en=en, name_ta=ta,
                        scientific_name=sci, crop_type=ctype, verification_status=UNVERIFIED)
            db.add(crop)
            db.flush()
        have = {a.alias_norm for a in db.scalars(select(CropAlias).where(CropAlias.crop_id == crop.id))}
        wanted = [(en, "en"), (ta, "ta")]
        wanted += [(a, "en") for a in _split(en_aliases)] + [(a, "tanglish") for a in _split(tg_aliases)]
        for alias, lang in wanted:
            n = normalize(alias)
            if not n or n in have:
                continue
            have.add(n)
            db.add(CropAlias(crop_id=crop.id, alias=alias, alias_norm=n, alias_skel=skeleton(alias),
                             lang="ta" if is_tamil(alias) else lang))
    db.flush()
    crops = {c.slug: c for c in db.scalars(select(Crop))}

    for slug, names in VARIETIES.items():
        for name in names:
            exists = db.scalar(select(CropVariety).where(
                CropVariety.crop_id == crops[slug].id, CropVariety.name == name))
            if exists is None:
                db.add(CropVariety(crop_id=crops[slug].id, name=name, verification_status=UNVERIFIED,
                                   notes="Catalog name only; not yet verified against a source."))

    for slug, season, sow, nursery, transplant, harvest in SAMPLE_SEASONS:
        cid = crops[slug].id
        exists = db.scalar(select(CropDistrictSeason).where(
            CropDistrictSeason.crop_id == cid, CropDistrictSeason.district_id.is_(None),
            CropDistrictSeason.season_name == season))
        if exists is None:
            db.add(CropDistrictSeason(
                crop_id=cid, district_id=None, season_name=season, irrigation="any",
                sow_start_month=sow[0], sow_end_month=sow[1],
                nursery_start_month=nursery[0] if nursery else None,
                nursery_end_month=nursery[1] if nursery else None,
                transplant_start_month=transplant[0] if transplant else None,
                transplant_end_month=transplant[1] if transplant else None,
                harvest_start_month=harvest[0], harvest_end_month=harvest[1],
                notes=SAMPLE_NOTE, verification_status=UNVERIFIED))
    db.commit()
    return {
        "districts": len(db.scalars(select(District)).all()),
        "crops": len(crops),
        "aliases": len(db.scalars(select(CropAlias)).all()),
    }


if __name__ == "__main__":
    with session_factory()() as s:
        print(seed(s))
