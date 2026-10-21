"""Scheduler boundary; live source jobs are intentionally disabled in Sprint 1."""


def configure_scheduler():
    """Return no jobs until a source passes the policy gate."""
    return []
