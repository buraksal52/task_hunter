from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.collection.ingest import ingest_raw_jobs, purge_expired_jobs
from app.collection.retry import fetch_with_retry
from app.db.models import CollectionRun, Source
from app.sources.himalayas import HimalayasAdapter
from app.sources.jobicy import JobicyAdapter

ADAPTER_FACTORIES = {
    "jobicy": JobicyAdapter,
    "himalayas": HimalayasAdapter,
}


async def collect_source(
    session: Session,
    source: Source,
    now: datetime | None = None,
    limit: int = 100,
    alert_chat_id: int | None = None,
) -> CollectionRun:
    now = now or datetime.now(UTC)
    run = CollectionRun(source_id=source.id, status="running", started_at=now)
    session.add(run)
    session.flush()
    factory = ADAPTER_FACTORIES.get(source.source_key)
    if not source.enabled or source.policy_status != "approved" or factory is None:
        run.status = "skipped"
        run.finished_at = now
        run.error_code = "SOURCE_DISABLED"
        session.commit()
        return run
    adapter = factory()
    if not adapter.enabled:
        run.status = "skipped"
        run.finished_at = now
        run.error_code = "ADAPTER_DISABLED"
        session.commit()
        return run
    try:
        raw_jobs = await fetch_with_retry(
            lambda: adapter.fetch_jobs(source.last_success_at, limit),
            max_attempts=3,
        )
        run.fetched_count = len(raw_jobs)
        created, updated, skipped = ingest_raw_jobs(
            session, source, raw_jobs, now, alert_chat_id=alert_chat_id
        )
        run.new_count = created
        run.updated_count = updated
        run.skipped_count = skipped
        source.last_success_at = now
        purge_expired_jobs(session, source, now)
        run.status = "succeeded"
    except Exception as error:
        run.status = "failed"
        run.error_code = type(error).__name__
        run.error_message = str(error)[:500]
    run.finished_at = now
    session.commit()
    return run
