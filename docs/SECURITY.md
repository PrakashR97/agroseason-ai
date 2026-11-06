# Security
- Secrets only via environment; `.env` is git-ignored; no keys in the frontend; `SecretStr`-style repr hiding and log redaction filter (`sk-…`, `X-API-KEY`, bearer, `password=`).
- SQL injection: SQLAlchemy parameters; LIKE wildcards escaped. Tested.
- SSRF: only http/https, ports 80/443, hostname resolved and rejected if private/loopback/link-local/reserved; every redirect hop re-validated; host allow-list for images. Known limit: DNS-rebinding between check and connect is not pinned.
- Downloads: streaming size caps, content-type allow-list, timeouts.
- CORS restricted to `CORS_ORIGINS`; nginx CSP, nosniff, frame deny; API security headers.
- Rate limits per IP (Redis fixed window, in-memory fallback). Behind Traefik the **last** X-Forwarded-For entry is used (first is client-spoofable).
- Containers: non-root (api/worker uid 10001, nginx-unprivileged); PostgreSQL/Redis on an `internal: true` network, no published ports; Redis password required.
- LLM prompt injection: page text is untrusted; output only accepted if the quote exists in the page and passes validation.
- Never commit SSH keys; deployments use your own SSH agent.
