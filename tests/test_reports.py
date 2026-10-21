from datetime import UTC, date, datetime

import pytest
from sqlalchemy import select

from app.db.models import NotificationOutbox, Source
from app.notifications.reports import enqueue_daily_report
from app.notifications.service import deliver_pending_events


def test_daily_report_is_deduplicated(client):
    with client.app.state.session_factory() as session:
        session.add(Source(source_key="jobicy", name="Jobicy", policy_status="approved"))
        session.commit()
        first, created = enqueue_daily_report(session, date(2026, 10, 21), 8)
        second, duplicate_created = enqueue_daily_report(session, date(2026, 10, 21), 8)
        assert created is True
        assert duplicate_created is False
        assert first.id == second.id
        assert session.scalar(
            select(NotificationOutbox).where(
                NotificationOutbox.event_key == "daily-report:2026-10-21"
            )
        )


@pytest.mark.asyncio
async def test_outbox_delivery_marks_event_sent(client):
    with client.app.state.session_factory() as session:
        session.add(Source(source_key="jobicy", name="Jobicy", policy_status="approved"))
        session.commit()
        enqueue_daily_report(session, date(2026, 10, 21), 8)

        class Sender:
            async def send_message(self, chat_id, text):
                assert chat_id == 8
                assert "market report" in text
                return {"result": {"message_id": 42}}

        assert (
            await deliver_pending_events(session, Sender(), datetime(2026, 10, 21, tzinfo=UTC)) == 1
        )
        event = session.scalar(select(NotificationOutbox))
        assert event.status == "sent"
        assert event.telegram_message_id == "42"
