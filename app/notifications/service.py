"""Durable Telegram outbox delivery boundary."""

import json
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Job, NotificationOutbox


async def deliver_pending_events(session: Session, sender, now: datetime | None = None) -> int:
    """Deliver pending events; failures remain retryable and never expose payloads in errors."""
    now = now or datetime.now(UTC)
    session.query(NotificationOutbox).filter(NotificationOutbox.status == "sending").update(
        {NotificationOutbox.status: "pending"}, synchronize_session=False
    )
    session.commit()
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
        event.status = "sending"
        session.commit()
        try:
            result = await sender.send_message(payload["chat_id"], payload["text"])
        except Exception:
            event.attempts += 1
            event.status = "pending"
            event.last_error_code = "telegram_delivery_failed"
            event.next_attempt_at = now + timedelta(seconds=min(3600, 60 * (2**event.attempts)))
        else:
            event.status = "sent"
            event.sent_at = now
            event.telegram_message_id = str(result.get("result", {}).get("message_id", "")) or None
            if event.event_type == "telegram.new_job":
                job_id = json.loads(event.payload_json).get("job_id")
                if job_id:
                    job = session.get(Job, job_id)
                    if job:
                        job.notified_at = now
            delivered += 1
        session.commit()
    return delivered
