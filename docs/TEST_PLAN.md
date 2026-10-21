# Test Strategy and Acceptance Matrix

## Unit tests
- Classification: freelance project/hourly, remote contract, full-time, internship, contradictory/unknown.
- Normalization: missing budget, unknown publication date, timezone conversion, canonical URLs.
- Skill extraction: Python/FastAPI/Next.js/C++/C#/Golang; reject false positive English `go` and `C`.
- Dedup: same source ID idempotent; cross-source matches not merged blindly.
- Analytics: top 20 skills, source/type segmentation, unknown exclusion, currencies not mixed.

## Integration tests
- In-memory/test-file SQLite migration and foreign key checks.
- Lease acquisition and expiry recovery; one active same-source run.
- Webhook secret validation, unauthorized user/chat rejection, duplicate `update_id` handling.
- Telegram send failure and outbox retry; no double event creation.
- Mocked API/RSS via respx and fixture feeds; 429, 500, malformed records, timeouts, zero results.

## Deployment acceptance
- Health endpoints respond after Railway deployment.
- Volume-backed DB survives restart.
- `/hunt` enqueues a durable task; before approved adapters it reports no approved sources, not fake success.
- Source credentials and Telegram secrets absent from logs.
- Observe RAM, CPU, disk and usage; confirm spend alarms.

## Compliance gate
For each enabled adapter, attach reviewed terms/doc links, allowed fields, retention, polling interval and test evidence. Do not mark integration complete without approval.
