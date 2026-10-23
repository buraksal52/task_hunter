from datetime import UTC, datetime
from typing import Any

import httpx

from app.sources.base import RawJob


class HimalayasAdapter:
    source_key = "himalayas"
    allowed_method = "public_json_api"
    minimum_poll_seconds = 86400
    allows_description_storage = True
    retention_days = None
    attribution_required = True
    verified_at = "2026-10-23"
    enabled = True

    def __init__(
        self,
        client: httpx.AsyncClient | None = None,
        base_url: str = "https://himalayas.app",
    ):
        self.client = client
        self.base_url = base_url.rstrip("/")

    async def fetch_jobs(self, since: datetime | None, limit: int) -> list[RawJob]:
        bounded_limit = max(1, min(limit, 20))
        params = {"limit": bounded_limit}
        if self.client:
            response = await self.client.get(f"{self.base_url}/jobs/api", params=params, timeout=30)
        else:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(f"{self.base_url}/jobs/api", params=params)
        response.raise_for_status()
        payload = response.json()
        jobs = payload.get("jobs") if isinstance(payload, dict) else None
        if not isinstance(jobs, list):
            raise ValueError("Himalayas response did not contain a jobs list")
        return [job for job in (self._parse_job(item, since) for item in jobs) if job is not None]

    @staticmethod
    def _parse_job(item: Any, since: datetime | None) -> RawJob | None:
        if not isinstance(item, dict) or not item.get("guid") or not item.get("title"):
            return None
        published_at = _unix_datetime(item.get("pubDate"))
        expires_at = _unix_datetime(item.get("expiryDate"))
        if since and published_at and published_at <= since:
            return None
        guid = str(item["guid"]).lstrip("/")
        url = guid if guid.startswith("http") else f"https://himalayas.app/jobs/{guid}"
        period = str(item.get("salaryPeriod") or "").lower()
        budget_type = "hourly" if "hour" in period else "fixed" if period else "unknown"
        budget_min, budget_max = _salary_bounds(item)
        return RawJob(
            source_key="himalayas",
            external_id=str(item["guid"]),
            url=url,
            title=item["title"].strip(),
            description=item.get("description") or item.get("excerpt"),
            published_at=published_at,
            expires_at=expires_at,
            budget_type=budget_type,
            budget_min=budget_min,
            budget_max=budget_max,
            currency=item.get("currency"),
            engagement_hint=item.get("employmentType"),
            remote_policy_hint="remote",
        )


def _unix_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    return datetime.fromtimestamp(float(value), tz=UTC)


def _salary_bounds(item: dict[str, Any]) -> tuple[float | None, float | None]:
    """Support the current salary object as well as the legacy flat fields."""
    salaries = item.get("salaries")
    if isinstance(salaries, list):
        values = [salary for salary in salaries if isinstance(salary, dict)]
        minimums = [_number(salary.get("min")) for salary in values]
        maximums = [_number(salary.get("max")) for salary in values]
        minimums = [value for value in minimums if value is not None]
        maximums = [value for value in maximums if value is not None]
        if minimums or maximums:
            return (min(minimums) if minimums else None, max(maximums) if maximums else None)
    return _number(item.get("minSalary")), _number(item.get("maxSalary"))


def _number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
