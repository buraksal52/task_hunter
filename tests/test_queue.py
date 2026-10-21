from datetime import UTC, datetime, timedelta

from app.collection.queue import claim_task, enqueue_task, recover_expired_leases


def test_queue_is_idempotent_and_lease_recovers(client):
    session_factory = client.app.state.session_factory
    now = datetime.now(UTC)
    with session_factory() as session:
        first = enqueue_task(session, "same-key", now)
        second = enqueue_task(session, "same-key", now)
        assert first.id == second.id
        claimed = claim_task(session, "worker-a", lease_seconds=1, now=now)
        assert claimed.id == first.id
        assert claim_task(session, "worker-b", now=now) is None
        claimed.lease_until = now - timedelta(seconds=1)
        session.commit()
        assert recover_expired_leases(session, now) == 1
        reclaimed = claim_task(session, "worker-b", now=now)
        assert reclaimed.id == first.id


def test_two_claimants_cannot_claim_same_task(client):
    session_factory = client.app.state.session_factory
    now = datetime.now(UTC)
    with session_factory() as session:
        enqueue_task(session, "one", now)
        assert claim_task(session, "a", now=now) is not None
        assert claim_task(session, "b", now=now) is None
