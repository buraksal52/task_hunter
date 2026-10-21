# Technical Specification — v0.1

## Stack
Python 3.12, uv, FastAPI, Uvicorn, Pydantic v2 + pydantic-settings, httpx, feedparser, SQLAlchemy 2, Alembic, SQLite (WAL), APScheduler, pytest, pytest-asyncio, respx, Ruff. Telegram Bot HTTP API via httpx. Docker on Railway.

## Core interfaces
```python
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
    raw_payload: dict | None = None  # never persist unless source policy permits


class SourceAdapter(Protocol):
    source_key: str

    async def fetch_jobs(self, since: datetime | None, limit: int) -> list[RawJob]: ...
```
Each adapter also exposes policy metadata: `allowed_method`, `minimum_poll_seconds`, `allows_description_storage`, `retention_days`, `attribution_required`, `verified_at`, `enabled`. Default `enabled=False` until approved.

## Ingestion algorithm
1. Claim scheduled task with a lease; create/start `collection_run`.
2. Validate source is approved and within rate limits.
3. Fetch with explicit timeouts, user-agent/attribution where required, bounded pages and bounded record count.
4. Normalize: stable source ID, canonical URL, sanitized title, optional description, budget and currency, dates, engagement and remote policy, confidence/evidence.
5. Enforce storage policy; hash permitted canonical content; transactionally upsert by `(source_id, external_id)`; preserve `first_seen_at`; update `last_seen_at`.
6. Add snapshot only when allowed and content hash changes. Extract skills with versioned dictionary and evidence; don't infer unmentioned skills.
7. Write counts/error codes and complete task; enqueue report events where appropriate.

The current collection engine implements this boundary with Jobicy and Himalayas adapters, UTC-aware `expires_at`, source-specific retention cleanup, idempotent content-hash snapshots, and a single APScheduler tick with `max_instances=1`. Runtime collection stays disabled unless both `COLLECTION_ENABLED=true` and a source row has `enabled=true` and `policy_status=approved`.

## Classification
Deterministic ordered rules + explicit source metadata. Do not classify based solely on keyword `remote` or `contract` without context. Priority: explicit source type > structured employment field > carefully tested text patterns; contradictory evidence => `unknown`. Store `classification_confidence` and `classification_evidence`.

## Skill extraction
Case-insensitive alias matching with token boundaries; protect collisions (`Go` vs English verb, `R` vs letter, `C` vs letter). `Go` only from explicit technology context or `Golang`; handle `Next.js`, `C++`, `C#`, `Node.js`. Save extractor version. Start with ~40 curated canonical skills and aliases. Measure precision with fixtures.

## API contract
| Method | Route | Auth | Response |
|---|---|---|---|
| GET | `/health/live` | none | 200 `{"status":"ok"}` |
| GET | `/health/ready` | none | 200/503 minimal readiness |
| POST | `/telegram/webhook` | Telegram secret + allowlist | 200 quickly |
| GET | `/api/v1/stats` | API key | aggregated counts |
| GET | `/api/v1/jobs` | API key | paginated jobs with filters |
| GET | `/api/v1/sources` | API key | source health |
| POST | `/api/v1/collection-runs` | API key | 202 + queued task id |

Pagination must have bounded page size; never return raw source payloads by default. `/hunt` enqueues one run per source or a batch with deduped task keys. `/stats` includes period, source, engagement type, sample size and unknown count.

## Telegram commands
`/start` intro, `/hunt` enqueue scan, `/stats` summary, `/sources` status, `/health` lightweight health. Ignore unauthorized users/chats. Register webhook using HTTPS Railway URL, Telegram bot token and separate webhook secret. Verify secret with constant-time comparison. Prevent replay/duplicate processing using Telegram `update_id` unique storage or bounded retention.

## SQLite operational settings
Use `PRAGMA journal_mode=WAL`, `busy_timeout=5000`, `foreign_keys=ON`. Short write transactions; indexes in schema. DB on persistent volume, not ephemeral container FS. Do not copy live DB alone without WAL-consistent backup; use SQLite backup API or safe checkpoint/backup strategy. Monitor file growth and retention.

## Retry and idempotency
Source request retries only for transient network/429/5xx with rate-limit-aware delay and jitter; cap attempts. Unique task idempotency key per source/scheduled window; no concurrent same-source fetch. Unique notification event keys. `sent_at` means Telegram API acknowledged request, not that user read message.

## Observability
Structured JSON logs with `run_id`, `source_key`, duration, counts, error_code; redact tokens and URLs with credentials. Health endpoints must not expose DB contents or credentials. Basic metrics via DB queries; no paid monitoring dependency.

## Configuration example
`DATABASE_URL=sqlite:////data/hunter.db`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`, `TELEGRAM_ALLOWED_USER_ID`, `TELEGRAM_ALLOWED_CHAT_ID`, `ADMIN_API_KEY`, `APP_TIMEZONE=Europe/Istanbul`, `COLLECTION_ENABLED=false`, `DAILY_REPORT_HOUR=18`. Secrets in Railway variables; never commit `.env`.
