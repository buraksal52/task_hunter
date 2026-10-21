from datetime import datetime
from typing import Protocol

from pydantic import BaseModel, HttpUrl


class RawJob(BaseModel):
    source_key: str
    external_id: str | None = None
    url: HttpUrl
    title: str
    description: str | None = None
    published_at: datetime | None = None
    expires_at: datetime | None = None
    raw_payload: dict | None = None


class SourceAdapter(Protocol):
    source_key: str
    enabled: bool

    async def fetch_jobs(self, since: datetime | None, limit: int) -> list[RawJob]: ...
