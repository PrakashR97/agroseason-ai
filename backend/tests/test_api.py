from app.models import VERIFIED, Crop, CropDistrictSeason, CultivationGuide, District, ResearchSource


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["database"] is True


def test_38_districts(client):
    r = client.get("/api/districts")
    assert r.status_code == 200 and len(r.json()) == 38
    assert any(d["name_en"] == "Salem" and d["name_ta"] == "சேலம்" for d in r.json())


def test_crops_pagination_and_filters(client):
    r = client.get("/api/crops", params={"page_size": 10, "page": 1}).json()
    assert len(r["items"]) == 10 and r["total"] >= 90
    veg = client.get("/api/crops", params={"category": "vegetables", "page_size": 100}).json()
    assert veg["total"] > 10 and all(c["category"]["slug"] == "vegetables" for c in veg["items"])
    assert client.get("/api/crops", params={"q": "தக்காளி"}).json()["items"][0]["slug"] == "tomato"
    assert client.get("/api/crops", params={"page_size": 1000}).status_code == 422


def test_search_endpoint(client):
    r = client.get("/api/crops/search", params={"q": "thakkali"}).json()
    assert r[0]["crop"]["slug"] == "tomato"
    assert client.get("/api/crops/search").status_code == 422


def test_crop_detail_and_404(client):
    cid = client.get("/api/crops/search", params={"q": "paddy"}).json()[0]["crop"]["id"]
    d = client.get(f"/api/crops/{cid}").json()
    assert d["name_ta"] == "நெல்" and "rice" in [a.lower() for a in d["aliases"]]
    assert any(v["name"] == "ADT 45" for v in d["varieties"])
    assert client.get("/api/crops/999999").status_code == 404
    assert client.get("/api/crops/abc").status_code == 422


def _verified_tomato_salem(db):
    tomato = db.query(Crop).filter_by(slug="tomato").one()
    salem = db.query(District).filter_by(slug="salem").one()
    src = ResearchSource(url="https://agritech.tnau.ac.in/test", title="TNAU test", domain="agritech.tnau.ac.in", is_trusted=True)
    db.add(src); db.flush()
    db.add(CropDistrictSeason(crop_id=tomato.id, district_id=salem.id, season_name="Rabi", sow_start_month=10,
                              sow_end_month=11, harvest_start_month=1, harvest_end_month=3,
                              verification_status=VERIFIED, source_id=src.id))
    db.add(CultivationGuide(crop_id=tomato.id, district_id=None, verification_status=VERIFIED, sections={
        "soil": {"value": "Well drained loam", "status": "verified", "source_ids": [src.id]}}))
    db.commit()
    return tomato, salem


def test_calendar_district_and_month(client, db):
    tomato, salem = _verified_tomato_salem(db)
    r = client.get("/api/calendar", params={"crop_id": tomato.id, "district_id": salem.id, "month": 11}).json()
    assert r["scope"] == "district" and r["selected_month"]["suitability"] == "recommended"
    assert "sowing" in r["months"][9]["phases"]
    assert "harvest" in r["months"][0]["phases"] and "harvest" in r["months"][2]["phases"]
    assert client.get("/api/calendar", params={"crop_id": tomato.id, "district_id": salem.id, "month": 6}
                      ).json()["selected_month"]["suitability"] == "not_documented"


def test_calendar_no_data_is_honest(client, db):
    pumpkin = db.query(Crop).filter_by(slug="pumpkin").one()
    r = client.get("/api/calendar", params={"crop_id": pumpkin.id}).json()
    assert r["scope"] == "none" and r["message"] == "Insufficient verified information."
    assert all(m["suitability"] == "not_documented" for m in r["months"])


def test_calendar_sample_season_cross_year_unverified(client, db):
    paddy = db.query(Crop).filter_by(slug="paddy").one()
    r = client.get("/api/calendar", params={"crop_id": paddy.id, "month": 1}).json()
    assert r["scope"] == "state"
    assert r["selected_month"]["suitability"] == "documented_unverified"  # Navarai sowing spans Dec-Jan
    assert all(s["verification_status"] == "unverified" for s in r["seasons"])


def test_guide_never_invents(client, db):
    tomato, salem = _verified_tomato_salem(db)
    g = client.get("/api/cultivation-guide", params={"crop_id": tomato.id, "district_id": salem.id}).json()
    by = {s["key"]: s for s in g["sections"]}
    assert len(g["sections"]) == 32 or len(g["sections"]) >= 30
    assert by["soil"]["status"] == "verified" and by["soil"]["sources"][0]["url"].startswith("https://agritech")
    assert by["seed_rate"]["status"] == "missing" and by["seed_rate"]["message"] == "Insufficient verified information."
    assert by["scientific_name"]["status"] == "catalog"


def test_district_crops_and_crop_districts(client, db):
    tomato, salem = _verified_tomato_salem(db)
    r = client.get(f"/api/districts/{salem.id}/crops", params={"month": 11}).json()
    slugs = [i["crop"]["slug"] for i in r["items"]]
    assert "tomato" in slugs
    t = next(i for i in r["items"] if i["crop"]["slug"] == "tomato")
    assert t["scope"] == "district" and t["verification_status"] == "verified"
    d = client.get(f"/api/crops/{tomato.id}/districts").json()
    assert d[0]["district"]["slug"] == "salem"
    assert client.get("/api/districts/9999/crops").status_code == 404


def test_validation_error_shape(client):
    r = client.get("/api/calendar", params={"crop_id": 1, "month": 13})
    assert r.status_code == 422 and r.json()["detail"] == "Validation failed"
