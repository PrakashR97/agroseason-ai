from __future__ import annotations

import datetime as dt
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class DistrictOut(ORM):
    id: int
    slug: str
    name_en: str
    name_ta: str
    region: str


class CategoryOut(ORM):
    id: int
    slug: str
    name_en: str
    name_ta: str


class VarietyOut(ORM):
    id: int
    name: str
    notes: str | None
    verification_status: str


class CropOut(ORM):
    id: int
    slug: str
    name_en: str
    name_ta: str
    scientific_name: str | None
    crop_type: str
    verification_status: str
    category: CategoryOut


class CropDetail(CropOut):
    description_en: str | None
    description_ta: str | None
    aliases: list[str]
    varieties: list[VarietyOut]
    season_records: int
    verified_season_records: int


class CropSearchHit(BaseModel):
    crop: CropOut
    score: float
    matched_alias: str
    month_suitability: str | None = None


class CropInDistrict(BaseModel):
    crop: CropOut
    scope: str  # district | state
    verification_status: str
    seasons: list[str]
    month_suitability: str | None = None


class DistrictForCrop(BaseModel):
    district: DistrictOut
    verification_status: str
    seasons: list[str]


class ResearchRequest(BaseModel):
    crop: str = Field(min_length=1, max_length=120)
    district: str | None = Field(default=None, max_length=80)
    month: int | None = Field(default=None, ge=1, le=12)


class JobOut(ORM):
    id: str
    kind: str
    crop_id: int | None
    district_id: int | None
    month: int | None
    status: str
    attempts: int
    error: str | None
    result: dict
    created_at: dt.datetime
    updated_at: dt.datetime
    finished_at: dt.datetime | None


class ResearchResponse(BaseModel):
    state: str  # cached | queued | existing_job | budget_exhausted
    reason: str | None = None
    job: JobOut | None = None
    summary: dict | None = None
    cache: dict | None = None
    message: str | None = None
