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

## Reprioritized MVP source plan — 2026-10-23

These tickets refine FH-009–FH-014 without treating an unapproved source as implemented. A source adapter may be enabled only after its acceptance criteria and the source policy record are complete.

| ID | Priority | Source | Task | Acceptance |
|---|---|---|---|---|
| FH-026 | P0 | Freelancer.com | Obtain express written permission and approved read-only API scope | Official response records allowed endpoints/fields, rate limits, attribution, retention, display and automation restrictions; no code before approval |
| FH-027 | P0 | Himalayas | Maintain the approved adapter against the current API contract | Mocked paginated/current-field fixtures cover `guid`, `applicationLink`, `pubDate`, `expiryDate`, employment type, salary and sanitized HTML; daily cadence and expiry behavior are tested |
| FH-028 | P0 | Remote OK | Resolve feed operational policy before implementation | Official clarification records polling, retention, description storage and takedown rules; only then add mocked JSON/RSS adapter and attribution tests |
| FH-029 | P1 | Source operations | Verify source-specific freshness and notification behavior | Enabled approved sources produce durable collection metrics and eligible-only new-job notifications without redistributing restricted listings |
| FH-030 | P2 | Browser | Isolated permitted Playwright adapter benchmark | Source-specific written permission, isolated process, memory/latency measurement and no CAPTCHA/anti-bot bypass |
| FH-031 | P1 | Upwork | Implement OAuth/API adapter after approval | Approval evidence, callback/state/token tests, read-only public job scope, retention/rate-limit tests; no scraping |

Explicitly out of scope for this plan: Fiverr scraping/API discovery without permission, OCR/visual LLM agents, browser automation used to bypass access controls, and auto-apply.
