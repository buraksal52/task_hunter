from datetime import UTC

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.api.auth import admin_header, require_admin
from app.collection.queue import enqueue_task
from app.core.config import Settings
from app.db.models import Source


def build_router(settings: Settings, session_factory) -> APIRouter:
    router = APIRouter(prefix="/api/v1")

    @router.get("/sources")
    def sources(api_key: str | None = Depends(admin_header)):
        require_admin(settings, api_key)
        with session_factory() as session:
            return [
                {"source_key": s.source_key, "enabled": s.enabled, "policy_status": s.policy_status}
                for s in session.scalars(select(Source)).all()
            ]

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
