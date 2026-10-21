"""Daily market report generation and durable outbox enqueueing."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics.queries import market_stats
from app.db.models import NotificationOutbox
from app.notifications.outbox import enqueue_event


def format_daily_report(stats: dict) -> str:
    sample = stats["sample"]
    lines = [
        f"Freelance Hunter — {stats['period']['end']} market report",
        (
            f"Observed: {sample['total_jobs']} jobs | Eligible: {sample['eligible_jobs']} | "
            f"Unknown: {sample['unknown_jobs']}"
        ),
        "Top skills:",
    ]
    lines.extend(
        f"{index}. {item['skill']} ({item['count']})"
        for index, item in enumerate(stats["top_skills"], 1)
    )
    lines.append("Scope: approved-source sample; not representative of the whole market.")
    return "\n".join(lines)


def enqueue_daily_report(
    session: Session,
    report_date: date,
    chat_id: int,
) -> tuple[object, bool]:
    stats = market_stats(session, report_date, report_date)
    event_key = f"daily-report:{report_date.isoformat()}"
    existed = session.scalar(
        select(NotificationOutbox.id).where(NotificationOutbox.event_key == event_key)
    )
    event = enqueue_event(
        session,
        event_key,
        "telegram.daily_report",
        {
            "chat_id": chat_id,
            "report_date": report_date.isoformat(),
            "text": format_daily_report(stats),
        },
    )
    return event, existed is None
