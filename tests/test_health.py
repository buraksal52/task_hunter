def test_health_endpoints(client):
    assert client.get("/health/live").json() == {"status": "ok"}
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_admin_route_requires_api_key(client):
    assert client.get("/api/v1/sources").status_code == 401
    assert client.get("/api/v1/sources", headers={"X-API-Key": "admin-secret"}).json() == []


def test_sources_reports_freshness_and_latest_run(client):
    from datetime import UTC, datetime

    from app.db.models import CollectionRun, Source

    with client.app.state.session_factory() as session:
        source = Source(
            source_key="jobicy",
            name="Jobicy",
            enabled=True,
            policy_status="approved",
            last_success_at=datetime(2026, 10, 21, 10, tzinfo=UTC),
        )
        session.add(source)
        session.flush()
        session.add(
            CollectionRun(
                source_id=source.id,
                status="failed",
                fetched_count=2,
                error_code="timeout",
            )
        )
        session.commit()

    response = client.get("/api/v1/sources", headers={"X-API-Key": "admin-secret"})
    payload = response.json()[0]
    assert payload["source_key"] == "jobicy"
    assert payload["last_success_at"].startswith("2026-10-21T10:00:00")
    assert payload["latest_run"]["status"] == "failed"
    assert payload["latest_run"]["error_code"] == "timeout"
    assert payload["latest_run"]["duration_ms"] is None
    assert payload["freshness_seconds"] >= 0


def test_stats_endpoint_returns_scoped_report(client):
    response = client.get(
        "/api/v1/stats?start=2026-10-21&end=2026-10-21",
        headers={"X-API-Key": "admin-secret"},
    )
    assert response.status_code == 200
    assert response.json()["period"] == {
        "start": "2026-10-21",
        "end": "2026-10-21",
        "timezone": "UTC",
    }
