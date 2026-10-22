import httpx
import respx
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.db.models import CollectionTask, TelegramUpdate
from app.main import create_app


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


@respx.mock
def test_command_response_is_sent_to_telegram(settings):
    settings.telegram_bot_token = SecretStr("bot-token")
    route = respx.post("https://api.telegram.org/botbot-token/sendMessage").mock(
        return_value=httpx.Response(200, json={"ok": True, "result": {"message_id": 1}})
    )
    with TestClient(create_app(settings)) as test_client:
        response = test_client.post(
            "/telegram/webhook",
            headers={"X-Telegram-Bot-Api-Secret-Token": "test-secret"},
            json=payload(update_id=200, command="/start"),
        )
    assert response.status_code == 200
    assert response.json()["message"].startswith("Freelance Hunter is ready")
    assert route.called
    assert route.calls[0].request.content == (
        b'{"chat_id":8,"text":"Freelance Hunter is ready. Use /hunt to scan approved sources."}'
    )
