# Roadmap — Milestones and Release Gates

## Phase 0: Planning (complete)
- [x] Choose freelance + remote contract scope with separate labels.
- [x] Choose Railway Hobby modular monolith and SQLite volume.
- [x] Define PRD, architecture, schema, sprint backlog and agent contract.

## Sprint 1 — Foundation (estimate 1–3 focused days)
Goal: deployable, secured skeleton, persistent queue, Telegram webhook, migrations, tests. **No live source collection yet.** See `backlog/SPRINT_01.md`.
Exit: deployment + restart + auth + migration + queue tests passed.

## Sprint 2 — Collection Engine (estimate 2–4 days)
Goal: policy-check candidate sources; implement at least two approved adapters, normalization, classification, upsert and collection metrics.
Exit: two legal source integrations (or documented blockers), stable ingestion and dedup tests.

## Sprint 3 — Analytics & Reporting (estimate 2–3 days)
Goal: curated skill taxonomy, extraction, top-20 stats, daily Telegram reports, by-source/type filters.
Exit: useful reports based on real collected records, tested aggregates and clear sampling caveats.

## Sprint 4 — Reliability & Freshness (estimate 1–3 days)
Goal: new-listing alerts, lag metrics, operational alerts, source-specific rate policy, retention and backup checks.
Exit: 7-day observation, measured lag and cost, reliable retry/outbox behavior.

## v0.2 — Market Intelligence Expansion
Budget distributions, skill co-occurrence, source comparisons, export with data-rights enforcement, lightweight dashboard if justified.

## v0.3 — Personalized Ranking
Explicit preference profile, weighted scoring, evidence-backed matching, feedback labels; optional embeddings only after benchmarking. Data volume alone is not labeled preference data.

## v0.4+ — Proposal / Applications
Draft proposals using verified portfolio facts, explicit user approval and permitted platform submission integrations; no autonomous outreach by default.

## Release gates
G1 foundation stability; G2 source compliance; G3 data quality; G4 analytics correctness; G5 budget measurement. Never skip G2 to hit a date.
