from datetime import UTC, date, datetime, timedelta

from app.analytics.export import export_jobs, jobs_to_csv
from app.db.models import Job, Source


def test_export_respects_description_rights_expiry_and_retention(client):
    now = datetime(2026, 10, 21, 12, tzinfo=UTC)
    with client.app.state.session_factory() as session:
        allowed = Source(
            source_key="jobicy",
            name="Jobicy",
            description_storage_allowed=True,
            retention_days=7,
        )
        restricted = Source(
            source_key="himalayas",
            name="Himalayas",
            description_storage_allowed=False,
            retention_days=7,
        )
        session.add_all([allowed, restricted])
        session.flush()
        session.add_all(
            [
                Job(
                    source_id=allowed.id,
                    external_id="allowed",
                    title="Allowed",
                    description="Permitted description",
                    url="https://example.test/allowed",
                    first_seen_at=now,
                    last_seen_at=now,
                ),
                Job(
                    source_id=restricted.id,
                    external_id="restricted",
                    title="Restricted",
                    description="Should not export",
                    url="https://example.test/restricted",
                    first_seen_at=now,
                    last_seen_at=now,
                ),
                Job(
                    source_id=allowed.id,
                    external_id="expired",
                    title="Expired",
                    url="https://example.test/expired",
                    first_seen_at=now,
                    last_seen_at=now,
                    expires_at=now - timedelta(minutes=1),
                ),
                Job(
                    source_id=allowed.id,
                    external_id="retained-out",
                    title="Old",
                    url="https://example.test/old",
                    first_seen_at=now - timedelta(days=8),
                    last_seen_at=now - timedelta(days=8),
                ),
            ]
        )
        session.commit()
        records = export_jobs(session, date(2026, 10, 1), date(2026, 10, 21), now=now)
        assert {record["external_id"] for record in records} == {"allowed", "restricted"}
        assert records[0]["description"] == "Permitted description"
        assert "description" not in records[1]
        csv_body = jobs_to_csv(records)
        assert "Permitted description" in csv_body
        assert "Should not export" not in csv_body


def test_export_endpoint_requires_auth_and_supports_csv(client):
    assert client.get("/api/v1/jobs/export").status_code == 401
    response = client.get(
        "/api/v1/jobs/export?start=2026-10-21&end=2026-10-21&output=csv",
        headers={"X-API-Key": "admin-secret"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "source_key" in response.text


def test_export_rejects_unknown_format(client):
    response = client.get(
        "/api/v1/jobs/export?output=xml",
        headers={"X-API-Key": "admin-secret"},
    )
    assert response.status_code == 400
