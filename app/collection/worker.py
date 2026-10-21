from sqlalchemy.orm import Session

from app.collection.queue import claim_task, skip_unconfigured_source
from app.collection.service import collect_source


def run_once(session: Session, worker_id: str):
    task = claim_task(session, worker_id)
    if task is None:
        return None
    # Sprint 1 has no live adapters; every claimed task is reported honestly.
    skip_unconfigured_source(session, task)
    return task


async def process_once(session: Session, worker_id: str, alert_chat_id: int | None = None):
    task = claim_task(session, worker_id)
    if task is None:
        return None
    if task.source_id is None:
        skip_unconfigured_source(session, task)
        return task
    from app.db.models import Source

    source = session.get(Source, task.source_id)
    if source is None:
        skip_unconfigured_source(session, task)
        return task
    run = await collect_source(session, source, alert_chat_id=alert_chat_id)
    task.status = {
        "succeeded": "succeeded",
        "skipped": "skipped",
        "failed": "failed",
    }.get(run.status, "failed")
    task.lease_owner = None
    task.lease_until = None
    session.commit()
    return task
