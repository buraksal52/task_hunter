import json
from datetime import UTC, datetime

from sqlalchemy import and_, delete, or_, select
from sqlalchemy.orm import Session

from app.analytics.skills import persist_job_skills
from app.db.models import Job, JobSnapshot, Source
from app.normalization.jobs import NormalizedJob, normalize_job, retention_cutoff
from app.notifications.alerts import enqueue_new_job_alert
from app.sources.base import RawJob


def upsert_job(
    session: Session,
    source: Source,
    normalized: NormalizedJob,
    now: datetime | None = None,
) -> tuple[Job, bool, bool]:
    now = now or datetime.now(UTC)
    content_hash = normalized.content_hash(source.description_storage_allowed)
    job = session.scalar(
        select(Job).where(Job.source_id == source.id, Job.external_id == normalized.external_id)
    )
    created = job is None
    changed = False
    if job is None:
        job = Job(
            source_id=source.id,
            external_id=normalized.external_id,
            first_seen_at=now,
            last_seen_at=now,
        )
        session.add(job)
    else:
        changed = job.content_hash != content_hash
        job.last_seen_at = now
    job.title = normalized.title
    job.description = normalized.description
    job.url = normalized.url
    job.engagement_type = normalized.engagement_type
    job.remote_policy = normalized.remote_policy
    job.classification_confidence = normalized.classification_confidence
    job.classification_evidence = normalized.classification_evidence
    job.budget_type = normalized.budget_type
    job.budget_min = normalized.budget_min
    job.budget_max = normalized.budget_max
    job.currency = normalized.currency
    job.published_at = normalized.published_at
    job.expires_at = normalized.expires_at
    job.content_hash = content_hash
    session.flush()
    if source.description_storage_allowed and (created or changed):
        snapshot = JobSnapshot(
            job_id=job.id,
            content_hash=content_hash,
            changed_at=now,
            snapshot_data=json.dumps(
                normalized.snapshot_fields(description_allowed=True),
                sort_keys=True,
                separators=(",", ":"),
            ),
        )
        session.add(snapshot)
    return job, created, changed


def ingest_raw_jobs(
    session: Session,
    source: Source,
    raw_jobs: list[RawJob],
    now: datetime | None = None,
    alert_chat_id: int | None = None,
) -> tuple[int, int, int]:
    now = now or datetime.now(UTC)
    created_count = 0
    updated_count = 0
    skipped_count = 0
    for raw_job in raw_jobs:
        try:
            normalized = normalize_job(raw_job, source.description_storage_allowed)
            job, created, changed = upsert_job(session, source, normalized, now)
            persist_job_skills(
                session, job.id, f"{normalized.title}\n{normalized.description or ''}"
            )
            if created:
                enqueue_new_job_alert(session, job, alert_chat_id)
            created_count += int(created)
            updated_count += int(changed and not created)
        except (ValueError, TypeError):
            skipped_count += 1
    session.commit()
    return created_count, updated_count, skipped_count


def purge_expired_jobs(session: Session, source: Source, now: datetime | None = None) -> int:
    now = now or datetime.now(UTC)
    conditions = [and_(Job.expires_at.is_not(None), Job.expires_at <= now)]
    cutoff = retention_cutoff(now, source.retention_days)
    if cutoff:
        conditions.append(Job.last_seen_at < cutoff)
    jobs = session.scalars(
        select(Job).where(Job.source_id == source.id).where(or_(*conditions))
    ).all()
    for job in jobs:
        session.execute(delete(JobSnapshot).where(JobSnapshot.job_id == job.id))
        session.delete(job)
    session.commit()
    return len(jobs)
