# Sprint 1 — Foundation

**Goal:** production-shaped deployable skeleton; no actual source ingestion. **Estimate:** 1–3 focused days, not a commitment. **Definition of done:** all tasks checked with evidence and tests.

## Ordered tasks

### FH-001 — Repository and tooling
- [x] Create Python 3.12 project with `uv`, `pyproject.toml`, Ruff, pytest and GitHub Actions CI.
- [x] Create modular directories `app/{api,core,db,collection,sources,normalization,analytics,notifications}` and `tests`.
- [x] Add `.gitignore`, `.env.example`, README setup instructions.
**AC:** clean environment can install, lint and test.

### FH-002 — Configuration and secrets
- [x] Pydantic Settings for DB, Telegram, admin auth and timezone.
- [x] Ensure secrets absent from logs and git.
- [x] Document Railway environment variables.
**AC:** startup validates required production config; tests use safe fixtures.

### FH-003 — FastAPI lifecycle and health
- [x] Application factory/lifespan.
- [x] `/health/live` and `/health/ready`.
- [x] Structured logging with correlation IDs.
**AC:** health tests pass, readiness fails safely if DB unavailable.

### FH-004 — SQLite schema and migrations
- [x] SQLAlchemy models aligned with `docs/DATA_MODEL.md`.
- [x] Initial Alembic migration and SQLite pragmas.
- [x] Unique constraints, foreign keys and indexes.
**AC:** upgrade from empty DB; re-run migration without data loss.

### FH-005 — Durable collection queue
- [x] Queue task model, unique idempotency key, lease claim, expiry recovery.
- [x] Worker stub that marks unconfigured/disabled sources as skipped.
- [x] Scheduler stub with no live adapters enabled.
**AC:** restart simulation recovers work; two claimants cannot own same task.

### FH-006 — Telegram integration
- [x] Webhook secret header validation, user/chat allowlist, update dedup.
- [x] `/start`, `/health`, `/hunt` enqueue stub; clear response when no sources approved.
- [x] Telegram send service + outbox skeleton.
**AC:** unauthorized update rejected; authorized `/hunt` persists task or reports disabled sources honestly.

### FH-007 — Docker and Railway
- [x] Minimal Dockerfile, production startup command, healthcheck.
- [x] Persistent volume mount `/data`, DB path `/data/hunter.db`.
- [x] Document deployment, token registration and budget alert setup.
**AC:** Railway restart retains test record and pending task; only one replica.

### FH-008 — Test and documentation gate
- [x] Run Ruff and pytest; add queue, webhook, migration tests.
- [x] Update ADRs and operational instructions with actual behavior.
- [ ] Record observed memory/CPU/disk cost after deploy.
**AC:** green CI; verified manual smoke test and honest completion report.

## Sprint 1 exclusions
No real source polling, no browser automation, no LLM/ML, no auto-apply, no Flutter, no Redis/Postgres/Celery.

## End-of-sprint report template
```
Completed: FH-...
Tests: command, count, pass/fail
Deployment: URL/status (only if verified)
Database persistence: tested/not tested
Railway resource usage: observed or not yet measured
Risks/blockers:
Next: FH-009 source permission research
```

## Implementation report — 2026-10-21

```
Completed: FH-001–FH-007; FH-008 implementation, tests and documentation
Tests: uv run ruff check .; uv run pytest — 9 passed; Alembic upgrade twice — passed
Manual smoke: /health/live, /health/ready and authorized /hunt — passed locally
Deployment: not performed; no Railway URL or deployment access verified
Database persistence: migration and local SQLite persistence tested
Railway resource usage: not yet measured
Risks/blockers: Docker daemon unavailable locally; Railway deployment measurement remains external
Next: FH-009 source permission research
```
