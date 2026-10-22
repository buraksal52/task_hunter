import secrets
from datetime import UTC, date, datetime

from fastapi import APIRouter, Header, HTTPException, Request, status
from sqlalchemy import select

from app.analytics.queries import market_stats
from app.collection.queue import enqueue_task
from app.core.config import Settings
from app.db.models import Source, TelegramUpdate
from app.notifications.reports import format_daily_report


def build_router(settings: Settings, session_factory) -> APIRouter:
    router = APIRouter()

    @router.post("/telegram/webhook")
    async def webhook(
        request: Request, x_telegram_bot_api_secret_token: str | None = Header(default=None)
    ):
        expected = (
            settings.telegram_webhook_secret.get_secret_value()
            if settings.telegram_webhook_secret
            else None
        )
        if (
            not expected
            or not x_telegram_bot_api_secret_token
            or not secrets.compare_digest(x_telegram_bot_api_secret_token, expected)
        ):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
        payload = await request.json()
        update_id = payload.get("update_id")
        message = payload.get("message") or {}
        user_id = (message.get("from") or {}).get("id")
        chat_id = (message.get("chat") or {}).get("id")
        if (
            update_id is None
            or user_id != settings.telegram_allowed_user_id
            or chat_id != settings.telegram_allowed_chat_id
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        with session_factory() as session:
            if session.get(TelegramUpdate, update_id):
                return {"ok": True, "duplicate": True}
            session.add(TelegramUpdate(update_id=update_id))
            command = (message.get("text") or "").split()[0] if message.get("text") else ""
            response = {"ok": True, "command": command}
            if command == "/hunt":
                sources = session.scalars(
                    select(Source).where(
                        Source.enabled.is_(True), Source.policy_status == "approved"
                    )
                ).all()
                if not sources:
                    response["message"] = "No approved sources are enabled."
                else:
                    for source in sources:
                        enqueue_task(
                            session,
                            f"manual:{source.source_key}:{update_id}",
                            datetime.now(UTC),
                            source.id,
                        )
                    response["message"] = f"Queued {len(sources)} source(s)."
            elif command == "/start":
                response["message"] = (
                    "Freelance Hunter is ready. Use /hunt to scan approved sources."
                )
            elif command == "/stats":
                response["message"] = format_daily_report(
                    market_stats(session, date.today(), date.today())
                )
            elif command in {"/health", "/sources"}:
                response["message"] = (
                    "Command accepted; source health is available through the authenticated API."
                )
            session.commit()
        return response

    return router
