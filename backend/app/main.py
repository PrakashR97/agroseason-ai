from __future__ import annotations

import logging
import re
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app import queue
from app.api.routes import router
from app.config import get_settings
from app.db import get_engine

SECRET_PATTERN = re.compile(r"(sk-[A-Za-z0-9_\-]{8,}|X-API-KEY[=: ]+\S+|Bearer\s+\S+|password=\S+)", re.I)


class RedactFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = SECRET_PATTERN.sub("[REDACTED]", str(record.getMessage()))
        record.args = ()
        return True


def create_app() -> FastAPI:
    s = get_settings()
    for h in logging.getLogger().handlers:
        h.addFilter(RedactFilter())
    logging.getLogger("uvicorn.error").addFilter(RedactFilter())
    logging.getLogger("httpx").setLevel(logging.WARNING)  # httpx logs full URLs

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        s.media_dir.mkdir(parents=True, exist_ok=True)
        yield

    app = FastAPI(title="AgroSeason AI API", version="1.0.0", lifespan=lifespan,
                  description="Tamil Nadu crop seasons, cultivation guides and evidence-backed research.")
    app.add_middleware(CORSMiddleware, allow_origins=s.cors_origin_list, allow_methods=["GET", "POST"],
                       allow_headers=["Content-Type"], allow_credentials=False)

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        resp = await call_next(request)
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("Referrer-Policy", "no-referrer")
        return resp

    @app.exception_handler(RequestValidationError)
    async def validation_handler(_: Request, exc: RequestValidationError):
        errs = [{"field": ".".join(str(p) for p in e["loc"][1:]), "message": e["msg"]} for e in exc.errors()]
        return JSONResponse(status_code=422, content={"detail": "Validation failed", "errors": errs})

    @app.exception_handler(Exception)
    async def unhandled(_: Request, exc: Exception):
        logging.getLogger("agro").exception("Unhandled error")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    @app.get("/health", tags=["ops"])
    def health():
        db_ok = True
        try:
            with get_engine().connect() as c:
                c.execute(text("select 1"))
        except Exception:
            db_ok = False
        redis_ok = queue.ping()
        body = {"status": "ok" if db_ok else "degraded", "database": db_ok, "redis": redis_ok}
        return JSONResponse(body, status_code=200 if db_ok else 503)

    app.include_router(router)
    s.media_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/media", StaticFiles(directory=s.media_dir), name="media")
    return app


app = create_app()
