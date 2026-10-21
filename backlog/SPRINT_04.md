# Sprint 4 — Reliability & Freshness (in progress)

- [x] FH-019: Configurable immediate alerts for newly found eligible jobs via deduplicated outbox.
- [x] FH-020: Budget analytics and skill co-occurrence with source/currency caveats.
- [x] FH-021: Rights-aware CSV/JSON export with retention enforcement.

**Gate:** alert, freshness, retention and outbox restart behavior are verified without enabling unapproved sources.

## Operational gate evidence

- [x] SQLite online backup and integrity verification utility with restore test.
- [ ] Production 7-day observation, Railway resource measurement and real Telegram delivery verification.
