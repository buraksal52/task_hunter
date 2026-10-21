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
