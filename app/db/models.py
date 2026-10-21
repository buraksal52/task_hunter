from datetime import UTC, datetime

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.types import UTCDateTime


def utc_now() -> datetime:
    return datetime.now(UTC)


class Source(Base):
    __tablename__ = "sources"
    id: Mapped[int] = mapped_column(primary_key=True)
    source_key: Mapped[str] = mapped_column(String(100), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    policy_status: Mapped[str] = mapped_column(String(20), default="unverified")
    access_method: Mapped[str | None] = mapped_column(String(50))
    terms_url: Mapped[str | None] = mapped_column(String(500))
    policy_verified_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    minimum_poll_seconds: Mapped[int | None] = mapped_column(Integer)
    retention_days: Mapped[int | None] = mapped_column(Integer)
    description_storage_allowed: Mapped[bool] = mapped_column(Boolean, default=False)
    attribution_required: Mapped[bool] = mapped_column(Boolean, default=False)
    last_success_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utc_now)


class CollectionTask(Base):
    __tablename__ = "collection_tasks"
    __table_args__ = (UniqueConstraint("idempotency_key"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"))
    run_id: Mapped[int | None] = mapped_column(ForeignKey("collection_runs.id"))
    idempotency_key: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(20), default="queued")
    scheduled_at: Mapped[datetime] = mapped_column(UTCDateTime())
    lease_owner: Mapped[str | None] = mapped_column(String(100))
    lease_until: Mapped[datetime | None] = mapped_column(UTCDateTime())
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utc_now)


class CollectionRun(Base):
    __tablename__ = "collection_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    status: Mapped[str] = mapped_column(String(20))
    started_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    finished_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    fetched_count: Mapped[int] = mapped_column(default=0)
    new_count: Mapped[int] = mapped_column(default=0)
    updated_count: Mapped[int] = mapped_column(default=0)
    skipped_count: Mapped[int] = mapped_column(default=0)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    error_code: Mapped[str | None] = mapped_column(String(100))
    error_message: Mapped[str | None] = mapped_column(Text)


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (UniqueConstraint("source_id", "external_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    external_id: Mapped[str] = mapped_column(String(500))
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str] = mapped_column(String(2000))
    engagement_type: Mapped[str] = mapped_column(String(30), default="unknown")
    remote_policy: Mapped[str] = mapped_column(String(20), default="unknown")
    classification_confidence: Mapped[float | None] = mapped_column(Float)
    classification_evidence: Mapped[str | None] = mapped_column(Text)
    budget_type: Mapped[str] = mapped_column(String(20), default="unknown")
    budget_min: Mapped[float | None] = mapped_column(Float)
    budget_max: Mapped[float | None] = mapped_column(Float)
    currency: Mapped[str | None] = mapped_column(String(10))
    published_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    expires_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    notified_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    first_seen_at: Mapped[datetime] = mapped_column(UTCDateTime())
    last_seen_at: Mapped[datetime] = mapped_column(UTCDateTime())
    content_hash: Mapped[str | None] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utc_now)


class NotificationOutbox(Base):
    __tablename__ = "notification_outbox"
    id: Mapped[int] = mapped_column(primary_key=True)
    event_key: Mapped[str] = mapped_column(String(255), unique=True)
    event_type: Mapped[str] = mapped_column(String(100))
    payload_json: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    attempts: Mapped[int] = mapped_column(default=0)
    next_attempt_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    sent_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    telegram_message_id: Mapped[str | None] = mapped_column(String(100))
    last_error_code: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utc_now)


class TelegramUpdate(Base):
    __tablename__ = "telegram_updates"
    update_id: Mapped[int] = mapped_column(primary_key=True)
    received_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utc_now)


class Skill(Base):
    __tablename__ = "skills"
    id: Mapped[int] = mapped_column(primary_key=True)
    canonical_name: Mapped[str] = mapped_column(String(100), unique=True)
    category: Mapped[str] = mapped_column(String(100))


class SkillAlias(Base):
    __tablename__ = "skill_aliases"
    id: Mapped[int] = mapped_column(primary_key=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"))
    alias: Mapped[str] = mapped_column(String(100))
    match_rule: Mapped[str] = mapped_column(String(50), default="word_boundary")
    __table_args__ = (UniqueConstraint("skill_id", "alias"),)


class JobSkill(Base):
    __tablename__ = "job_skills"
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), primary_key=True)
    confidence: Mapped[float | None] = mapped_column(Float)
    evidence: Mapped[str | None] = mapped_column(Text)
    extractor_version: Mapped[str] = mapped_column(String(50))


class JobSnapshot(Base):
    __tablename__ = "job_snapshots"
    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"))
    content_hash: Mapped[str] = mapped_column(String(128))
    changed_at: Mapped[datetime] = mapped_column(UTCDateTime())
    snapshot_data: Mapped[str | None] = mapped_column(Text)
    __table_args__ = (UniqueConstraint("job_id", "content_hash"),)


class DailyMetric(Base):
    __tablename__ = "daily_metrics"
    metric_date: Mapped[str] = mapped_column(String(10), primary_key=True)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), primary_key=True)
    engagement_type: Mapped[str] = mapped_column(String(30), primary_key=True)
    metric_key: Mapped[str] = mapped_column(String(100), primary_key=True)
    metric_value: Mapped[float] = mapped_column(Float)
    computed_at: Mapped[datetime] = mapped_column(UTCDateTime())
