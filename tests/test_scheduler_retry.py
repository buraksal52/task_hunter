from datetime import UTC, datetime

from app.collection.retry import decide_retry, retry_delay_seconds
from app.collection.scheduler import configure_scheduler, schedule_due_sources
from app.db.models import Source


def test_scheduler_respects_source_poll_interval(client):
    session_factory = client.app.state.session_factory
    now = datetime.now(UTC)
    with session_factory() as session:
        source = Source(
            source_key="jobicy",
            name="Jobicy",
            enabled=True,
            policy_status="approved",
            minimum_poll_seconds=3600,
        )
        session.add(source)
        session.commit()
        first = schedule_due_sources(session, now)
        second = schedule_due_sources(session, now)
        assert len(first) == 1
        assert second == first


def test_retry_is_bounded_and_honors_retry_after():
    assert retry_delay_seconds(10) == 2560
    assert retry_delay_seconds(20) == 3600
    decision = decide_retry(1, 3, status_code=429, retry_after=12)
    assert decision.retry is True
    assert decision.delay_seconds == 12
    assert decide_retry(3, 3, status_code=500).retry is False
    assert decide_retry(1, 3, status_code=400).retry is False


def test_scheduler_has_single_non_overlapping_tick(client):
    scheduler = configure_scheduler(client.app.state.session_factory, tick_seconds=3600)
    job = scheduler.get_job("collection-tick")
    assert job is not None
    assert job.max_instances == 1
