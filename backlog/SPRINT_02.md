# Sprint 2 — Source Collection Engine (in progress)

- [x] FH-009: Verify official terms/API docs, allowed fields, retention and polling for candidate sources; record approval decisions. Five official candidates reviewed; Jobicy and Himalayas are policy-approved with conservative retention rules, while Remote OK, Remotive and Freelancer.com remain blocked.
- [x] FH-010: Implement first approved source adapter with mocked fixtures and a bounded live smoke test. Jobicy adapter parses bounded JSON responses; fixture and live smoke passed.
- [x] FH-011: Implement second approved source adapter; if no second legal source, document blocker and find alternative. Himalayas adapter preserves expiry metadata; fixture and live smoke passed.
- [x] FH-012: Normalize/classify engagement and remote policy; store confidence/evidence and unknown separately. Deterministic classification, evidence, confidence and UTC-aware normalized fields implemented.
- [x] FH-013: Idempotent upsert, first/last seen semantics, source-specific snapshots/retention. Content-hash snapshots, Jobicy 7-day retention and Himalayas expiry cleanup implemented.
- [x] FH-014: Per-source scheduler, quotas, retries, overlap prevention. APScheduler tick, source intervals, bounded task leases and transient retry/backoff implemented.

**Gate:** two policy-approved integrations or explicit blocker; real records persisted, tests green, no rights violations.

## FH-009 evidence

Reviewed 2026-10-21. Official source URLs, evidence and per-source decisions are recorded in `docs/SOURCE_POLICY.md`. Jobicy and Himalayas are approved for bounded adapters; database `Source.enabled` remains false by default and `COLLECTION_ENABLED=false` remains the safe default.

## Implementation report — 2026-10-21

```
Completed: FH-009–FH-014
Tests: uv run ruff check .; uv run pytest — 23 passed
Migration: Alembic upgrade head from empty DB and repeat upgrade — passed
Live smoke: Jobicy and Himalayas adapter fetch — 1 record each; temporary SQLite persistence — passed
Runtime safety: source rows disabled by default; collection requires explicit enablement
Risks: source terms may change; re-review before enabling new fields or changing retention
Next: Sprint 3 analytics and reporting
```
