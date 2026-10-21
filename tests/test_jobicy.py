from datetime import UTC, datetime

import httpx
import respx

from app.sources.jobicy import JobicyAdapter


@respx.mock
async def test_jobicy_adapter_parses_bounded_public_response():
    route = respx.get("https://jobicy.test/api/jobs").mock(
        return_value=httpx.Response(
            200,
            json={
                "jobs": [
                    {
                        "id": 123,
                        "url": "https://jobicy.test/jobs/123",
                        "jobTitle": "Senior Python Engineer",
                        "jobDescription": "Build APIs",
                        "pubDate": "2026-10-21T09:00:00+00:00",
                    }
                ]
            },
        )
    )
    async with httpx.AsyncClient() as client:
        jobs = await JobicyAdapter(client=client, base_url="https://jobicy.test").fetch_jobs(
            since=None, limit=999
        )
    assert route.calls[0].request.url.params["count"] == "200"
    assert jobs[0].external_id == "123"
    assert jobs[0].title == "Senior Python Engineer"


@respx.mock
async def test_jobicy_adapter_filters_records_at_or_before_since():
    respx.get("https://jobicy.test/api/jobs").mock(
        return_value=httpx.Response(
            200,
            json={
                "jobs": [
                    {
                        "id": 123,
                        "url": "https://jobicy.test/jobs/123",
                        "jobTitle": "Old job",
                        "pubDate": "2026-10-20T09:00:00+00:00",
                    }
                ]
            },
        )
    )
    async with httpx.AsyncClient() as client:
        jobs = await JobicyAdapter(client=client, base_url="https://jobicy.test").fetch_jobs(
            since=datetime(2026, 10, 20, 9, 0, tzinfo=UTC), limit=10
        )
    assert jobs == []
