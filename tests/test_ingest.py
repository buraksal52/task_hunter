from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.collection.ingest import ingest_raw_jobs, purge_expired_jobs
from app.db.models import Job, JobSnapshot, Source
from app.sources.base import RawJob


def test_reingest_is_idempotent_and_snapshots_only_on_change(client):
    session_factory = client.app.state.session_factory
    first_seen = datetime(2026, 10, 21, 10, 0, tzinfo=UTC)
    later = first_seen + timedelta(hours=1)
    raw = RawJob(
        source_key="jobicy",
        external_id="123",
        url="https://jobicy.test/jobs/123",
        title="Python Contractor",
        description="Remote API work",
        engagement_hint="Contract",
        remote_policy_hint="remote",
    )
    with session_factory() as session:
        source = Source(
            source_key="jobicy",
            name="Jobicy",
            enabled=True,
            policy_status="approved",
            description_storage_allowed=True,
            retention_days=7,
        )
        session.add(source)
        session.commit()
        assert ingest_raw_jobs(session, source, [raw], first_seen) == (1, 0, 0)
        assert ingest_raw_jobs(session, source, [raw], later) == (0, 0, 0)
        job = session.scalar(select(Job).where(Job.external_id == "123"))
        assert job.first_seen_at == first_seen
        assert job.last_seen_at == later
        assert session.scalar(select(JobSnapshot).where(JobSnapshot.job_id == job.id)) is not None
        assert (
            len(session.scalars(select(JobSnapshot).where(JobSnapshot.job_id == job.id)).all()) == 1
        )

        changed = raw.model_copy(update={"description": "Remote API and testing work"})
        assert ingest_raw_jobs(session, source, [changed], later + timedelta(hours=1)) == (0, 1, 0)
        assert (
            len(session.scalars(select(JobSnapshot).where(JobSnapshot.job_id == job.id)).all()) == 2
        )


def test_retention_and_source_expiry_remove_jobs(client):
    session_factory = client.app.state.session_factory
    now = datetime(2026, 10, 21, 10, 0, tzinfo=UTC)
    with session_factory() as session:
        source = Source(
            source_key="himalayas",
            name="Himalayas",
            enabled=True,
            policy_status="approved",
            description_storage_allowed=True,
        )
        session.add(source)
        session.commit()
        expired = RawJob(
            source_key="himalayas",
            external_id="expired",
            url="https://himalayas.app/jobs/expired",
            title="Expired contractor",
            engagement_hint="Contractor",
            remote_policy_hint="remote",
            expires_at=now - timedelta(minutes=1),
        )
        ingest_raw_jobs(session, source, [expired], now - timedelta(days=2))
        assert purge_expired_jobs(session, source, now) == 1
        assert session.scalar(select(Job).where(Job.external_id == "expired")) is None

        active = RawJob(
            source_key="himalayas",
            external_id="active",
            url="https://himalayas.app/jobs/active",
            title="Active contractor",
            engagement_hint="Contractor",
            remote_policy_hint="remote",
            expires_at=now + timedelta(days=1),
        )
        ingest_raw_jobs(session, source, [active], now)
        assert purge_expired_jobs(session, source, now) == 0
        assert session.scalar(select(Job).where(Job.external_id == "active")) is not None
