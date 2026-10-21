from datetime import UTC, datetime

import pytest
from sqlalchemy import select

from app.db.models import Job, Source
from app.imports.manual import import_manual_jobs


def test_manual_import_accepts_user_supplied_records_without_fetching(client):
    with client.app.state.session_factory() as session:
        source = Source(
            source_key="manual_fiverr",
            name="User supplied Fiverr export",
            enabled=True,
            policy_status="approved",
            access_method="manual_user_supplied",
        )
        session.add(source)
        session.commit()
        result = import_manual_jobs(
            session,
            source,
            [
                {
                    "external_id": "manual-1",
                    "url": "https://example.test/manual-1",
                    "title": "User supplied project",
                    "raw_payload": {"private": "discard"},
                }
            ],
            datetime(2026, 10, 21, tzinfo=UTC),
        )
        assert result == (1, 0, 0)
        job = session.scalar(select(Job).where(Job.external_id == "manual-1"))
        assert job is not None


def test_manual_import_requires_explicit_source_mode(client):
    with client.app.state.session_factory() as session:
        source = Source(source_key="fiverr", name="Fiverr", enabled=False)
        session.add(source)
        session.commit()
        with pytest.raises(ValueError, match="manual user-supplied"):
            import_manual_jobs(session, source, [])


def test_manual_import_endpoint_requires_admin_and_ingests_records(client):
    assert client.post("/api/v1/imports/manual", json={}).status_code == 401
    with client.app.state.session_factory() as session:
        session.add(
            Source(
                source_key="manual_fiverr",
                name="Manual Fiverr",
                enabled=True,
                policy_status="approved",
                access_method="manual_user_supplied",
            )
        )
        session.commit()
    response = client.post(
        "/api/v1/imports/manual",
        headers={"X-API-Key": "admin-secret"},
        json={
            "source_key": "manual_fiverr",
            "records": [
                {
                    "external_id": "endpoint-1",
                    "url": "https://example.test/endpoint-1",
                    "title": "Imported listing",
                }
            ],
        },
    )
    assert response.status_code == 202
    assert response.json()["created"] == 1
