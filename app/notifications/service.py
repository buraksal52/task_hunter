"""Durable Telegram outbox delivery boundary."""

import json
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import NotificationOutbox


async def deliver_pending_events(session: Session, sender, now: datetime | None = None) -> int:
    """Deliver pending events; failures remain retryable and never expose payloads in errors."""
    now = now or datetime.now(UTC)
    events = session.scalars(
        select(NotificationOutbox)
        .where(NotificationOutbox.status == "pending")
        .where(
            (NotificationOutbox.next_attempt_at.is_(None))
            | (NotificationOutbox.next_attempt_at <= now)
        )
        .order_by(NotificationOutbox.id)
    ).all()
    delivered = 0
    for event in events:
        payload = json.loads(event.payload_json)
        try:
            result = await sender.send_message(payload["chat_id"], payload["text"])
        except Exception:
            event.attempts += 1
            event.last_error_code = "telegram_delivery_failed"
            event.next_attempt_at = now
        else:
            event.status = "sent"
            event.sent_at = now
            event.telegram_message_id = str(result.get("result", {}).get("message_id", "")) or None
            delivered += 1
        session.commit()
    return delivered
