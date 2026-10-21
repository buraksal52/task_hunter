from app.db.models import CollectionTask, TelegramUpdate


def payload(update_id=1, command="/hunt"):
    return {
        "update_id": update_id,
        "message": {
            "from": {"id": 7},
            "chat": {"id": 8},
            "text": command,
        },
    }


def test_webhook_rejects_bad_secret(client):
    response = client.post(
        "/telegram/webhook", json=payload(), headers={"X-Telegram-Bot-Api-Secret-Token": "bad"}
    )
    assert response.status_code == 401


def test_webhook_rejects_unallowlisted_user(client):
    body = payload()
    body["message"]["from"]["id"] = 99
    response = client.post(
        "/telegram/webhook", json=body, headers={"X-Telegram-Bot-Api-Secret-Token": "test-secret"}
    )
    assert response.status_code == 403


def test_hunt_is_honest_when_no_sources_approved(client):
    headers = {"X-Telegram-Bot-Api-Secret-Token": "test-secret"}
    response = client.post("/telegram/webhook", json=payload(), headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "No approved sources are enabled."
    duplicate = client.post("/telegram/webhook", json=payload(), headers=headers)
    assert duplicate.json()["duplicate"] is True
    with client.app.state.session_factory() as session:
        assert session.get(TelegramUpdate, 1) is not None
        assert session.query(CollectionTask).count() == 0


def test_stats_returns_real_scoped_report(client):
    response = client.post(
        "/telegram/webhook",
        headers={"X-Telegram-Bot-Api-Secret-Token": "test-secret"},
        json={
            "update_id": 100,
            "message": {
                "text": "/stats",
                "from": {"id": 7},
                "chat": {"id": 8},
            },
        },
    )
    assert response.status_code == 200
    assert "market report" in response.json()["message"]
