from datetime import UTC, datetime

from app.collection.queue import enqueue_task
from app.collection.worker import run_once
from app.notifications.outbox import enqueue_event


def test_outbox_is_idempotent_and_worker_skips_without_adapter(client):
    session_factory = client.app.state.session_factory
    with session_factory() as session:
        event_a = enqueue_event(session, "daily:2026-10-21", "daily_report", {"count": 0})
        event_b = enqueue_event(session, "daily:2026-10-21", "daily_report", {"count": 99})
        assert event_a.id == event_b.id
        enqueue_task(session, "worker-task", datetime.now(UTC))
        task = run_once(session, "worker-1")
        assert task.status == "skipped"
