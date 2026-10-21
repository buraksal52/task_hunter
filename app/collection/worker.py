from sqlalchemy.orm import Session

from app.collection.queue import claim_task, skip_unconfigured_source


def run_once(session: Session, worker_id: str):
    task = claim_task(session, worker_id)
    if task is None:
        return None
    # Sprint 1 has no live adapters; every claimed task is reported honestly.
    skip_unconfigured_source(session, task)
    return task
