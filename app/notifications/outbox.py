import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import NotificationOutbox


def enqueue_event(
    session: Session, event_key: str, event_type: str, payload: dict
) -> NotificationOutbox:
    event = session.scalar(
        select(NotificationOutbox).where(NotificationOutbox.event_key == event_key)
    )
    if event:
        return event
    event = NotificationOutbox(
        event_key=event_key,
        event_type=event_type,
        payload_json=json.dumps(payload, separators=(",", ":")),
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    return event
