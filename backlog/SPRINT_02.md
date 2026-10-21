# Sprint 2 — Source Collection Engine (planned)

- [ ] FH-009: Verify official terms/API docs, allowed fields, retention and polling for candidate sources; record approval decisions.
- [ ] FH-010: Implement first approved source adapter with mocked fixtures and a bounded live smoke test.
- [ ] FH-011: Implement second approved source adapter; if no second legal source, document blocker and find alternative.
- [ ] FH-012: Normalize/classify engagement and remote policy; store confidence/evidence and unknown separately.
- [ ] FH-013: Idempotent upsert, first/last seen semantics, source-specific snapshots/retention.
- [ ] FH-014: Per-source scheduler, quotas, retries, overlap prevention.

**Gate:** two policy-approved integrations or explicit blocker; real records persisted, tests green, no rights violations.
