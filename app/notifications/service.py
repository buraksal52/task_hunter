"""Outbox delivery service boundary for the durable worker."""


def deliver_pending_events():
    """Delivery is wired in a later sprint; Sprint 1 only persists intent."""
    return 0
