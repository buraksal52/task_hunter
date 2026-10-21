# Data Model — v0.1

`schemas/schema.sql` is a **logical SQLite reference schema**; Alembic migrations generated from SQLAlchemy models are the production source of truth once implemented. Keep both synchronized.

## Entity rules
- `sources`: approved access method and retention policy; default disabled.
- `jobs`: one row per source-specific listing. Unique `(source_id, external_id)`. A missing platform ID uses stable canonical URL hash; avoid title-only IDs.
- `collection_runs`: each actual fetch attempt and outcomes.
- `collection_tasks`: persistent queue with lease and idempotency key.
- `skills` and `skill_aliases`: versionable controlled vocabulary.
- `job_skills`: extracted matches and supporting text.
- `job_snapshots`: changed-content history only if source allows storage.
- `notification_outbox`: delivery intent and retry state.
- `telegram_updates`: replay/dedup by `update_id`.
- `daily_metrics`: optional materialized aggregates; raw queries are authoritative.

## Enums
`engagement_type`: `freelance_project`, `freelance_hourly`, `remote_contract`, `remote_full_time`, `internship`, `unknown`.
`remote_policy`: `remote`, `hybrid`, `onsite`, `unknown`.
`collection status`: `queued`, `running`, `succeeded`, `failed`, `skipped`.
`notification status`: `pending`, `sending`, `sent`, `failed`.

## Time semantics
- `published_at`: source-reported publication timestamp, nullable.
- `first_seen_at`: first ingest time (immutable).
- `last_seen_at`: most recent observed appearance.
- `notified_at`: successful Telegram API acknowledgment for an immediate job notification, not a read receipt.
- Never assume listing is closed simply because a subsequent fetch omitted it.

## Budget semantics
Budget min/max nullable; `budget_type` (`fixed`, `hourly`, `unknown`), `currency` nullable; avoid mixing currencies in averages. Store original currency and values; currency conversion belongs to later analysis.

## Compliance and retention
Each source's policy controls whether descriptions, raw payloads, snapshots or derived fields can be stored. Retention cleanup must be source-aware. If rights are uncertain, only store allowed metadata or disable source.
