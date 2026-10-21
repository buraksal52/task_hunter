import hashlib
import json
from datetime import datetime, timedelta
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.normalization.classification import Classification, classify_job
from app.sources.base import RawJob


class NormalizedJob(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_key: str
    external_id: str
    title: str
    description: str | None
    url: str
    engagement_type: str
    remote_policy: str
    classification_confidence: float | None
    classification_evidence: str
    budget_type: str
    budget_min: float | None
    budget_max: float | None
    currency: str | None
    published_at: datetime | None
    expires_at: datetime | None

    def snapshot_fields(self, description_allowed: bool) -> dict[str, Any]:
        fields = self.model_dump(mode="json")
        if not description_allowed:
            fields["description"] = None
        return fields

    def content_hash(self, description_allowed: bool) -> str:
        encoded = json.dumps(
            self.snapshot_fields(description_allowed), sort_keys=True, separators=(",", ":")
        ).encode()
        return hashlib.sha256(encoded).hexdigest()


def normalize_job(raw: RawJob, description_allowed: bool) -> NormalizedJob:
    classification: Classification = classify_job(
        raw.title, raw.description, raw.engagement_hint, raw.remote_policy_hint
    )
    return NormalizedJob(
        source_key=raw.source_key,
        external_id=raw.external_id or hashlib.sha256(str(raw.url).encode()).hexdigest(),
        title=" ".join(raw.title.split()),
        description=raw.description if description_allowed else None,
        url=str(raw.url),
        engagement_type=classification.engagement_type,
        remote_policy=classification.remote_policy,
        classification_confidence=classification.confidence,
        classification_evidence=classification.evidence,
        budget_type=raw.budget_type,
        budget_min=raw.budget_min,
        budget_max=raw.budget_max,
        currency=raw.currency,
        published_at=raw.published_at,
        expires_at=raw.expires_at,
    )


def retention_cutoff(now: datetime, retention_days: int | None) -> datetime | None:
    if retention_days is None:
        return None
    return now - timedelta(days=retention_days)
