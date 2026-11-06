from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import (
    JSON, Boolean, Date, DateTime, Float, ForeignKey, Index, Integer, String, Text,
    UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

JsonType = JSON().with_variant(JSONB(), "postgresql")

# verification_status values
VERIFIED = "verified"
REVIEW_REQUIRED = "review_required"
UNVERIFIED = "unverified"
VERIFICATION_STATUSES = (VERIFIED, REVIEW_REQUIRED, UNVERIFIED)


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


class TimestampMixin:
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow, server_default=func.now())
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, server_default=func.now()
    )


class District(Base, TimestampMixin):
    __tablename__ = "districts"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True)
    name_en: Mapped[str] = mapped_column(String(100), unique=True)
    name_ta: Mapped[str] = mapped_column(String(100))
    region: Mapped[str] = mapped_column(String(50))


class CropCategory(Base, TimestampMixin):
    __tablename__ = "crop_categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True)
    name_en: Mapped[str] = mapped_column(String(100))
    name_ta: Mapped[str] = mapped_column(String(100))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)


class Crop(Base, TimestampMixin):
    __tablename__ = "crops"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("crop_categories.id"), index=True)
    name_en: Mapped[str] = mapped_column(String(120))
    name_ta: Mapped[str] = mapped_column(String(120))
    scientific_name: Mapped[str | None] = mapped_column(String(160))
    # annual | short_duration | repeated_harvest | perennial | plantation
    crop_type: Mapped[str] = mapped_column(String(32), default="annual")
    description_en: Mapped[str | None] = mapped_column(Text)
    description_ta: Mapped[str | None] = mapped_column(Text)
    verification_status: Mapped[str] = mapped_column(String(20), default=UNVERIFIED)

    category: Mapped[CropCategory] = relationship()
    aliases: Mapped[list[CropAlias]] = relationship(back_populates="crop", cascade="all, delete-orphan")
    varieties: Mapped[list[CropVariety]] = relationship(back_populates="crop", cascade="all, delete-orphan")

    __table_args__ = (Index("ix_crops_name_en_lower", func.lower(name_en)),)


class CropAlias(Base):
    __tablename__ = "crop_aliases"
    id: Mapped[int] = mapped_column(primary_key=True)
    crop_id: Mapped[int] = mapped_column(ForeignKey("crops.id", ondelete="CASCADE"))
    alias: Mapped[str] = mapped_column(String(160))
    alias_norm: Mapped[str] = mapped_column(String(160))
    alias_skel: Mapped[str] = mapped_column(String(160))
    lang: Mapped[str] = mapped_column(String(10))  # en | ta | tanglish

    crop: Mapped[Crop] = relationship(back_populates="aliases")
    __table_args__ = (
        UniqueConstraint("crop_id", "alias_norm", name="uq_crop_alias_norm"),
        Index("ix_crop_aliases_norm", "alias_norm"),
        Index("ix_crop_aliases_skel", "alias_skel"),
    )


class ResearchSource(Base, TimestampMixin):
    __tablename__ = "research_sources"
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(1000), unique=True)
    title: Mapped[str] = mapped_column(String(500))
    publisher: Mapped[str | None] = mapped_column(String(200))
    domain: Mapped[str] = mapped_column(String(200), index=True)
    is_trusted: Mapped[bool] = mapped_column(Boolean, default=False)
    retrieved_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    content_hash: Mapped[str | None] = mapped_column(String(64))


class CropVariety(Base, TimestampMixin):
    __tablename__ = "crop_varieties"
    id: Mapped[int] = mapped_column(primary_key=True)
    crop_id: Mapped[int] = mapped_column(ForeignKey("crops.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    notes: Mapped[str | None] = mapped_column(Text)
    verification_status: Mapped[str] = mapped_column(String(20), default=UNVERIFIED)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("research_sources.id"))

    crop: Mapped[Crop] = relationship(back_populates="varieties")
    __table_args__ = (UniqueConstraint("crop_id", "name", name="uq_variety_crop_name"),)


class CropDistrictSeason(Base, TimestampMixin):
    """A documented season. district_id NULL means state-level (Tamil Nadu wide)."""

    __tablename__ = "crop_district_seasons"
    id: Mapped[int] = mapped_column(primary_key=True)
    crop_id: Mapped[int] = mapped_column(ForeignKey("crops.id", ondelete="CASCADE"), index=True)
    district_id: Mapped[int | None] = mapped_column(ForeignKey("districts.id"), index=True)
    variety_id: Mapped[int | None] = mapped_column(ForeignKey("crop_varieties.id"))
    season_name: Mapped[str] = mapped_column(String(80))
    irrigation: Mapped[str] = mapped_column(String(20), default="any")  # any | irrigated | rainfed
    sow_start_month: Mapped[int | None] = mapped_column(Integer)
    sow_end_month: Mapped[int | None] = mapped_column(Integer)
    nursery_start_month: Mapped[int | None] = mapped_column(Integer)
    nursery_end_month: Mapped[int | None] = mapped_column(Integer)
    transplant_start_month: Mapped[int | None] = mapped_column(Integer)
    transplant_end_month: Mapped[int | None] = mapped_column(Integer)
    harvest_start_month: Mapped[int | None] = mapped_column(Integer)
    harvest_end_month: Mapped[int | None] = mapped_column(Integer)
    duration_days_min: Mapped[int | None] = mapped_column(Integer)
    duration_days_max: Mapped[int | None] = mapped_column(Integer)
    repeated_harvest: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text)
    verification_status: Mapped[str] = mapped_column(String(20), default=UNVERIFIED)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("research_sources.id"))

    __table_args__ = (
        Index("ix_cds_crop_district", "crop_id", "district_id"),
        UniqueConstraint(
            "crop_id", "district_id", "season_name", "irrigation", "variety_id", name="uq_season_scope",
            postgresql_nulls_not_distinct=True,
        ),
    )


