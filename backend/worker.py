"""Background worker: python worker.py. Redis wakes it; DB rows are authoritative."""
import logging
import time

import redis

from app import queue
from app.config import get_settings
from app.db import session_factory
from app.models import ResearchJob, utcnow
from app.services.research import process_job
from sqlalchemy import select
import datetime as dt

log = logging.getLogger("agro.worker")


def requeue_pending() -> int:
    """Recover jobs left queued (Redis outage) or stuck running (worker crash)."""
    with session_factory()() as db:
        cutoff = utcnow() - dt.timedelta(minutes=10)
        for j in db.scalars(select(ResearchJob).where(
                ResearchJob.status == "running", ResearchJob.updated_at < cutoff)):
            j.status = "queued"
        db.commit()
        ids = list(db.scalars(select(ResearchJob.id).where(ResearchJob.status == "queued")))
        for i in ids:
            queue.enqueue(i)
        return len(ids)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    log.info("worker starting; recovered %d pending jobs", _safe_requeue())
    blocking = queue._client(blocking=True)
    while True:
        try:
            item = blocking.blpop(queue.QUEUE_KEY, timeout=15)
            if item is None:
                _safe_requeue()  # periodic DB sweep
                continue
            job_id = item[1].decode()
            with session_factory()() as db:
                job = process_job(db, job_id)
                log.info("job %s -> %s", job_id, job.status if job else "missing")
                if job and job.status == "queued":  # retry with exponential backoff
                    time.sleep(min(2 ** job.attempts, 30))
                    queue.enqueue(job_id)
        except redis.RedisError:
            log.warning("redis unavailable, retrying in 5s")
            time.sleep(5)
        except Exception:
            log.exception("worker loop error")
            time.sleep(2)


def _safe_requeue() -> int:
    try:
        return requeue_pending()
    except Exception:
        log.exception("requeue failed")
        return 0


if __name__ == "__main__":
    main()
