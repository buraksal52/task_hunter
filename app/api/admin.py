from datetime import UTC, date, datetime, timedelta

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from sqlalchemy import select

from app.analytics.export import export_jobs, jobs_to_csv
from app.analytics.queries import market_stats
from app.api.auth import admin_header, require_admin
from app.collection.queue import enqueue_task
from app.core.config import Settings
from app.db.models import CollectionRun, Source


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
                            "error_code": latest.error_code,
                        }
                        if latest
                        else None,
                    }
                )
            return result

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
        from datetime import datetime

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
