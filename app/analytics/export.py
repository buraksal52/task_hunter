"""Rights-aware exports of normalized jobs only."""

from __future__ import annotations

import csv
import io
from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics.queries import _utc_bounds
from app.db.models import Job, Source

EXPORT_FIELDS = (
    "source_key",
    "external_id",
    "title",
    "url",
    "engagement_type",
    "remote_policy",
    "classification_confidence",
    "budget_type",
    "budget_min",
    "budget_max",
    "currency",
    "published_at",
    "expires_at",
    "first_seen_at",
    "last_seen_at",
    "description",
)


def export_jobs(
    session: Session,
    start: date,
    end: date,
    now: datetime | None = None,
) -> list[dict]:
    start_at, end_at = _utc_bounds(start, end)
    now = now or datetime.now(UTC)
    rows = session.execute(
        select(Job, Source)
        .join(Source, Source.id == Job.source_id)
        .where(Job.first_seen_at >= start_at, Job.first_seen_at < end_at)
        .where((Job.expires_at.is_(None)) | (Job.expires_at > now))
        .order_by(Job.first_seen_at, Job.id)
    ).all()
    records = []
    for job, source in rows:
        if source.retention_days is not None:
            cutoff = now.timestamp() - source.retention_days * 86400
            if job.last_seen_at.timestamp() < cutoff:
                continue
        record = {
            "source_key": source.source_key,
            "external_id": job.external_id,
            "title": job.title,
            "url": job.url,
            "engagement_type": job.engagement_type,
            "remote_policy": job.remote_policy,
            "classification_confidence": job.classification_confidence,
            "budget_type": job.budget_type,
            "budget_min": job.budget_min,
            "budget_max": job.budget_max,
            "currency": job.currency,
            "published_at": job.published_at.isoformat() if job.published_at else None,
            "expires_at": job.expires_at.isoformat() if job.expires_at else None,
            "first_seen_at": job.first_seen_at.isoformat(),
            "last_seen_at": job.last_seen_at.isoformat(),
        }
        if source.description_storage_allowed:
            record["description"] = job.description
        records.append(record)
    return records


def jobs_to_csv(records: list[dict]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=EXPORT_FIELDS, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(records)
    return output.getvalue()
