from datetime import UTC, datetime, timedelta

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db.models import CollectionTask


def enqueue_task(
    session: Session, idempotency_key: str, scheduled_at: datetime, source_id: int | None = None
) -> CollectionTask:
    existing = session.scalar(
        select(CollectionTask).where(CollectionTask.idempotency_key == idempotency_key)
    )
    if existing:
        return existing
    task = CollectionTask(
        source_id=source_id,
        idempotency_key=idempotency_key,
        scheduled_at=scheduled_at,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def recover_expired_leases(session: Session, now: datetime | None = None) -> int:
    now = now or datetime.now(UTC)
    tasks = session.scalars(
        select(CollectionTask).where(
            CollectionTask.status == "running",
            CollectionTask.lease_until.is_not(None),
            CollectionTask.lease_until < now,
        )
    ).all()
    for task in tasks:
        task.status = "queued"
        task.lease_owner = None
        task.lease_until = None
    session.commit()
    return len(tasks)


def claim_task(
    session: Session, worker_id: str, lease_seconds: int = 300, now: datetime | None = None
):
    now = now or datetime.now(UTC)
    recover_expired_leases(session, now)
    # SQLite has no row-level FOR UPDATE; BEGIN IMMEDIATE takes a write lock for the
    # whole connection, which is what actually serializes the claim below.
    session.connection().exec_driver_sql("BEGIN IMMEDIATE")
    task = session.scalar(
        select(CollectionTask)
        .where(
            CollectionTask.status == "queued",
            CollectionTask.scheduled_at <= now,
            or_(
                CollectionTask.source_id.is_(None),
                ~CollectionTask.source_id.in_(
                    select(CollectionTask.source_id).where(
                        CollectionTask.status == "running", CollectionTask.source_id.is_not(None)
                    )
                ),
            ),
        )
        .order_by(CollectionTask.scheduled_at, CollectionTask.id)
    )
    if not task:
        return None
    task.status = "running"
    task.lease_owner = worker_id
    task.lease_until = now + timedelta(seconds=lease_seconds)
    task.attempts += 1
    session.commit()
    session.refresh(task)
    return task


def skip_unconfigured_source(session: Session, task: CollectionTask) -> None:
    task.status = "skipped"
    task.lease_owner = None
    task.lease_until = None
    # No adapter registry is enabled in Sprint 1, so this is always honest.
    session.commit()
