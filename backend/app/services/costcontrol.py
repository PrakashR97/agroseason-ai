"""Daily request limits, monthly budget tracking and token usage logging."""
from __future__ import annotations

import datetime as dt

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import ApiUsageLog, utcnow

# Approximate prices (USD) used for budget tracking only.
OPENAI_IN_PER_TOKEN = 0.15 / 1_000_000
OPENAI_OUT_PER_TOKEN = 0.60 / 1_000_000
SERPER_PER_REQUEST = 0.001


class BudgetExhausted(Exception):
    pass


def _daily_limit(provider: str) -> int:
    s = get_settings()
    return s.serper_daily_limit if provider == "serper" else s.openai_daily_limit


def requests_today(db: Session, provider: str) -> int:
    return db.scalar(select(func.count()).select_from(ApiUsageLog).where(
        ApiUsageLog.provider == provider, ApiUsageLog.day == utcnow().date())) or 0


def spend_this_month(db: Session) -> float:
    first = utcnow().date().replace(day=1)
    return float(db.scalar(select(func.coalesce(func.sum(ApiUsageLog.cost_usd), 0.0)).where(
        ApiUsageLog.day >= first)) or 0.0)


def ensure_budget(db: Session, provider: str) -> None:
    if requests_today(db, provider) >= _daily_limit(provider):
        raise BudgetExhausted(f"Daily {provider} request limit reached")
    if spend_this_month(db) >= get_settings().monthly_budget_usd:
        raise BudgetExhausted("Monthly API budget reached")


def record_usage(db: Session, provider: str, endpoint: str, tokens_in: int = 0, tokens_out: int = 0,
                 job_id: str | None = None) -> None:
    cost = SERPER_PER_REQUEST if provider == "serper" else (
        tokens_in * OPENAI_IN_PER_TOKEN + tokens_out * OPENAI_OUT_PER_TOKEN)
    db.add(ApiUsageLog(provider=provider, endpoint=endpoint, tokens_in=tokens_in, tokens_out=tokens_out,
                       cost_usd=cost, job_id=job_id))
    db.commit()


def usage_summary(db: Session) -> dict:
    s = get_settings()
    return {
        "serper_today": requests_today(db, "serper"), "serper_daily_limit": s.serper_daily_limit,
        "openai_today": requests_today(db, "openai"), "openai_daily_limit": s.openai_daily_limit,
        "month_spend_usd": round(spend_this_month(db), 4), "monthly_budget_usd": s.monthly_budget_usd,
        "serper_configured": bool(s.serper_api_key), "openai_configured": bool(s.openai_api_key),
    }
