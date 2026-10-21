from datetime import UTC, datetime
from typing import Any

import httpx

from app.sources.base import RawJob


class JobicyAdapter:
    source_key = "jobicy"
    allowed_method = "public_json_api"
    minimum_poll_seconds = 3600
    allows_description_storage = True
    retention_days = 7
    attribution_required = True
    verified_at = "2026-10-21"
    enabled = False

    def __init__(
        self, client: httpx.AsyncClient | None = None, base_url: str = "https://jobicy.com"
    ):
        self.client = client
        self.base_url = base_url.rstrip("/")

    async def fetch_jobs(self, since: datetime | None, limit: int) -> list[RawJob]:
        bounded_limit = max(1, min(limit, 200))
        params = {"count": bounded_limit}
        if self.client:
            response = await self.client.get(f"{self.base_url}/api/jobs", params=params, timeout=30)
        else:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(f"{self.base_url}/api/jobs", params=params)
        response.raise_for_status()
        payload = response.json()
        jobs = payload.get("jobs") if isinstance(payload, dict) else None
        if not isinstance(jobs, list):
            raise ValueError("Jobicy response did not contain a jobs list")
        return [job for job in (self._parse_job(item, since) for item in jobs) if job is not None]

    @staticmethod
    def _parse_job(item: Any, since: datetime | None) -> RawJob | None:
        if (
            not isinstance(item, dict)
            or not item.get("id")
            or not item.get("url")
            or not item.get("jobTitle")
        ):
            return None
        published_at = item.get("pubDate")
        parsed_published_at = datetime.fromisoformat(published_at) if published_at else None
        if parsed_published_at and parsed_published_at.tzinfo is None:
            parsed_published_at = parsed_published_at.replace(tzinfo=UTC)
        if since and parsed_published_at and parsed_published_at <= since:
            return None
        return RawJob(
            source_key="jobicy",
            external_id=str(item["id"]),
            url=item["url"],
            title=item["jobTitle"].strip(),
            description=item.get("jobDescription") or item.get("jobExcerpt"),
            published_at=parsed_published_at,
        )
