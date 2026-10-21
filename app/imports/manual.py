"""User-supplied listing import; never fetches or automates a source."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.collection.ingest import ingest_raw_jobs
from app.db.models import Source
from app.sources.base import RawJob

MAX_MANUAL_RECORDS = 100


def import_manual_jobs(
    session: Session,
    source: Source,
    records: list[dict[str, Any]],
    now: datetime | None = None,
) -> tuple[int, int, int]:
    """Import records explicitly supplied by a user or an authorized export.

    The source must be configured as ``manual_user_supplied``. No URLs are fetched,
    no browser is launched, and raw payloads are discarded before ingestion.
    """
    if not source.enabled or source.access_method != "manual_user_supplied":
        raise ValueError("source is not enabled for manual user-supplied import")
    if len(records) > MAX_MANUAL_RECORDS:
        raise ValueError(f"manual import is limited to {MAX_MANUAL_RECORDS} records")
    raw_jobs = []
    for record in records:
        if record.get("source_key") not in (None, source.source_key):
            raise ValueError("record source_key does not match source")
        raw_jobs.append(
            RawJob.model_validate({**record, "source_key": source.source_key, "raw_payload": None})
        )
    return ingest_raw_jobs(session, source, raw_jobs, now or datetime.now(UTC))
