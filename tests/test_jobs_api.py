from datetime import UTC, datetime

from app.db.models import Job, Source


def test_jobs_endpoint_is_authenticated_and_bounded(client):
    assert client.get("/api/v1/jobs").status_code == 401
    assert (
        client.get(
            "/api/v1/jobs?page_size=101",
            headers={"X-API-Key": "admin-secret"},
        ).status_code
        == 400
    )


def test_jobs_endpoint_filters_and_applies_description_policy(client):
    now = datetime(2026, 10, 21, 12, tzinfo=UTC)
    with client.app.state.session_factory() as session:
        allowed = Source(
            source_key="jobicy",
            name="Jobicy",
            description_storage_allowed=True,
        )
        restricted = Source(
            source_key="himalayas",
            name="Himalayas",
            description_storage_allowed=False,
        )
        session.add_all([allowed, restricted])
        session.flush()
        session.add_all(
            [
                Job(
                    source_id=allowed.id,
                    external_id="job-1",
                    title="Python project",
                    description="Allowed description",
                    url="https://example.test/1",
                    engagement_type="freelance_project",
                    remote_policy="remote",
                    first_seen_at=now,
                    last_seen_at=now,
                ),
                Job(
                    source_id=restricted.id,
                    external_id="job-2",
                    title="Restricted contract",
                    description="Do not expose",
                    url="https://example.test/2",
                    engagement_type="remote_contract",
                    remote_policy="remote",
                    first_seen_at=now,
                    last_seen_at=now,
                ),
            ]
        )
        session.commit()
    response = client.get(
        "/api/v1/jobs?source_key=jobicy&engagement_type=freelance_project",
        headers={"X-API-Key": "admin-secret"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["description"] == "Allowed description"
    assert "raw_payload" not in body["items"][0]

    restricted_response = client.get(
        "/api/v1/jobs?source_key=himalayas",
        headers={"X-API-Key": "admin-secret"},
    )
    assert "description" not in restricted_response.json()["items"][0]


def test_source_enable_endpoint_requires_approval_and_admin_auth(client):
    with client.app.state.session_factory() as session:
        session.add_all(
            [
                Source(source_key="jobicy", name="Jobicy", policy_status="approved"),
                Source(source_key="blocked", name="Blocked", policy_status="blocked"),
            ]
        )
        session.commit()

    assert client.post("/api/v1/sources/jobicy/enable").status_code == 401
    response = client.post(
        "/api/v1/sources/jobicy/enable", headers={"X-API-Key": "admin-secret"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "source_key": "jobicy",
        "enabled": True,
        "policy_status": "approved",
    }
    blocked_response = client.post(
        "/api/v1/sources/blocked/enable", headers={"X-API-Key": "admin-secret"}
    )
    assert blocked_response.status_code == 409
