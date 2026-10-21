import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.admin import build_router as build_admin_router
from app.api.telegram import build_router as build_telegram_router
from app.collection.scheduler import configure_scheduler
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.db.session import create_session_factory, init_db

logger = logging.getLogger("freelance_hunter")


def create_app(settings: Settings | None = None) -> FastAPI:
    configure_logging()
    settings = settings or get_settings()
    engine, session_factory = create_session_factory(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        init_db(engine)
        scheduler = (
            configure_scheduler(
                session_factory,
                alert_chat_id=(
                    settings.telegram_allowed_chat_id if settings.instant_alerts_enabled else None
                ),
            )
            if settings.collection_enabled
            else None
        )
        if scheduler:
            scheduler.start()
        app.state.scheduler = scheduler
        yield
        if scheduler:
            scheduler.shutdown(wait=False)
        engine.dispose()

    app = FastAPI(title="Freelance Hunter", version="0.1.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.engine = engine
    app.state.session_factory = session_factory

    @app.middleware("http")
    async def correlation_middleware(request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response

    @app.get("/health/live")
    async def live():
        return {"status": "ok"}

    @app.get("/health/ready")
    async def ready():
        try:
            with session_factory() as session:
                session.execute(__import__("sqlalchemy").text("SELECT 1"))
            return {"status": "ready"}
        except Exception:
            return JSONResponse(status_code=503, content={"status": "not_ready"})

    app.include_router(build_telegram_router(settings, session_factory))
    app.include_router(build_admin_router(settings, session_factory))
    return app


app = create_app()
