from datetime import UTC, datetime

from sqlalchemy import select

from app.collection.ingest import ingest_raw_jobs
from app.db.models import NotificationOutbox, Source
from app.sources.base import RawJob


def test_new_eligible_job_alert_is_deduplicated(client):
    with client.app.state.session_factory() as session:
        source = Source(source_key="jobicy", name="Jobicy", enabled=True, policy_status="approved")
        session.add(source)
        session.commit()
        raw = RawJob(
            source_key="jobicy",
            external_id="alert-1",
            url="https://example.test/alert-1",
            title="Remote Python contractor",
            engagement_hint="contract",
            remote_policy_hint="remote",
        )
        ingest_raw_jobs(session, source, [raw], datetime(2026, 10, 21, tzinfo=UTC), alert_chat_id=8)
        ingest_raw_jobs(
            session, source, [raw], datetime(2026, 10, 21, 1, tzinfo=UTC), alert_chat_id=8
        )
        events = session.scalars(select(NotificationOutbox)).all()
        assert len(events) == 1
        assert events[0].event_type == "telegram.new_job"


def test_onsite_and_unknown_jobs_do_not_alert(client):
    with client.app.state.session_factory() as session:
        source = Source(source_key="jobicy", name="Jobicy", policy_status="approved")
        session.add(source)
        session.commit()
        jobs = [
            RawJob(
                source_key="jobicy",
                external_id="onsite-1",
                url="https://example.test/onsite-1",
                title="Onsite developer",
                engagement_hint="project",
                remote_policy_hint="onsite",
            ),
            RawJob(
                source_key="jobicy",
                external_id="unknown-1",
                url="https://example.test/unknown-1",
                title="Developer opportunity",
            ),
        ]
        ingest_raw_jobs(session, source, jobs, alert_chat_id=8)
        assert session.scalars(select(NotificationOutbox)).all() == []
