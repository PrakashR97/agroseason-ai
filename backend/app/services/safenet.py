"""SSRF-safe HTTP fetching with size/time limits."""
from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urljoin, urlparse

import httpx

from app.config import get_settings


# Wikimedia and many institutions reject requests without a descriptive User-Agent.
USER_AGENT = "AgroSeasonAI/1.0 (+https://github.com/PrakashR97/agroseason-ai; agricultural research bot)"


class UnsafeURL(Exception):
    pass


class FetchError(Exception):
    pass


def validate_public_url(url: str, allowed_hosts: set[str] | None = None) -> str:
    p = urlparse(url)
    if p.scheme not in ("http", "https"):
        raise UnsafeURL("Only http/https URLs are allowed")
    if not p.hostname or p.username or p.password:
        raise UnsafeURL("Invalid URL")
    if p.port not in (None, 80, 443):
        raise UnsafeURL("Port not allowed")
    host = p.hostname.lower()
    if allowed_hosts is not None and host not in allowed_hosts and not any(host.endswith("." + h) for h in allowed_hosts):
        raise UnsafeURL("Host not allowed")
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as e:
        raise UnsafeURL("Host does not resolve") from e
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved
                or ip.is_multicast or ip.is_unspecified):
            raise UnsafeURL("Address not allowed")
    return url


def safe_get(url: str, *, max_bytes: int | None = None, content_types: tuple[str, ...] = (),
             allowed_hosts: set[str] | None = None, max_redirects: int = 3,
             client: httpx.Client | None = None) -> tuple[bytes, str]:
    """Fetch with per-hop validation, streaming size cap. Returns (body, content_type)."""
    s = get_settings()
    cap = max_bytes or s.max_download_bytes
    own = client is None
    client = client or httpx.Client(timeout=s.http_timeout_seconds, follow_redirects=False,
                                    headers={"User-Agent": USER_AGENT})
    try:
        for _ in range(max_redirects + 1):
            validate_public_url(url, allowed_hosts)
            with client.stream("GET", url) as r:
                if r.status_code in (301, 302, 303, 307, 308) and r.headers.get("location"):
                    url = urljoin(url, r.headers["location"])
                    continue
                if r.status_code != 200:
                    raise FetchError(f"HTTP {r.status_code}")
                ctype = r.headers.get("content-type", "").split(";")[0].strip().lower()
                if content_types and ctype not in content_types:
                    raise FetchError(f"Unsupported content type: {ctype}")
                if int(r.headers.get("content-length", 0) or 0) > cap:
                    raise FetchError("Response too large")
                buf = bytearray()
                for chunk in r.iter_bytes():
                    buf.extend(chunk)
                    if len(buf) > cap:
                        raise FetchError("Response too large")
                return bytes(buf), ctype
        raise FetchError("Too many redirects")
    except httpx.HTTPError as e:
        raise FetchError(str(e)) from e
    finally:
        if own:
            client.close()
