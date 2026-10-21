from datetime import UTC, date, datetime

from app.analytics.queries import market_stats
from app.collection.ingest import ingest_raw_jobs
from app.db.models import Job, Source
from app.sources.base import RawJob


def test_market_stats_are_scoped_and_deterministic(client):
    with client.app.state.session_factory() as session:
        source = Source(
            source_key="jobicy",
            name="Jobicy",
            policy_status="approved",
            description_storage_allowed=True,
        )
        session.add(source)
        session.commit()
        now = datetime(2026, 10, 21, 12, tzinfo=UTC)
        ingest_raw_jobs(
            session,
            source,
            [
                RawJob(
                    source_key="jobicy",
                    external_id="eligible",
                    url="https://x/1",
                    title="Python project",
                    description="Build a FastAPI service",
                    engagement_hint="project",
                    remote_policy_hint="remote",
                    budget_type="fixed",
                    budget_min=1000,
                    budget_max=1500,
                    currency="USD",
                ),
                RawJob(
                    source_key="jobicy",
                    external_id="unknown",
                    url="https://x/2",
                    title="Python unknown",
                ),
            ],
            now,
        )
        session.add(
            Job(
                source_id=source.id,
                external_id="onsite",
                title="Python onsite",
                url="https://x/3",
                engagement_type="freelance_project",
                remote_policy="onsite",
                first_seen_at=now,
                last_seen_at=now,
            )
        )
        session.commit()
        result = market_stats(session, date(2026, 10, 21), date(2026, 10, 21))
        assert result["sample"] == {"total_jobs": 3, "eligible_jobs": 1, "unknown_jobs": 1}
        assert result["by_source"] == {"jobicy": {"freelance_project": 2, "unknown": 1}}
        assert result["top_skills"] == [
            {"skill": "FastAPI", "count": 1},
            {"skill": "Python", "count": 1},
        ]
        assert result["budget"]["groups"] == [
            {
                "currency": "USD",
                "budget_type": "fixed",
                "job_count": 1,
                "jobs_with_min": 1,
                "observed_min": 1000.0,
                "observed_max": 1500.0,
            }
        ]
        assert result["skill_cooccurrence"] == [{"skills": ["FastAPI", "Python"], "count": 1}]
        assert result["period"]["timezone"] == "UTC"


def test_market_stats_rejects_reversed_range(client):
    with client.app.state.session_factory() as session:
        try:
            market_stats(session, date(2026, 10, 22), date(2026, 10, 21))
        except ValueError as exc:
            assert "end date" in str(exc)
        else:
            raise AssertionError("expected reversed date range to fail")
