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


@respx.mock
async def test_himalayas_adapter_normalizes_current_salary_shape_and_application_metadata():
    respx.get("https://himalayas.test/jobs/api").mock(
        return_value=httpx.Response(
            200,
            json={
                "jobs": [
                    {
                        "guid": "acme/contractor-123",
                        "title": "Backend Contractor",
                        "description": "<p>Build an API</p>",
                        "pubDate": 1792573200,
                        "expiryDate": 1795165200,
                        "applicationLink": "https://acme.example/apply/123",
                        "employmentType": "Contractor",
                        "salaryPeriod": "Yearly",
                        "currency": "USD",
                        "salaries": [{"min": 90000, "max": 120000}],
                    }
                ]
            },
        )
    )
    async with httpx.AsyncClient() as client:
        jobs = await HimalayasAdapter(client=client, base_url="https://himalayas.test").fetch_jobs(
            since=None, limit=5
        )
    assert jobs[0].budget_min == 90000
    assert jobs[0].budget_max == 120000
    assert jobs[0].budget_type == "fixed"
    assert jobs[0].engagement_hint == "Contractor"
    assert str(jobs[0].url) == "https://himalayas.app/jobs/acme/contractor-123"
