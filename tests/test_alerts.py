from datetime import UTC, datetime

import pytest
from sqlalchemy import select

from app.collection.ingest import ingest_raw_jobs
from app.db.models import Job, NotificationOutbox, Source
from app.notifications.service import deliver_pending_events
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


@pytest.mark.asyncio
async def test_successful_alert_delivery_sets_notified_at(client):
    with client.app.state.session_factory() as session:
        source = Source(source_key="jobicy", name="Jobicy", enabled=True, policy_status="approved")
        session.add(source)
        session.commit()
        ingest_raw_jobs(
            session,
            source,
            [
                RawJob(
                    source_key="jobicy",
                    external_id="notified-1",
                    url="https://example.test/notified-1",
                    title="Remote project",
                    engagement_hint="project",
                    remote_policy_hint="remote",
                )
            ],
            datetime(2026, 10, 21, tzinfo=UTC),
            alert_chat_id=8,
        )

        class Sender:
            async def send_message(self, chat_id, text):
                return {"result": {"message_id": 7}}

        acknowledged_at = datetime(2026, 10, 21, 13, tzinfo=UTC)
        assert await deliver_pending_events(session, Sender(), acknowledged_at) == 1
        job = session.scalar(select(Job).where(Job.external_id == "notified-1"))
        assert job.notified_at == acknowledged_at
