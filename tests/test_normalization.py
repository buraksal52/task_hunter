from datetime import UTC, datetime

from app.normalization.classification import classify_job
from app.normalization.jobs import normalize_job
from app.sources.base import RawJob


def test_classification_keeps_engagement_and_remote_policy_independent():
    result = classify_job("Python contractor", "Remote role", remote_policy_hint="remote")
    assert result.engagement_type == "remote_contract"
    assert result.remote_policy == "remote"
    assert "contract" in result.evidence


def test_classification_does_not_invent_remote_contract():
    result = classify_job("Python contractor", "Onsite in Istanbul")
    assert result.engagement_type == "unknown"
    assert result.remote_policy == "onsite"


def test_normalization_uses_url_hash_when_external_id_missing():
    raw = RawJob(
        source_key="test",
        url="https://example.test/jobs/1",
        title="  Python   Engineer ",
        published_at=datetime(2026, 10, 21, tzinfo=UTC),
    )
    normalized = normalize_job(raw, description_allowed=False)
    assert normalized.title == "Python Engineer"
    assert len(normalized.external_id) == 64
    assert normalized.description is None
