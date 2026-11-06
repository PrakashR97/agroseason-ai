import pytest

from app.services import safenet
from app.services.ratelimit import limiter


@pytest.mark.parametrize("url", [
    "http://127.0.0.1/", "http://localhost/x", "http://169.254.169.254/latest/meta-data",
    "http://10.0.0.5/", "http://192.168.1.1/", "http://[::1]/", "file:///etc/passwd", "ftp://example.com/",
    "http://user:pw@example.com/", "https://example.com:8443/", "http://0.0.0.0/",
])
def test_ssrf_blocked(url):
    with pytest.raises(safenet.UnsafeURL):
        safenet.validate_public_url(url)


def test_host_allowlist():
    with pytest.raises(safenet.UnsafeURL):
        safenet.validate_public_url("https://example.com/a.jpg", allowed_hosts={"upload.wikimedia.org"})


def test_redirect_to_private_is_blocked(monkeypatch):
    import httpx
    monkeypatch.setattr(safenet, "validate_public_url", lambda u, a=None: (_ for _ in ()).throw(safenet.UnsafeURL("x")) if "127.0.0.1" in u else u)
    transport = httpx.MockTransport(lambda r: httpx.Response(302, headers={"location": "http://127.0.0.1/admin"}))
    with pytest.raises(safenet.UnsafeURL):
        safenet.safe_get("https://example.com/", client=httpx.Client(transport=transport))


def test_size_limit(monkeypatch):
    import httpx
    monkeypatch.setattr(safenet, "validate_public_url", lambda u, a=None: u)
    transport = httpx.MockTransport(lambda r: httpx.Response(200, content=b"x" * 5000, headers={"content-type": "image/png"}))
    with pytest.raises(safenet.FetchError):
        safenet.safe_get("https://example.com/", max_bytes=1000, client=httpx.Client(transport=transport))
    with pytest.raises(safenet.FetchError):
        safenet.safe_get("https://example.com/", content_types=("image/jpeg",), client=httpx.Client(transport=transport))


def test_rate_limit_per_ip(client, monkeypatch):
    from app.config import get_settings
    monkeypatch.setattr(get_settings(), "rate_limit_per_minute", 3)
    limiter.reset()
    codes = [client.get("/api/districts").status_code for _ in range(5)]
    assert codes[:3] == [200] * 3 and codes[3:] == [429, 429]
    assert "retry-after" in client.get("/api/districts").headers
    limiter.reset()


def test_research_rate_limit(client, monkeypatch):
    from app.config import get_settings
    monkeypatch.setattr(get_settings(), "research_rate_limit_per_hour", 2)
    monkeypatch.setattr("app.queue.enqueue", lambda i: True)
    limiter.reset()
    codes = [client.post("/api/research", json={"crop": c}).status_code for c in ("tomato", "okra", "paddy")]
    assert codes == [200, 200, 429]
    limiter.reset()


def test_sql_injection_params(client):
    r = client.get("/api/crops/search", params={"q": "' OR 1=1; --"})
    assert r.status_code == 200 and r.json() == []
    assert client.get("/api/crops", params={"category": "x' OR '1'='1"}).json()["total"] == 0
    assert client.get("/api/districts").status_code == 200  # tables intact


def test_cors_and_headers(client):
    r = client.get("/health", headers={"Origin": "http://evil.example"})
    assert "access-control-allow-origin" not in r.headers
    r = client.get("/health", headers={"Origin": "http://localhost:5173"})
    assert r.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert r.headers["x-content-type-options"] == "nosniff"


def test_secrets_not_in_repr_or_logs():
    from app.config import Settings
    from app.main import SECRET_PATTERN
    s = Settings(openai_api_key="sk-supersecret123456", serper_api_key="serperkey123")
    assert "supersecret" not in repr(s) and "serperkey123" not in repr(s)
    assert "[REDACTED]" in SECRET_PATTERN.sub("[REDACTED]", "key sk-supersecret123456 used")


def test_no_stack_trace_leak(client, monkeypatch):
    from fastapi.testclient import TestClient
    from app.main import create_app
    app = create_app()

    @app.get("/boom")
    def boom(): raise RuntimeError("secret internals")
    r = TestClient(app, raise_server_exceptions=False).get("/boom")
    assert r.status_code == 500 and "secret" not in r.text
