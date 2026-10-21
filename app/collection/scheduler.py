"""Source-aware scheduling primitives used by the single application worker."""

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.collection.queue import enqueue_task
from app.db.models import Source


def configure_scheduler(
    session_factory,
    tick_seconds: int = 60,
    alert_chat_id: int | None = None,
    report_chat_id: int | None = None,
    report_hour: int = 18,
    app_timezone: str = "UTC",
    sender=None,
    collect_enabled: bool = True,
) -> AsyncIOScheduler:
    """Build the one-process scheduler; caller owns start/stop in application lifespan."""
    from app.collection.worker import process_once

    scheduler = AsyncIOScheduler(timezone="UTC")

    async def tick() -> None:
        with session_factory() as session:
            if collect_enabled:
                schedule_due_sources(session)
                await process_once(session, "scheduler-worker", alert_chat_id=alert_chat_id)
            if sender:
                from app.notifications.service import deliver_pending_events

                await deliver_pending_events(session, sender)

    async def daily_report() -> None:
        if not report_chat_id:
            return
        with session_factory() as session:
            from app.notifications.reports import enqueue_daily_report
            from app.notifications.service import deliver_pending_events

            report_date = datetime.now(ZoneInfo(app_timezone)).date()
            enqueue_daily_report(session, report_date, report_chat_id)
            if sender:
                await deliver_pending_events(session, sender)

    scheduler.add_job(
        tick,
        "interval",
        seconds=tick_seconds,
        id="collection-tick",
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        daily_report,
        "cron",
        hour=report_hour,
        minute=0,
        id="daily-report",
        max_instances=1,
        coalesce=True,
        timezone=ZoneInfo(app_timezone),
    )
    return scheduler


def schedule_due_sources(session: Session, now: datetime | None = None) -> list[int]:
    now = now or datetime.now(UTC)
    task_ids: list[int] = []
    sources = session.scalars(
        select(Source).where(Source.enabled.is_(True), Source.policy_status == "approved")
    ).all()
    for source in sources:
        interval = source.minimum_poll_seconds or 3600
        if source.last_success_at and (now - source.last_success_at).total_seconds() < interval:
            continue
        window = int(now.timestamp()) // interval
        task = enqueue_task(
            session,
            f"scheduled:{source.source_key}:{window}",
            now,
            source.id,
        )
        task_ids.append(task.id)
    return task_ids
