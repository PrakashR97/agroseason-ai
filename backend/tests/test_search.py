import pytest

from app.services.search import resolve_crop, resolve_district, search_crops
from app.services.textnorm import normalize, skeleton


def top(db, q):
    r = search_crops(db, q, 3)
    return r[0][0].slug if r else None


@pytest.mark.parametrize("q,slug", [
    ("Tomato", "tomato"), ("tomato", "tomato"), ("TOMATO", "tomato"), ("  tomato  ", "tomato"),
    ("தக்காளி", "tomato"), ("Thakkali", "tomato"), ("takkali", "tomato"), ("thakali", "tomato"),
    ("lady's finger", "okra"), ("Ladys Finger", "okra"), ("vendakkai", "okra"), ("வெண்டைக்காய்", "okra"),
    ("நெல்", "paddy"), ("rice", "paddy"), ("ragi", "finger-millet"), ("கேழ்வரகு", "finger-millet"),
    ("pumpkin", "pumpkin"), ("poosanikai", "pumpkin"), ("brinjal", "brinjal"), ("kathirikai", "brinjal"),
    ("tomatto", "tomato"),
])
def test_multilingual_lookup(db, q, slug):
    assert top(db, q) == slug


def test_prefix_suggestions(db):
    slugs = [c.slug for c, _, _ in search_crops(db, "toma", 5)]
    assert "tomato" in slugs


def test_no_match_and_empty(db):
    assert search_crops(db, "zzzzqqq", 5) == []
    assert search_crops(db, "   ", 5) == []


def test_sql_wildcards_are_escaped(db):
    assert search_crops(db, "%", 5) == []
    assert search_crops(db, "'; drop table crops; --", 5) == []


def test_resolve_crop_threshold(db):
    assert resolve_crop(db, "Thakkali").slug == "tomato"
    assert resolve_crop(db, "xyzxyz") is None


def test_districts(db):
    assert resolve_district(db, "Salem").slug == "salem"
    assert resolve_district(db, "சேலம்").slug == "salem"
    assert resolve_district(db, "Trichy").slug == "tiruchirappalli"
    assert resolve_district(db, "Namakkal").slug == "namakkal"
    assert resolve_district(db, "Atlantis") is None


def test_normalization():
    assert normalize("Lady’s  Finger") == "ladys finger"
    assert skeleton("Thakkali") == skeleton("takkali")