class CultivationGuide(Base, TimestampMixin):
    """sections: {section_key: {value, status, source_ids, note}}; district_id NULL = state level."""

    __tablename__ = "cultivation_guides"
    id: Mapped[int] = mapped_column(primary_key=True)
    crop_id: Mapped[int] = mapped_column(ForeignKey("crops.id", ondelete="CASCADE"), index=True)
    district_id: Mapped[int | None] = mapped_column(ForeignKey("districts.id"))
    sections: Mapped[dict] = mapped_column(JsonType, default=dict)
    verification_status: Mapped[str] = mapped_column(String(20), default=UNVERIFIED)

    __table_args__ = (
        UniqueConstraint("crop_id", "district_id", name="uq_guide_scope", postgresql_nulls_not_distinct=True),
    )


class ResearchEvidence(Base):
    __tablename__ = "research_evidence"
    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("research_sources.id", ondelete="CASCADE"), index=True)
    crop_id: Mapped[int] = mapped_column(ForeignKey("crops.id", ondelete="CASCADE"), index=True)
    district_id: Mapped[int | None] = mapped_column(ForeignKey("districts.id"))
    job_id: Mapped[str | None] = mapped_column(String(36), index=True)
    field_key: Mapped[str] = mapped_column(String(64))
    extracted_value: Mapped[str] = mapped_column(Text)
    evidence_quote: Mapped[str] = mapped_column(Text)
    applicability: Mapped[dict] = mapped_column(JsonType, default=dict)
    quote_validated: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20), default=REVIEW_REQUIRED)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class FarmingDiagram(Base, TimestampMixin):
    __tablename__ = "farming_diagrams"
    id: Mapped[int] = mapped_column(primary_key=True)
    crop_id: Mapped[int] = mapped_column(ForeignKey("crops.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(40))  # spacing | seed_depth ...
    title: Mapped[str] = mapped_column(String(200))
    spec: Mapped[dict] = mapped_column(JsonType, default=dict)
    verification_status: Mapped[str] = mapped_column(String(20), default=UNVERIFIED)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("research_sources.id"))


class ResearchJob(Base, TimestampMixin):
    __tablename__ = "research_jobs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    kind: Mapped[str] = mapped_column(String(20), default="research")  # research | sketch
    crop_id: Mapped[int | None] = mapped_column(ForeignKey("crops.id"), index=True)
    district_id: Mapped[int | None] = mapped_column(ForeignKey("districts.id"))
    month: Mapped[int | None] = mapped_column(Integer)
    dedupe_key: Mapped[str] = mapped_column(String(200), index=True)
    status: Mapped[str] = mapped_column(String(20), default="queued", index=True)
    # queued | running | completed | review_required | insufficient | failed | budget_exhausted
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(Text)
    result: Mapped[dict] = mapped_column(JsonType, default=dict)
    finished_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True))


class ResearchCache(Base):
    __tablename__ = "research_cache"
    id: Mapped[int] = mapped_column(primary_key=True)
    cache_key: Mapped[str] = mapped_column(String(200), unique=True)
    payload: Mapped[dict] = mapped_column(JsonType, default=dict)
    status: Mapped[str] = mapped_column(String(20))
    expires_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Sketch(Base, TimestampMixin):
    __tablename__ = "sketches"
    id: Mapped[int] = mapped_column(primary_key=True)
    crop_id: Mapped[int] = mapped_column(ForeignKey("crops.id", ondelete="CASCADE"))
    kind: Mapped[str] = mapped_column(String(20), default="produce")  # produce|plant|seed|seedling|stage
    status: Mapped[str] = mapped_column(String(20), default="placeholder")  # generated|placeholder
    file_path: Mapped[str | None] = mapped_column(String(300))
    source_image_url: Mapped[str | None] = mapped_column(String(1000))
    source_page_url: Mapped[str | None] = mapped_column(String(1000))
    license_name: Mapped[str | None] = mapped_column(String(100))
    license_url: Mapped[str | None] = mapped_column(String(1000))
    attribution: Mapped[str | None] = mapped_column(Text)
    reason: Mapped[str | None] = mapped_column(String(200))
    __table_args__ = (UniqueConstraint("crop_id", "kind", name="uq_sketch_crop_kind"),)


class ApiUsageLog(Base):
    __tablename__ = "api_usage_log"
    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[str] = mapped_column(String(20), index=True)  # serper | openai
    day: Mapped[dt.date] = mapped_column(Date, index=True, default=lambda: utcnow().date())
    endpoint: Mapped[str] = mapped_column(String(60), default="")
    tokens_in: Mapped[int] = mapped_column(Integer, default=0)
    tokens_out: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    job_id: Mapped[str | None] = mapped_column(String(36))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
