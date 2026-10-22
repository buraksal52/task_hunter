# Sprint 4 — Reliability & Freshness (in progress)

- [x] FH-019: Configurable immediate alerts for newly found eligible jobs via deduplicated outbox.
- [x] FH-020: Budget analytics and skill co-occurrence with source/currency caveats.
- [x] FH-021: Rights-aware CSV/JSON export with retention enforcement.

**Gate:** alert, freshness, retention and outbox restart behavior are verified without enabling unapproved sources.

## Operational gate evidence

- [x] SQLite online backup and integrity verification utility with restore test.
- [x] Daily report cron and outbox delivery worker wiring with retry/recovery tests.
- [x] Authenticated paginated `/api/v1/jobs` endpoint with bounded filters.
- [x] `expires_at` and `notified_at` synchronized across model, migrations and logical schema.
- [ ] Production 7-day observation, Railway resource measurement and real Telegram delivery verification.

## Latest verification — 2026-10-22

- Local quality gate: Ruff passed; 47 tests passed with one existing Starlette/httpx deprecation warning.
- Migration gate: Alembic upgraded an empty SQLite database to head and repeated the upgrade successfully.
- Configuration gate: `railway.toml` parsed successfully and `git diff --check` passed.
- Source initialization: approved `jobicy` and `himalayas` metadata is seeded disabled; collection still requires explicit enablement.
- Docker image gate: not completed because the local Docker daemon was unavailable; Railway deployment was not attempted because the Railway service was unavailable.
- Production gate: intentionally still open; no Railway URL, resource usage, seven-day observation or Telegram delivery is claimed.
