"""Redis-backed job queue. DB rows are the source of truth; Redis only wakes the worker."""
from __future__ import annotations

import logging

import redis

from app.config import get_settings

log = logging.getLogger("agro.queue")
QUEUE_KEY = "agro:jobs"


def _client(blocking: bool = False) -> redis.Redis:
    # blocking clients (worker BLPOP) need a read timeout longer than the BLPOP timeout
    return redis.Redis.from_url(get_settings().redis_url, socket_timeout=40 if blocking else 2,
                                socket_connect_timeout=2)


def enqueue(job_id: str) -> bool:
    if not get_settings().redis_url:
        return False
    try:
        _client().rpush(QUEUE_KEY, job_id)
        return True
    except redis.RedisError:
        log.warning("Redis unavailable; job %s stays queued in the database", job_id)
        return False


def ping() -> bool:
    try:
        return bool(_client().ping())
    except Exception:
        return False
