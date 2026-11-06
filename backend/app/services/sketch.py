"""Pencil sketch engine: licensed photo -> OpenCV pencil sketch, cached with attribution."""
from __future__ import annotations

import html
import io
import re
from pathlib import Path
from urllib.parse import unquote, urlparse

import cv2
import httpx
import numpy as np
from PIL import Image
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Crop, ResearchJob, Sketch, utcnow
from app.services import costcontrol, safenet

KINDS = ("produce", "plant", "seed", "seedling", "stage")
KIND_QUERY = {"produce": "", "plant": "plant", "seed": "seeds", "seedling": "seedling", "stage": "growth stage"}
IMAGE_HOSTS = {"upload.wikimedia.org", "thumb.wikimedia.org"}
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
ALLOWED_LICENSE = re.compile(r"^(cc0|public domain|pd\b|cc[- ]by(-sa)?[- ][1-4]\.\d)", re.I)
MIN_DIM, MAX_DIM = 200, 8000
Image.MAX_IMAGE_PIXELS = 40_000_000


class ImageRejected(Exception):
    pass


def validate_image(data: bytes) -> np.ndarray:
    """Check format and dimensions; return BGR array."""
    try:
        with Image.open(io.BytesIO(data)) as im:
            if im.format not in ("JPEG", "PNG", "WEBP"):
                raise ImageRejected(f"Unsupported format {im.format}")
            w, h = im.size
            if not (MIN_DIM <= w <= MAX_DIM and MIN_DIM <= h <= MAX_DIM):
                raise ImageRejected(f"Image dimensions out of range: {w}x{h}")
            rgb = np.array(im.convert("RGB"))
    except ImageRejected:
        raise
    except Exception as e:
        raise ImageRejected(f"Unreadable image: {type(e).__name__}") from e
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def make_pencil_sketch(bgr: np.ndarray, max_side: int = 800) -> np.ndarray:
    """Monochrome pencil sketch on a white background (single-channel uint8)."""
    h, w = bgr.shape[:2]
    scale = max_side / max(h, w)
    if scale < 1:
        bgr = cv2.resize(bgr, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    gray_sketch, _ = cv2.pencilSketch(bgr, sigma_s=50, sigma_r=0.07, shade_factor=0.03)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(cv2.bitwise_not(gray), (21, 21), 0)
    dodge = cv2.divide(gray, 255 - blur, scale=256)  # classic dodge-blend line art
    edges = cv2.adaptiveThreshold(cv2.medianBlur(gray, 5), 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                  cv2.THRESH_BINARY, 9, 6)
    mix = cv2.addWeighted(gray_sketch, 0.5, dodge, 0.5, 0)
    mix = cv2.min(mix, edges)
    mix = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(mix)
    # push light tones to pure white for a paper look
    lut = np.clip((np.arange(256) - 20) * (255 / (225 - 20)), 0, 255).astype(np.uint8)
    return cv2.LUT(mix, lut)


def _clean_html(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def commons_license(file_title: str, client: httpx.Client | None = None) -> dict | None:
    """Look up a Wikimedia Commons file; return license/attribution info only for reusable licenses."""
    s = get_settings()
    own = client is None
    client = client or httpx.Client(timeout=s.http_timeout_seconds, headers={"User-Agent": safenet.USER_AGENT})
    try:
        r = client.get(COMMONS_API, params={
            "action": "query", "titles": file_title, "prop": "imageinfo", "format": "json",
            "iiprop": "url|extmetadata|size|mime", "iiurlwidth": 1000})
        r.raise_for_status()
        page = next(iter(r.json().get("query", {}).get("pages", {}).values()), {})
        info = (page.get("imageinfo") or [None])[0]
        if not info:
            return None
        meta = info.get("extmetadata", {})
        lic = _clean_html(meta.get("LicenseShortName", {}).get("value", ""))
        if not lic or not ALLOWED_LICENSE.match(lic):
            return None
        if info.get("mime") not in ("image/jpeg", "image/png", "image/webp"):
            return None
        artist = _clean_html(meta.get("Artist", {}).get("value", "")) or "Unknown author"
        return {
            "image_url": info.get("thumburl") or info.get("url"), "page_url": info.get("descriptionurl"),
            "license_name": lic, "license_url": _clean_html(meta.get("LicenseUrl", {}).get("value", "")) or None,
            "attribution": f"{artist}, {lic}, via Wikimedia Commons",
        }
    except (httpx.HTTPError, ValueError):
        return None
    finally:
        if own:
            client.close()


def _commons_title(result: dict) -> str | None:
    for key in ("link", "source", "imageUrl"):
        u = result.get(key) or ""
        m = re.search(r"commons\.wikimedia\.org/wiki/(File:[^?#]+)", u)
        if m:
            return unquote(m.group(1)).replace("_", " ")
        if "upload.wikimedia.org" in u:
            name = unquote(urlparse(u).path.rsplit("/", 1)[-1])
            name = re.sub(r"^\d+px-", "", name)
            if name:
                return "File:" + name.replace("_", " ")
    return None


def _placeholder(db: Session, crop: Crop, kind: str, reason: str) -> Sketch:
    sk = db.scalar(select(Sketch).where(Sketch.crop_id == crop.id, Sketch.kind == kind))
    if sk is None:
        sk = Sketch(crop_id=crop.id, kind=kind)
        db.add(sk)
    sk.status, sk.reason, sk.updated_at = "placeholder", reason, utcnow()
    db.commit()
    return sk


def generate_sketch(db: Session, crop: Crop, kind: str, *, serper, fetch=None, license_lookup=None,
                    job_id: str | None = None) -> Sketch:
    """Full workflow (cache check happens in the caller). Falls back to a placeholder."""
    fetch = fetch or (lambda url: safenet.safe_get(
        url, content_types=("image/jpeg", "image/png", "image/webp"), allowed_hosts=IMAGE_HOSTS)[0])
    license_lookup = license_lookup or commons_license
    query = f"{crop.name_en} {crop.scientific_name or ''} {KIND_QUERY.get(kind, '')} site:commons.wikimedia.org".split()
    costcontrol.ensure_budget(db, "serper")
    results = serper.images(" ".join(query), num=10)
    costcontrol.record_usage(db, "serper", "images", job_id=job_id)

    licensed = None
    for res in results[:6]:
        title = _commons_title(res)
        if not title:
            continue
        licensed = license_lookup(title)
        if licensed:
            break
    if not licensed:
        return _placeholder(db, crop, kind, "No image with a verifiable reuse license was found")
    try:
        data = fetch(licensed["image_url"])
        bgr = validate_image(data)
    except (safenet.UnsafeURL, safenet.FetchError, ImageRejected) as e:
        return _placeholder(db, crop, kind, f"Image rejected: {str(e)[:120]}")

    out = make_pencil_sketch(bgr)
    media = Path(get_settings().media_dir) / "sketches"
    media.mkdir(parents=True, exist_ok=True)
    fname = f"{crop.slug}-{kind}.png"
    ok, buf = cv2.imencode(".png", out)
    if not ok:
        return _placeholder(db, crop, kind, "Sketch encoding failed")
    (media / fname).write_bytes(buf.tobytes())

    sk = db.scalar(select(Sketch).where(Sketch.crop_id == crop.id, Sketch.kind == kind))
    if sk is None:
        sk = Sketch(crop_id=crop.id, kind=kind)
        db.add(sk)
    sk.status, sk.file_path, sk.reason = "generated", f"sketches/{fname}", None
    sk.source_image_url, sk.source_page_url = licensed["image_url"], licensed["page_url"]
    sk.license_name, sk.license_url, sk.attribution = (
        licensed["license_name"], licensed["license_url"], licensed["attribution"])
    sk.updated_at = utcnow()
    db.commit()
    return sk


def run_sketch_job(db: Session, job: ResearchJob, *, serper=None, **_) -> None:
    from app.services import providers
    crop = db.get(Crop, job.crop_id)
    kind = job.dedupe_key.rsplit(":", 1)[-1]
    sk = generate_sketch(db, crop, kind, serper=serper or providers.get_serper(), job_id=job.id)
    job.status = "completed" if sk.status == "generated" else "insufficient"
    job.result = {"sketch_status": sk.status, "reason": sk.reason}
    job.finished_at = utcnow()


def sketch_to_dict(sk: Sketch | None, crop: Crop, kind: str) -> dict:
    if sk is None or sk.status != "generated":
        return {"crop_id": crop.id, "kind": kind, "status": "placeholder", "image_url": None,
                "reason": sk.reason if sk else "Sketch not generated yet", "attribution": None,
                "license_name": None, "license_url": None, "source_page_url": None}
    return {"crop_id": crop.id, "kind": kind, "status": "generated", "image_url": f"/media/{sk.file_path}",
            "reason": None, "attribution": sk.attribution, "license_name": sk.license_name,
            "license_url": sk.license_url, "source_page_url": sk.source_page_url}
