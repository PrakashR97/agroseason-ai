import pytest
from sqlalchemy import select

from app.models import (
    ApiUsageLog, Crop, CropDistrictSeason, CultivationGuide, District, ResearchEvidence, ResearchJob,
)
from app.services import costcontrol, research

PAGE = ("<html><body><h1>Tomato cultivation in Tamil Nadu</h1><p>" + "Tomato is a warm season crop grown widely. " * 8 +
        "Tomato requires well drained red loam soil with pH 6.0 to 7.0 for best growth.</p>"
        "<p>In Salem district, tomato is sown during October to November for the rabi season.</p></body></html>")


class FakeSerper:
    def __init__(self, links): self.links, self.calls = links, 0
    def search(self, q, num=8):
        self.calls += 1
        return [{"link": l, "title": f"T {l}"} for l in self.links]


class FakeLLM:
    def __init__(self, payload): self.payload, self.calls = payload, 0
    def extract_json(self, system, user):
        self.calls += 1
        import copy
        return copy.deepcopy(self.payload), 1000, 200


GOOD = {"crop_matches": True, "fields": [
    {"field_key": "soil", "value": "Well drained red loam, pH 6.0 to 7.0",
     "evidence_quote": "Tomato requires well drained red loam soil with pH 6.0 to 7.0 for best growth.", "district": None, "general_guidance": True},
    {"field_key": "seed_rate", "value": "500 g per hectare",
     "evidence_quote": "Seed rate of tomato is 500 g per hectare", "district": None, "general_guidance": True},  # fabricated quote
], "seasons": [
    {"season_name": "Rabi", "sow_start_month": 10, "sow_end_month": 11, "district": "Salem",
     "general_guidance": True, "evidence_quote": "In Salem district, tomato is sown during October to November for the rabi season."}]}


def fetcher(url):
    return PAGE.encode(), "text/html"


def mkjob(db, district="salem"):
    crop = db.query(Crop).filter_by(slug="tomato").one()
    d = db.query(District).filter_by(slug=district).one()
    job = ResearchJob(kind="research", crop_id=crop.id, district_id=d.id, month=11,
                      dedupe_key=research.dedupe_key(crop.id, d.id, 11), status="queued")
    db.add(job); db.commit()
    return crop, d, job


def test_pipeline_validates_against_source(db):
    crop, d, job = mkjob(db)
    serper = FakeSerper(["https://agritech.tnau.ac.in/tomato.html", "https://blog.example.com/t"])
    llm = FakeLLM(GOOD)
    res = research.run_research(db, job, serper=serper, llm=llm, fetch=fetcher)
    assert job.status == "completed"
    g = db.query(CultivationGuide).filter_by(crop_id=crop.id, district_id=None).one()
    assert g.sections["soil"]["status"] == "verified"
    assert "seed_rate" not in g.sections            # fabricated quote rejected
    assert res["fields_rejected"] >= 1
    ev = db.scalars(select(ResearchEvidence).where(ResearchEvidence.field_key == "seed_rate")).all()
    assert ev and not ev[0].quote_validated
    season = db.query(CropDistrictSeason).filter_by(crop_id=crop.id, district_id=d.id).one()
    assert (season.verification_status, season.sow_start_month, season.sow_end_month) == ("verified", 10, 11)
    assert db.query(ApiUsageLog).filter_by(provider="openai").count() >= 1
    assert db.query(ApiUsageLog).filter_by(provider="serper").count() == 2


def test_untrusted_source_is_review_required(db):
    crop, d, job = mkjob(db)
    research.run_research(db, job, serper=FakeSerper(["https://blog.example.com/t"]), llm=FakeLLM(GOOD), fetch=fetcher)
    g = db.query(CultivationGuide).filter_by(crop_id=crop.id).one()
    assert g.sections["soil"]["status"] == "review_required"
    assert job.status == "review_required"


def test_insufficient_when_nothing_valid(db):
    crop, d, job = mkjob(db)
    bad = {"crop_matches": True, "fields": [{"field_key": "soil", "value": "x 99", "evidence_quote": "not in the page at all really"}], "seasons": []}
    res = research.run_research(db, job, serper=FakeSerper(["https://tnau.ac.in/x"]), llm=FakeLLM(bad), fetch=fetcher)
    assert job.status == "insufficient" and res["message"] == "Insufficient verified information."
    assert db.query(CultivationGuide).count() == 0


def test_conflicting_sources_flagged(db):
    crop, d, job = mkjob(db)
    payloads = iter([
        {"crop_matches": True, "fields": [{"field_key": "soil", "value": "Red loam pH 6.0 to 7.0",
          "general_guidance": True, "evidence_quote": "Tomato requires well drained red loam soil with pH 6.0 to 7.0 for best growth."}], "seasons": []},
        {"crop_matches": True, "fields": [{"field_key": "soil", "value": "Sandy soil",
          "general_guidance": True, "evidence_quote": "Tomato is a warm season crop grown widely."}], "seasons": []}])

    class L:
        def extract_json(self, s, u): return next(payloads), 10, 10
    research.run_research(db, job, serper=FakeSerper(["https://a.tnau.ac.in/1", "https://b.icar.gov.in/2"]), llm=L(), fetch=fetcher)
    g = db.query(CultivationGuide).filter_by(crop_id=crop.id).one()
    assert g.sections["soil"]["status"] == "review_required" and "Conflicting" in g.sections["soil"]["note"]


def test_prompt_injection_and_wrong_crop_ignored(db):
    crop, d, job = mkjob(db)
    llm = FakeLLM({"crop_matches": False, "fields": GOOD["fields"], "seasons": []})
    research.run_research(db, job, serper=FakeSerper(["https://tnau.ac.in/x"]), llm=llm, fetch=fetcher)
    assert job.status == "insufficient"


