from datetime import UTC, date, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from sqlalchemy import func, select

from app.analytics.export import export_jobs, jobs_to_csv
from app.analytics.queries import market_stats
from app.api.auth import admin_header, require_admin
from app.collection.queue import enqueue_task
from app.core.config import Settings
from app.db.models import CollectionRun, Job, Source
from app.imports.manual import import_manual_jobs


def build_router(settings: Settings, session_factory) -> APIRouter:
    router = APIRouter(prefix="/api/v1")

    @router.get("/stats")
    def stats(
        start: date | None = None,
        end: date | None = None,
        api_key: str | None = Depends(admin_header),
    ):
        require_admin(settings, api_key)
        end = end or date.today()
        start = start or (end - timedelta(days=6))
        with session_factory() as session:
            return market_stats(session, start, end)

    @router.get("/jobs")
    def jobs(
        source_key: str | None = None,
        engagement_type: str | None = None,
        remote_policy: str | None = None,
        start: date | None = None,
        end: date | None = None,
        page: int = 1,
        page_size: int = 50,
        api_key: str | None = Depends(admin_header),
    ):
        require_admin(settings, api_key)
        if page < 1 or page_size < 1 or page_size > 100:
            return Response(
                status_code=400, content="page must be >= 1 and page_size must be 1..100"
            )
        with session_factory() as session:
            query = select(Job, Source).join(Source, Source.id == Job.source_id)
            if source_key:
                query = query.where(Source.source_key == source_key)
            if engagement_type:
                query = query.where(Job.engagement_type == engagement_type)
            if remote_policy:
                query = query.where(Job.remote_policy == remote_policy)
            if start:
                query = query.where(
                    Job.first_seen_at >= datetime.combine(start, datetime.min.time(), UTC)
                )
            if end:
                end_exclusive = datetime.combine(end + timedelta(days=1), datetime.min.time(), UTC)
                query = query.where(Job.first_seen_at < end_exclusive)
            total = session.scalar(select(func.count()).select_from(query.subquery())) or 0
            rows = session.execute(
                query.order_by(Job.first_seen_at.desc(), Job.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            ).all()
            items = []
            for job, source in rows:
                item = {
                    "id": job.id,
                    "source_key": source.source_key,
                    "external_id": job.external_id,
                    "title": job.title,
                    "url": job.url,
                    "engagement_type": job.engagement_type,
                    "remote_policy": job.remote_policy,
                    "classification_confidence": job.classification_confidence,
                    "classification_evidence": job.classification_evidence,
                    "budget_type": job.budget_type,
                    "budget_min": job.budget_min,
                    "budget_max": job.budget_max,
                    "currency": job.currency,
                    "published_at": job.published_at.isoformat() if job.published_at else None,
                    "expires_at": job.expires_at.isoformat() if job.expires_at else None,
                    "first_seen_at": job.first_seen_at.isoformat(),
                    "last_seen_at": job.last_seen_at.isoformat(),
                }
                if source.description_storage_allowed:
                    item["description"] = job.description
                items.append(item)
            return {"page": page, "page_size": page_size, "total": int(total), "items": items}

    @router.post("/imports/manual", status_code=202)
    def manual_import(payload: dict[str, Any], api_key: str | None = Depends(admin_header)):
        require_admin(settings, api_key)
        source_key = payload.get("source_key")
        records = payload.get("records")
        if not isinstance(source_key, str) or not isinstance(records, list):
            return Response(status_code=400, content="source_key and records are required")
        with session_factory() as session:
            source = session.scalar(select(Source).where(Source.source_key == source_key))
            if source is None:
                return Response(status_code=404, content="source not found")
            try:
                created, updated, skipped = import_manual_jobs(session, source, records)
            except (TypeError, ValueError) as error:
                return Response(status_code=400, content=str(error))
            return {
                "source_key": source_key,
                "created": created,
                "updated": updated,
                "skipped": skipped,
            }

    @router.get("/sources")
    def sources(api_key: str | None = Depends(admin_header)):
        require_admin(settings, api_key)
        with session_factory() as session:
            now = datetime.now(UTC)
            result = []
            for source in session.scalars(select(Source).order_by(Source.source_key)).all():
                latest = session.scalar(
                    select(CollectionRun)
                    .where(CollectionRun.source_id == source.id)
                    .order_by(CollectionRun.id.desc())
                )
                age = (
                    (now - source.last_success_at).total_seconds()
                    if source.last_success_at
                    else None
                )
                result.append(
                    {
                        "source_key": source.source_key,
                        "enabled": source.enabled,
                        "policy_status": source.policy_status,
                        "last_success_at": (
                            source.last_success_at.isoformat() if source.last_success_at else None
                        ),
                        "freshness_seconds": age,
                        "latest_run": {
                            "status": latest.status,
                            "finished_at": (
                                latest.finished_at.isoformat() if latest.finished_at else None
                            ),
                            "fetched_count": latest.fetched_count,
                            "new_count": latest.new_count,
                            "duration_ms": latest.duration_ms,
                            "error_code": latest.error_code,
                        }
                        if latest
                        else None,
                    }
                )
            return result

    @router.post("/sources/{source_key}/enable")
    def enable_source(source_key: str, api_key: str | None = Depends(admin_header)):
        require_admin(settings, api_key)
        with session_factory() as session:
            source = session.scalar(select(Source).where(Source.source_key == source_key))
            if source is None:
                return Response(status_code=404, content="source not found")
            if source.policy_status != "approved":
                return Response(status_code=409, content="source policy is not approved")
            source.enabled = True
            session.commit()
            return {
                "source_key": source.source_key,
                "enabled": source.enabled,
                "policy_status": source.policy_status,
            }

    @router.get("/jobs/export")
    def export(
        start: date | None = None,
        end: date | None = None,
        output: str = "json",
        api_key: str | None = Depends(admin_header),
    ):
        require_admin(settings, api_key)
        end = end or date.today()
        start = start or end
        if output not in {"json", "csv"}:
            return Response(status_code=400, content="output must be json or csv")
        with session_factory() as session:
            records = export_jobs(session, start, end)
        if output == "csv":
            return Response(
                content=jobs_to_csv(records),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=jobs.csv"},
            )
        return JSONResponse(
            {"period": {"start": start.isoformat(), "end": end.isoformat()}, "jobs": records}
        )

    @router.post("/collection-runs", status_code=202)
    def collection_runs(api_key: str | None = Depends(admin_header)):
        require_admin(settings, api_key)
        with session_factory() as session:
            sources = session.scalars(
                select(Source).where(Source.enabled.is_(True), Source.policy_status == "approved")
            ).all()
            tasks = [
                enqueue_task(
                    session,
                    f"api:{s.source_key}:{datetime.now(UTC).date()}",
                    datetime.now(UTC),
                    s.id,
                ).id
                for s in sources
            ]
            return {"task_ids": tasks}

    return router
