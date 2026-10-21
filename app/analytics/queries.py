"""Deterministic analytics queries with explicit market-scope rules."""

from __future__ import annotations

from datetime import UTC, date, datetime, time, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Job, JobSkill, Skill, Source

ELIGIBLE_ENGAGEMENT_TYPES = ("freelance_project", "freelance_hourly", "remote_contract")


def _utc_bounds(start: date, end: date) -> tuple[datetime, datetime]:
    if end < start:
        raise ValueError("end date must not precede start date")
    return (
        datetime.combine(start, time.min, tzinfo=UTC),
        datetime.combine(end + timedelta(days=1), time.min, tzinfo=UTC),
    )


def _window_clause(start: datetime, end: datetime):
    return (Job.first_seen_at >= start, Job.first_seen_at < end)


def market_stats(session: Session, start: date, end: date) -> dict:
    """Return counts for the observed window, without implying market representativeness."""
    start_at, end_at = _utc_bounds(start, end)
    window = _window_clause(start_at, end_at)
    total = session.scalar(select(func.count(Job.id)).where(*window)) or 0
    eligible = (
        session.scalar(
            select(func.count(Job.id)).where(
                *window,
                Job.engagement_type.in_(ELIGIBLE_ENGAGEMENT_TYPES),
                Job.remote_policy != "onsite",
            )
        )
        or 0
    )
    unknown = (
        session.scalar(select(func.count(Job.id)).where(*window, Job.engagement_type == "unknown"))
        or 0
    )

    split_rows = session.execute(
        select(Source.source_key, Job.engagement_type, func.count(Job.id))
        .join(Source, Source.id == Job.source_id)
        .where(*window)
        .group_by(Source.source_key, Job.engagement_type)
        .order_by(Source.source_key, Job.engagement_type)
    ).all()
    by_source: dict[str, dict[str, int]] = {}
    for source_key, engagement_type, count in split_rows:
        by_source.setdefault(source_key, {})[engagement_type] = int(count)

    skill_rows = session.execute(
        select(Skill.canonical_name, func.count(JobSkill.job_id).label("count"))
        .join(JobSkill, JobSkill.skill_id == Skill.id)
        .join(Job, Job.id == JobSkill.job_id)
        .where(
            *window,
            Job.engagement_type.in_(ELIGIBLE_ENGAGEMENT_TYPES),
            Job.remote_policy != "onsite",
        )
        .group_by(Skill.canonical_name)
        .order_by(func.count(JobSkill.job_id).desc(), Skill.canonical_name)
        .limit(20)
    ).all()

    return {
        "period": {"start": start.isoformat(), "end": end.isoformat(), "timezone": "UTC"},
        "sample": {
            "total_jobs": int(total),
            "eligible_jobs": int(eligible),
            "unknown_jobs": int(unknown),
        },
        "by_source": by_source,
        "top_skills": [{"skill": name, "count": int(count)} for name, count in skill_rows],
        "scope": {
            "included_engagement": list(ELIGIBLE_ENGAGEMENT_TYPES),
            "excluded_remote_policy": ["onsite"],
            "note": (
                "Observed approved-source sample; not representative of the whole freelance market."
            ),
        },
    }
