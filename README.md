# Freelance Hunter — Planning Pack v0.1

**Status:** Sprint 1–3 implementation in progress · **Date:** 2026-10-21 · **Language:** English for coding agents; product decisions agreed in Turkish.

## Mission
Build a single-user, low-cost **Freelance + Remote Contract Market Intelligence** service. Collect permitted listings, normalize and deduplicate them, classify engagement types, extract technical skills, persist history, and deliver Telegram reports. Later add personalized ML ranking and human-approved proposals.

## Start here (agent reading order)
1. `AGENTS.md` — operating contract and guardrails.
2. `docs/PRD.md` — scope, requirements and acceptance criteria.
3. `docs/ARCHITECTURE.md` — runtime and data flow.
4. `docs/TECH_SPEC.md` — interfaces, processing rules, reliability.
5. `docs/DATA_MODEL.md` and `schemas/schema.sql` — database contract.
6. `docs/SOURCE_POLICY.md` — mandatory pre-connector source review.
7. `docs/ROADMAP.md` and `backlog/BACKLOG.md` — sequence and priorities.
8. `backlog/SPRINT_01.md` — first implementation sprint.

## Non-negotiable decisions
- **Scope:** freelance project, freelance hourly and remote contract listings; label each separately. Exclude employee full-time and internships; retain uncertain classifications separately.
- **Hosting:** existing Railway Hobby plan, target total included usage <= $5/month (not a guarantee). One service and one instance for MVP.
- **Runtime:** Python 3.12, FastAPI, httpx, SQLAlchemy 2, Alembic, SQLite on persistent Railway volume, APScheduler, Telegram Bot HTTP API.
- **No LLM or browser agent in MVP.** Playwright is an optional later adapter only where explicitly permitted.
- **Source permission first:** do not collect/store data from a source until its terms, rate limits and storage conditions have been verified and documented.
- **No autonomous applications or outreach.** Later submissions require explicit human approval and platform authorization.

## Repository workflow
This pack is documentation-only. Copy its files into a new `freelance-hunter` repository. Implement Sprint 1 first. Never treat example source names as approved sources.

## Local setup

Requirements: Python 3.12 and `uv`.

```bash
cp .env.example .env
uv sync --dev
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

Run checks with `uv run ruff check .` and `uv run pytest`. The default configuration keeps collection and immediate alerts disabled and has no approved sources. `/hunt` reports that no approved sources are enabled; it does not claim a scan occurred. Analytics reports use UTC first-seen windows, exclude onsite-only jobs from eligible rankings, show unknown classifications separately, and keep budget currencies/types separate. Authenticated `/api/v1/sources` reports last success, freshness and latest run errors. `/api/v1/jobs/export` provides authenticated rights-aware JSON/CSV exports. Set `INSTANT_ALERTS_ENABLED=true` only when Telegram allowlist configuration is ready.

Current MVP source gate: Himalayas is the confirmed implemented adapter; Freelancer.com is a priority approval task blocked pending express written permission; Remote OK feed access is documented but its retention/polling/takedown rules still require clarification. Upwork remains pending API approval, Fiverr remains blocked, and no scraping, OCR, visual LLM agent or browser automation bypass is part of the MVP.

For a consistent live SQLite backup, call `app.db.backup.backup_sqlite` and verify the artifact with `verify_sqlite_backup`; keep backups outside the application volume when possible.

Non-API source material can use the authenticated `POST /api/v1/imports/manual` endpoint with a source configured as `manual_user_supplied`. It accepts user-provided records only; it does not fetch links, run Playwright or bypass source protections.

## Deployment baseline

Deploy one container/replica on Railway using `railway.toml`. Create a persistent volume mounted at `/data`, set `DATABASE_URL=sqlite:////data/hunter.db`, and use `/health/live` as the health check. Set secrets only as Railway variables. Telegram webhook registration and delivery require verified production secrets; neither is claimed by local tests. Railway supplies the runtime `PORT`; the Docker start command uses it and falls back to `8000` locally.

See [docs/DEPLOY_RAILWAY.md](docs/DEPLOY_RAILWAY.md) for the exact Railway variables, volume setup and safe activation order.

## MVP definition of done
Two **verified-permitted** sources, persistent normalized listings, engagement classification, deduplication, basic skill statistics, Telegram commands and daily report, collection health, restart recovery, tests and measured Railway usage. If two sources cannot be legally integrated, report blocker instead of violating policies.
