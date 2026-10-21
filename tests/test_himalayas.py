from datetime import UTC, datetime

import httpx
import respx

from app.sources.himalayas import HimalayasAdapter


@respx.mock
async def test_himalayas_adapter_parses_expiry_and_bounded_limit():
    route = respx.get("https://himalayas.test/jobs/api").mock(
        return_value=httpx.Response(
            200,
            json={
                "jobs": [
                    {
                        "guid": "acme/python-engineer-123",
                        "title": "Python Engineer",
                        "description": "Build services",
                        "pubDate": 1792573200,
                        "expiryDate": 1795165200,
                    }
                ]
            },
        )
    )
    async with httpx.AsyncClient() as client:
        jobs = await HimalayasAdapter(client=client, base_url="https://himalayas.test").fetch_jobs(
            since=None, limit=99
        )
    assert route.calls[0].request.url.params["limit"] == "20"
    assert str(jobs[0].url) == "https://himalayas.app/jobs/acme/python-engineer-123"
    assert jobs[0].expires_at is not None


@respx.mock
async def test_himalayas_adapter_filters_jobs_at_or_before_since():
    respx.get("https://himalayas.test/jobs/api").mock(
        return_value=httpx.Response(
            200,
            json={
                "jobs": [
                    {
                        "guid": "old-job",
                        "title": "Old job",
                        "pubDate": 1792573200,
                    }
                ]
            },
        )
    )
    async with httpx.AsyncClient() as client:
        jobs = await HimalayasAdapter(client=client, base_url="https://himalayas.test").fetch_jobs(
            since=datetime.fromtimestamp(1792573200, tz=UTC), limit=5
        )
    assert jobs == []
