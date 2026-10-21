from datetime import UTC, datetime

import httpx
import respx

from app.collection.service import collect_source
from app.db.models import Source


@respx.mock
async def test_collect_source_persists_normalized_job_and_run(client):
    respx.get("https://jobicy.com/api/jobs").mock(
        return_value=httpx.Response(
            200,
            json={
                "jobs": [
                    {
                        "id": 123,
                        "url": "https://jobicy.com/jobs/123",
                        "jobTitle": "Remote Python Contractor",
                        "jobDescription": "Build APIs",
                        "jobType": ["Contract"],
                        "pubDate": "2026-10-21T09:00:00+00:00",
                    }
                ]
            },
        )
    )
    with client.app.state.session_factory() as session:
        source = Source(
            source_key="jobicy",
            name="Jobicy",
            enabled=True,
            policy_status="approved",
            description_storage_allowed=True,
            minimum_poll_seconds=3600,
        )
        session.add(source)
        session.commit()
        run = await collect_source(session, source, datetime(2026, 10, 21, 10, tzinfo=UTC), 10)
        assert run.status == "succeeded"
        assert run.new_count == 1
        assert run.duration_ms is not None


async def test_collect_source_skips_disabled_source(client):
    with client.app.state.session_factory() as session:
        source = Source(source_key="jobicy", name="Jobicy", enabled=False, policy_status="approved")
        session.add(source)
        session.commit()
        run = await collect_source(session, source)
        assert run.status == "skipped"
        assert run.error_code == "SOURCE_DISABLED"
