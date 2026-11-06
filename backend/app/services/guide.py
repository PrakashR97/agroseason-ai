from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CultivationGuide, ResearchSource

# key, English label, Tamil label
SECTIONS = [
    ("introduction", "Crop introduction", "பயிர் அறிமுகம்"),
    ("scientific_name", "Scientific name", "அறிவியல் பெயர்"),
    ("names", "Tamil and English names", "தமிழ் மற்றும் ஆங்கிலப் பெயர்கள்"),
    ("suitable_districts", "Suitable districts", "ஏற்ற மாவட்டங்கள்"),
    ("varieties", "Suitable varieties", "ஏற்ற இரகங்கள்"),
    ("sowing_seasons", "Sowing seasons", "விதைப்புப் பருவங்கள்"),
    ("harvest_seasons", "Harvest seasons", "அறுவடைப் பருவங்கள்"),
    ("climate", "Climate requirements", "காலநிலைத் தேவைகள்"),
    ("soil", "Soil requirements", "மண் தேவைகள்"),
    ("soil_ph", "Soil pH", "மண் கார அமிலத்தன்மை"),
    ("land_preparation", "Land preparation", "நில ஆயத்தம்"),
    ("seed_selection", "Seed selection", "விதைத் தேர்வு"),
    ("seed_treatment", "Seed treatment", "விதை நேர்த்தி"),
    ("seed_rate", "Seed rate", "விதை அளவு"),
    ("nursery", "Nursery preparation", "நாற்றங்கால் தயாரிப்பு"),
    ("sowing_method", "Direct sowing or transplanting", "நேரடி விதைப்பு / நடவு"),
    ("sowing_depth", "Sowing depth", "விதைப்பு ஆழம்"),
    ("plant_spacing", "Plant spacing", "செடி இடைவெளி"),
    ("row_spacing", "Row spacing", "வரிசை இடைவெளி"),
    ("irrigation", "Irrigation", "நீர்ப்பாசனம்"),
    ("nutrient_management", "Nutrient management", "ஊட்டச்சத்து மேலாண்மை"),
    ("fertilizer", "Fertilizer recommendations", "உர பரிந்துரைகள்"),
    ("weed_management", "Weed management", "களை மேலாண்மை"),
    ("pests", "Common pests", "பொதுவான பூச்சிகள்"),
    ("diseases", "Common diseases", "பொதுவான நோய்கள்"),
    ("ipm", "Integrated pest management", "ஒருங்கிணைந்த பூச்சி மேலாண்மை"),
    ("growth_stages", "Growth stages", "வளர்ச்சி நிலைகள்"),
    ("first_harvest", "First harvest", "முதல் அறுவடை"),
    ("repeated_harvests", "Repeated harvests", "தொடர் அறுவடைகள்"),
    ("yield", "Approximate yield", "மகசூல்"),
    ("post_harvest", "Post-harvest handling", "அறுவடைக்குப் பின் கையாளுதல்"),
    ("seasonal_precautions", "Seasonal precautions", "பருவகால முன்னெச்சரிக்கைகள்"),
]
SECTION_KEYS = [s[0] for s in SECTIONS]
INSUFFICIENT = "Insufficient verified information."


def get_guide(db: Session, crop, district_id: int | None) -> dict:
    guides = db.scalars(select(CultivationGuide).where(CultivationGuide.crop_id == crop.id)).all()
    state = next((g for g in guides if g.district_id is None), None)
    dist = next((g for g in guides if district_id and g.district_id == district_id), None)

    all_ids: set[int] = set()
    for g in (state, dist):
        if g:
            for sec in g.sections.values():
                all_ids.update(sec.get("source_ids", []))
    sources = {s.id: s for s in db.scalars(select(ResearchSource).where(ResearchSource.id.in_(all_ids)))} if all_ids else {}

    out = []
    for key, en, ta in SECTIONS:
        sec, scope = None, None
        if dist and key in dist.sections:
            sec, scope = dist.sections[key], "district"
        elif state and key in state.sections:
            sec, scope = state.sections[key], "state"
        item = {"key": key, "label_en": en, "label_ta": ta}
        if key == "scientific_name" and crop.scientific_name and sec is None:
            item.update(value=crop.scientific_name, status="catalog", scope="catalog", sources=[])
        elif key == "names" and sec is None:
            item.update(value=f"{crop.name_en} / {crop.name_ta}", status="catalog", scope="catalog", sources=[])
        elif sec is None:
            item.update(value=None, status="missing", scope=None, sources=[], message=INSUFFICIENT)
        else:
            item.update(
                value=sec.get("value"), status=sec.get("status", "review_required"), scope=scope,
                note=sec.get("note"),
                sources=[{"id": i, "title": sources[i].title, "url": sources[i].url,
                          "retrieved_at": sources[i].retrieved_at.isoformat(), "trusted": sources[i].is_trusted}
                         for i in sec.get("source_ids", []) if i in sources],
            )
        out.append(item)
    documented = sum(1 for s in out if s["status"] in ("verified", "review_required"))
    return {"crop_id": crop.id, "district_id": district_id, "sections": out,
            "documented_sections": documented, "total_sections": len(out)}
