import io

import cv2
import numpy as np
import pytest
from PIL import Image

from app.models import Crop
from app.services import sketch


def fake_photo(w=640, h=480, fmt="JPEG"):
    img = np.full((h, w, 3), 255, np.uint8)
    cv2.circle(img, (w // 2, h // 2), 150, (40, 40, 220), -1)      # red "tomato"
    cv2.circle(img, (w // 2 - 40, h // 2 - 40), 30, (200, 200, 255), -1)
    cv2.rectangle(img, (w // 2 - 10, h // 2 - 190), (w // 2 + 10, h // 2 - 140), (30, 120, 30), -1)
    buf = io.BytesIO()
    Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).save(buf, fmt)
    return buf.getvalue()


def test_pencil_sketch_is_monochrome_on_white():
    out = sketch.make_pencil_sketch(sketch.validate_image(fake_photo()))
    assert out.ndim == 2 and out.dtype == np.uint8
    assert np.mean(out > 235) > 0.4           # mostly white paper
    assert out.min() < 150                    # some graphite lines exist


def test_validate_rejects_bad_images():
    with pytest.raises(sketch.ImageRejected):
        sketch.validate_image(b"not an image")
    with pytest.raises(sketch.ImageRejected):
        sketch.validate_image(fake_photo(50, 50))
    buf = io.BytesIO(); Image.new("RGB", (300, 300)).save(buf, "GIF")
    with pytest.raises(sketch.ImageRejected):
        sketch.validate_image(buf.getvalue())


class FakeSerper:
    def __init__(self): self.calls = 0
    def images(self, q, num=10):
        self.calls += 1
        return [{"link": "https://commons.wikimedia.org/wiki/File:Tomato_je.jpg", "imageUrl": "https://example.com/a.jpg"}]


LICENSED = {"image_url": "https://upload.wikimedia.org/x/Tomato_je.jpg", "page_url": "https://commons.wikimedia.org/wiki/File:Tomato_je.jpg",
            "license_name": "CC BY-SA 3.0", "license_url": "https://creativecommons.org/licenses/by-sa/3.0",
            "attribution": "Jane Doe, CC BY-SA 3.0, via Wikimedia Commons"}


def test_generate_and_cache(db):
    crop = db.query(Crop).filter_by(slug="tomato").one()
    s = FakeSerper()
    sk = sketch.generate_sketch(db, crop, "produce", serper=s, fetch=lambda u: fake_photo(),
                                license_lookup=lambda t: LICENSED)
    assert sk.status == "generated" and sk.attribution.endswith("via Wikimedia Commons")
    from app.config import get_settings
    assert (get_settings().media_dir / sk.file_path).exists()
    d = sketch.sketch_to_dict(sk, crop, "produce")
    assert d["image_url"] == "/media/sketches/tomato-produce.png" and d["license_name"] == "CC BY-SA 3.0"


def test_unlicensed_gets_placeholder_without_download(db):
    crop = db.query(Crop).filter_by(slug="pumpkin").one()

    def no_download(u): raise AssertionError("must not download unlicensed image")
    sk = sketch.generate_sketch(db, crop, "produce", serper=FakeSerper(), fetch=no_download,
                                license_lookup=lambda t: None)
    assert sk.status == "placeholder" and "license" in sk.reason


def test_bad_download_becomes_placeholder(db):
    crop = db.query(Crop).filter_by(slug="pumpkin").one()
    sk = sketch.generate_sketch(db, crop, "produce", serper=FakeSerper(), fetch=lambda u: b"junk",
                                license_lookup=lambda t: LICENSED)
    assert sk.status == "placeholder"


def test_license_allowlist():
    ok = sketch.ALLOWED_LICENSE
    assert ok.match("CC BY-SA 4.0") and ok.match("CC0") and ok.match("Public domain") and ok.match("CC BY 2.0")
    assert not ok.match("CC BY-NC 2.0") and not ok.match("All rights reserved") and not ok.match("CC BY-ND 4.0")


def test_commons_title_extraction():
    assert sketch._commons_title({"link": "https://commons.wikimedia.org/wiki/File:A_b.jpg"}) == "File:A b.jpg"
    assert sketch._commons_title({"imageUrl": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/X.jpg/800px-X.jpg"}) is not None
    assert sketch._commons_title({"link": "https://example.com/x.jpg"}) is None


def test_sketch_api_placeholder_and_job(client, db, monkeypatch):
    from app.config import get_settings
    monkeypatch.setattr(get_settings(), "serper_api_key", "test-key")
    monkeypatch.setattr("app.queue.enqueue", lambda i: True)
    cid = db.query(Crop).filter_by(slug="pumpkin").one().id
    r = client.get(f"/api/sketches/{cid}").json()
    assert r["status"] == "placeholder" and r["job_id"] is None
    r = client.get(f"/api/sketches/{cid}", params={"generate": "true"}).json()
    assert r["job_id"]
    again = client.get(f"/api/sketches/{cid}", params={"generate": "true"}).json()
    assert again["job_id"] == r["job_id"]       # duplicate prevented
    assert client.get(f"/api/sketches/{cid}", params={"kind": "bogus"}).status_code == 422


def test_sketch_api_not_configured_does_not_queue(client, db):
    cid = db.query(Crop).filter_by(slug="pumpkin").one().id
    r = client.get(f"/api/sketches/{cid}", params={"generate": "true"}).json()
    assert r["job_id"] is None and "not configured" in r["reason"]


def test_commons_requests_send_user_agent():
    import httpx
    seen = {}

    def handler(req):
        seen["ua"] = req.headers.get("user-agent", "")
        if "AgroSeasonAI" not in seen["ua"]:
            return httpx.Response(403, text="Please set a user-agent")
        return httpx.Response(200, json={"query": {"pages": {"1": {"imageinfo": [{
            "thumburl": "https://upload.wikimedia.org/x.jpg", "descriptionurl": "https://commons.wikimedia.org/wiki/File:x.jpg",
            "mime": "image/jpeg", "extmetadata": {"LicenseShortName": {"value": "CC BY-SA 4.0"}, "Artist": {"value": "<a>Jo</a>"}}}]}}}})

    from app.services import safenet
    c = httpx.Client(transport=httpx.MockTransport(handler), headers={"User-Agent": safenet.USER_AGENT})
    info = sketch.commons_license("File:x.jpg", client=c)
    assert info and info["attribution"] == "Jo, CC BY-SA 4.0, via Wikimedia Commons"
