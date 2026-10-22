# Architecture Decision Records

## ADR-001 — Single Railway modular monolith
**Accepted.** Existing Hobby plan, single user, low traffic. Avoid multiple billable services. Revisit on measured resource pressure.

## ADR-002 — SQLite on persistent volume
**Accepted.** Single writer/instance, WAL, migration and consistent backup. Revisit if concurrency/multi-instance requires PostgreSQL.

## ADR-003 — API/RSS first; no browser agent in MVP
**Accepted.** More predictable, cheaper, simpler to test. Browser automation requires explicit source permission and cost benchmark.

## ADR-004 — Data collection before ML ranking
**Accepted.** Gather and analyze legal listings first. Later use explicit user labels to train personalized models.

## ADR-005 — Separate engagement and remote labels
**Accepted.** `freelance_project`, `freelance_hourly`, `remote_contract`, excluded employment types, plus independent remote policy.

## ADR-006 — Durable SQLite queue/outbox
**Accepted.** Avoid ephemeral FastAPI background tasks for jobs and delivery intent; at-least-once execution and idempotent effects.

## Open decisions
- Which two sources pass current policy verification?
- Exact report delivery hour and polling intervals after source review.
- Whether full descriptions may be retained per source.
- What additional Railway workloads share the monthly usage allowance?

## ADR-007 — Sprint 1 source gate
**Accepted.** The scheduler and worker are present but have no live adapters. Tasks are durably queued and honestly marked skipped until a source has a reviewed policy record and an enabled adapter. This prevents a public endpoint from being treated as permission to automate or retain data.

## ADR-008 — Sprint 2 source policy gate
**Accepted.** On 2026-10-21, Remote OK, Remotive, Freelancer.com, Jobicy and Himalayas were reviewed against official materials. Jobicy and Himalayas pass a bounded policy gate with attribution and source-specific retention rules; their adapter classes are enabled, but database source rows remain disabled by default until an operator explicitly enables them. Remote OK and Remotive lack sufficient retention/polling/storage clarity, while Freelancer.com has explicit restrictions that conflict with this aggregator-style use case.

## ADR-009 — Sprint 3 analytics scope
**Accepted.** Analytics uses UTC first-seen windows. Eligible counts and skill rankings include freelance project/hourly and remote contract jobs, exclude onsite-only jobs, and keep unknown classifications visible but out of eligible rankings. Reports explicitly describe the result as an approved-source sample.

## ADR-010 — Budget analytics caveats
**Accepted.** Budget aggregates never combine currencies or budget types. Missing budget fields remain absent, and skill co-occurrence counts only consider eligible jobs in the selected UTC first-seen window.

## ADR-011 — Rights-aware exports
**Accepted.** Export endpoints expose normalized fields only, require admin authentication, omit descriptions when the source policy disallows description storage, and reapply source expiry/retention filters at export time. CSV uses an empty description cell for restricted sources rather than leaking stored content.

## ADR-012 — User-supplied source mode
**Accepted.** Non-API integrations may enter through a bounded `manual_user_supplied` path only. The path accepts user-provided records, screenshots/OCR output or authorized exports after external review; it never fetches URLs, launches a browser or persists raw payloads by default.

## ADR-013 — Notification acknowledgement semantics
**Accepted.** `jobs.notified_at` is written only after Telegram API acknowledgement for a `telegram.new_job` event. Daily reports do not mark individual jobs as notified; failed sends remain pending with bounded retry delay.

## ADR-014 — Upwork integration approval gate
**Accepted.** Upwork is a pending candidate, not an approved source. The registered application requests only read-only common entities, public marketplace job postings and read-only job details. The API key is currently disabled, so no Upwork adapter, OAuth token persistence, browser automation or job collection may be enabled. After approval, implement and test the registered callback URL, state validation, server-side token handling, source-specific retention and rate limits before adding the source row.

## ADR-014 — Structured collection/notification logging
**Accepted.** `collect_source` now emits one structured JSON log line per completed collection run (`run_id`, `source_key`, `duration_ms`, fetched/new/updated/skipped counts, `error_code`), at `WARNING` for `skipped`/`failed` runs and `INFO` for `succeeded` runs. Outbox delivery failures log `error_code` only. Exception text and payload bodies (which may contain source/Telegram URLs) are never logged, only stored on `collection_runs.error_message` for internal inspection; this satisfies the TECH_SPEC observability requirement without risking token/URL leakage. Closes the previously unimplemented logging gap identified in repo review.