def test_request_dedupe_and_cache(db):
    crop = db.query(Crop).filter_by(slug="tomato").one()
    d = db.query(District).filter_by(slug="salem").one()
    queued = []
    r1 = research.request_research(db, crop, d, 11, queued.append)
    r2 = research.request_research(db, crop, d, 11, queued.append)
    assert r1["state"] == "queued" and r2["state"] == "existing_job" and len(queued) == 1
    assert r2["job"].id == r1["job"].id
    research.run_research(db, r1["job"], serper=FakeSerper(["https://tnau.ac.in/x"]), llm=FakeLLM(GOOD), fetch=fetcher)
    r3 = research.request_research(db, crop, d, 11, queued.append)
    assert r3["state"] == "cached" and len(queued) == 1   # no new paid calls


def test_sufficient_verified_data_skips_research(db):
    crop = db.query(Crop).filter_by(slug="tomato").one()
    secs = {k: {"value": "v", "status": "verified", "source_ids": []} for k in ["soil", "climate", "irrigation", "yield", "pests"]}
    db.add(CultivationGuide(crop_id=crop.id, sections=secs))
    db.add(CropDistrictSeason(crop_id=crop.id, season_name="X", sow_start_month=1, sow_end_month=2, verification_status="verified"))
    db.commit()
    r = research.request_research(db, crop, None, None, lambda i: None)
    assert r["state"] == "cached" and r["reason"] == "verified_data_sufficient"


def test_budget_limits(db, monkeypatch):
    from app.config import get_settings
    monkeypatch.setattr(get_settings(), "serper_daily_limit", 1)
    crop = db.query(Crop).filter_by(slug="tomato").one()
    costcontrol.record_usage(db, "serper", "search")
    r = research.request_research(db, crop, None, None, lambda i: None)
    assert r["state"] == "budget_exhausted"
    assert db.query(ResearchJob).count() == 0


def test_monthly_budget(db, monkeypatch):
    from app.config import get_settings
    monkeypatch.setattr(get_settings(), "monthly_budget_usd", 0.0005)
    costcontrol.record_usage(db, "serper", "search")
    with pytest.raises(costcontrol.BudgetExhausted):
        costcontrol.ensure_budget(db, "openai")


def test_process_job_retry_and_failure(db, monkeypatch):
    crop, d, job = mkjob(db)

    def boom(*a, **k): raise RuntimeError("provider down")
    monkeypatch.setattr(research, "run_research", boom)
    j = research.process_job(db, job.id)
    assert j.status == "queued" and j.attempts == 1
    research.process_job(db, job.id); research.process_job(db, job.id)
    j = db.get(ResearchJob, job.id)
    assert j.status == "failed" and j.attempts == 3 and "provider down" in j.error
    assert research.process_job(db, job.id).attempts == 3  # no further retries


def test_post_research_api(client, db, monkeypatch):
    monkeypatch.setattr("app.queue.enqueue", lambda i: True)
    r = client.post("/api/research", json={"crop": "Thakkali", "district": "Salem", "month": 11})
    assert r.status_code == 200 and r.json()["state"] == "queued"
    jid = r.json()["job"]["id"]
    assert client.get(f"/api/research/jobs/{jid}").json()["status"] == "queued"
    assert client.post("/api/research", json={"crop": "Thakkali", "district": "Salem", "month": 11}).json()["state"] == "existing_job"
    assert client.post("/api/research", json={"crop": "nonsense"}).status_code == 404
    assert client.post("/api/research", json={"crop": "tomato", "month": 13}).status_code == 422
    assert client.get("/api/research/jobs/none").status_code == 404
    assert client.get("/api/research/usage").json()["serper_today"] == 0


def test_extraction_helpers():
    assert research.is_trusted_domain("agritech.tnau.ac.in")
    assert not research.is_trusted_domain("tnau.ac.in.evil.com")
    assert research.numbers_supported("pH 6.0 to 7.0", "soil pH 6.0 to 7.0")
    assert not research.numbers_supported("500 g", "no figures here")


def test_anecdote_urls_and_non_guidance_rejected(db):
    crop, d, job = mkjob(db)
    serper = FakeSerper(["https://agritech.tnau.ac.in/success_stories/tomato.html", "https://tnau.ac.in/news/tomato"])
    llm = FakeLLM(GOOD)
    res = research.run_research(db, job, serper=serper, llm=llm, fetch=fetcher)
    assert llm.calls == 0 and job.status == "insufficient"
    assert all("not agronomic guidance" in x for x in res["skipped"])
    assert research.is_guidance_url("https://tnau.ac.in/crop/tomato.html")


def test_non_general_guidance_items_dropped(db):
    crop, d, job = mkjob(db)
    anecdote = {"crop_matches": True, "seasons": [], "fields": [
        {"field_key": "yield", "value": "40 t", "general_guidance": False,
         "evidence_quote": "Tomato requires well drained red loam soil with pH 6.0 to 7.0 for best growth."}]}
    research.run_research(db, job, serper=FakeSerper(["https://tnau.ac.in/crop/t"]), llm=FakeLLM(anecdote), fetch=fetcher)
    assert job.status == "insufficient" and db.query(CultivationGuide).count() == 0


def test_barely_mentioned_crop_skipped(db):
    crop, d, job = mkjob(db)
    page = "<html><body><p>" + "General agriculture department notice about many topics. " * 12 + "Tomato once.</p></body></html>"
    llm = FakeLLM(GOOD)
    research.run_research(db, job, serper=FakeSerper(["https://tnau.ac.in/crop/t"]), llm=llm,
                          fetch=lambda u: (page.encode(), "text/html"))
    assert llm.calls == 0
