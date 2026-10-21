# Product Backlog — Ordered

Priority P0 required for MVP, P1 next release, P2 optional. Each item must be tracked in the active sprint before implementation.

| ID | Priority | Epic | Task | Dependencies | Acceptance |
|---|---|---|---|---|---|
| FH-001 | P0 | Foundation | Repo/tooling + CI | none | lint/tests run in CI |
| FH-002 | P0 | Foundation | Config and secret handling | FH-001 | missing secrets handled safely |
| FH-003 | P0 | Foundation | FastAPI lifecycle and health | FH-001 | liveness/readiness tests |
| FH-004 | P0 | Database | SQLAlchemy schema + Alembic | FH-001 | migrations upgrade cleanly |
| FH-005 | P0 | Queue | Durable collection tasks + leases | FH-004 | restart and concurrency tests |
| FH-006 | P0 | Telegram | Authenticated webhook and commands | FH-002,FH-005 | unauthorized/duplicate updates rejected |
| FH-007 | P0 | Deployment | Docker/Railway volume | FH-003,FH-004 | restart persistence demonstrated |
| FH-008 | P0 | QA | Tests, CI and operations docs | FH-001..007 | green suite and documented setup |
| FH-009 | P0 | Sources | Review source policies | none | 2 approved or documented blockers |
| FH-010 | P0 | Sources | First approved adapter | FH-009 | fixture + live smoke test |
| FH-011 | P0 | Sources | Second approved adapter | FH-009 | fixture + live smoke test |
| FH-012 | P0 | Ingestion | Normalize + engagement classification | FH-010 | fixtures pass |
| FH-013 | P0 | Ingestion | Idempotent upsert and snapshots | FH-004,FH-012 | no duplicates on repeat |
| FH-014 | P0 | Scheduler | Per-source schedule, rate limits and retries | FH-005,FH-009 | no overlapping polls |
| FH-015 | P0 | Analytics | Canonical skill taxonomy and extractor | FH-013 | precision fixtures pass |
| FH-016 | P0 | Analytics | Top-20 skills and source/type counts | FH-015 | deterministic aggregate tests |
| FH-017 | P0 | Telegram | Daily report via outbox | FH-006,FH-016 | once-per-window intent |
| FH-018 | P0 | Operations | Source health and freshness metrics | FH-014 | latency/error queries |
| FH-019 | P1 | Alerts | Instant new job notifications | FH-017 | configurable eligibility filter |
| FH-020 | P1 | Analytics | Budgets + skill co-occurrence | FH-016 | source/currency caveats |
| FH-021 | P1 | Export | Rights-aware CSV/JSON | FH-013,FH-009 | retention/export rules enforced |
| FH-022 | P2 | Browser | Permitted Playwright adapter benchmark | FH-009 | documented permission and memory cost |
| FH-023 | P2 | ML | Weighted personalized ranker | FH-016 | explainable scores, labeled feedback |
| FH-024 | P2 | Proposals | Human-approved proposal drafts | FH-023 | no unsupported claims |
| FH-025 | P2 | Applications | Authorized submission integration | FH-024 | explicit approval + idempotency |
