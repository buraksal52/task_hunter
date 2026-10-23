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

### MVP source integration priority — reviewed 2026-10-23

The requested priority is preserved, but implementation remains gated by the official source policy:

1. **Freelancer.com — priority approval work, not yet implementable.** Obtain express written permission and a read-only project-listing scope covering polling, fields, retention, attribution and in-app display. Until then, no API client, scraper, Playwright flow or stored Freelancer data is allowed.
2. **Himalayas — confirmed and already implemented.** Keep the approved adapter, daily full-feed cadence, expiry cleanup, attribution and normalized classification. Add regression coverage for the current paginated API contract if the adapter changes.
3. **Remote OK — priority policy clarification.** The official FAQ permits JSON/RSS feeds and requires credit plus an original-job link. Confirm retention, polling, description storage and takedown behavior before adding the adapter. After approval, use a read-only normalized feed adapter.
4. **Upwork — pending API approval.** Do not scrape, automate the website or persist data before the registered API application is approved.
5. **Fiverr — blocked.** No automated collection; only a separately reviewed authorized export/manual input path.

All adapters map source records into the canonical job model and never write to the source or submit applications. Playwright remains an isolated P2 option only for a source that explicitly permits browser automation. OCR and visual/LLM agents are outside the MVP.

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
