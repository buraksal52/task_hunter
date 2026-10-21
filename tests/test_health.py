def test_health_endpoints(client):
    assert client.get("/health/live").json() == {"status": "ok"}
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_admin_route_requires_api_key(client):
    assert client.get("/api/v1/sources").status_code == 401
    assert client.get("/api/v1/sources", headers={"X-API-Key": "admin-secret"}).json() == []
