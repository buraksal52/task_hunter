"""Eligibility and payload rules for immediate new-job notifications."""

from sqlalchemy.orm import Session

from app.db.models import Job
from app.notifications.outbox import enqueue_event

ELIGIBLE_ENGAGEMENT_TYPES = {"freelance_project", "freelance_hourly", "remote_contract"}


def enqueue_new_job_alert(session: Session, job: Job, chat_id: int | None) -> bool:
    if chat_id is None or job.engagement_type not in ELIGIBLE_ENGAGEMENT_TYPES:
        return False
    if job.remote_policy == "onsite":
        return False
    event = enqueue_event(
        session,
        f"new-job:{job.source_id}:{job.external_id}",
        "telegram.new_job",
        {
            "chat_id": chat_id,
            "job_id": job.id,
            "text": f"New freelance opportunity\n{job.title}\n{job.url}",
        },
    )
    return event.status == "pending"
