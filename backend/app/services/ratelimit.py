from __future__ import annotations

import threading
import time

from fastapi import HTTPException, Request

from app.config import get_settings


class RateLimiter:
    """Fixed-window per-key limiter. Redis when available, in-process fallback."""

    def __init__(self) -> None:
        self._mem: dict[str, tuple[float, int]] = {}
        self._lock = threading.Lock()
        self._redis = None
        self._redis_url: str | None = None

    def _client(self):
        url = get_settings().redis_url
        if not url:
            return None
        if self._redis is None or self._redis_url != url:
            import redis
            self._redis = redis.Redis.from_url(url, socket_timeout=0.5, socket_connect_timeout=0.5)
            self._redis_url = url
        return self._redis

    def hit(self, key: str, limit: int, window: int) -> tuple[bool, int]:
        """Returns (allowed, retry_after_seconds)."""
        try:
            r = self._client()
            if r is not None:
                bucket = int(time.time() // window)
                k = f"rl:{key}:{bucket}"
                pipe = r.pipeline()
                pipe.incr(k)
                pipe.expire(k, window + 1)
                count = pipe.execute()[0]
                return count <= limit, window - int(time.time() % window)
        except Exception:  # redis down -> fall back to memory
            pass
        now = time.time()
        with self._lock:
            start, count = self._mem.get(key, (now, 0))
            if now - start >= window:
                start, count = now, 0
            count += 1
            self._mem[key] = (start, count)
            if len(self._mem) > 10000:
                self._mem = {k: v for k, v in self._mem.items() if now - v[0] < window}
            return count <= limit, max(1, int(window - (now - start)))

    def reset(self) -> None:
        with self._lock:
            self._mem.clear()


limiter = RateLimiter()


def client_ip(request: Request) -> str:
    if get_settings().trust_proxy_headers:
        xff = request.headers.get("x-forwarded-for")
        if xff:
            # Traefik appends the real peer address last; earlier entries are client-supplied (spoofable)
            return xff.split(",")[-1].strip()
    return request.client.host if request.client else "unknown"


def _enforce(request: Request, scope: str, limit: int, window: int) -> None:
    ok, retry = limiter.hit(f"{scope}:{client_ip(request)}", limit, window)
    if not ok:
        raise HTTPException(429, "Rate limit exceeded. Please try again later.",
                            headers={"Retry-After": str(retry)})


def general_limit(request: Request) -> None:
    _enforce(request, "api", get_settings().rate_limit_per_minute, 60)


def research_limit(request: Request) -> None:
    _enforce(request, "research", get_settings().research_rate_limit_per_hour, 3600)
