# Product Requirements Document (PRD) — v0.1

## Problem
Freelance opportunities are scattered across platforms and often time-sensitive. It is hard to understand which technologies are requested, how budgets vary and which opportunities match a developer's skills. Before building a personalized application agent, establish a reliable market dataset.

## User and jobs to be done
Primary user: one technically capable developer seeking freelance and remote contract software work. Needs to (1) observe the market, (2) identify demand for skills and technology combinations, (3) receive trustworthy periodic summaries, (4) preserve history for future ranking.

## Scope
**Include:** `freelance_project`, `freelance_hourly`, `remote_contract`.
**Exclude from primary analytics:** `remote_full_time`, `internship`.
**Quarantine:** `unknown` (visible separately; not counted as qualifying jobs).
`remote_policy` is independent: `remote`, `hybrid`, `onsite`, `unknown`. Remote contract requires remote policy `remote`; freelance project/hourly may be remote or unspecified but onsite-only items should be filtered for this user's market view. Preserve raw classification evidence.

## Functional requirements
| ID | Requirement | Priority | Verification |
|---|---|---|---|
| FR-01 | Fetch listings from >=2 policy-approved sources | P0 | Two successful source integration tests |
| FR-02 | Per-source scheduling, quotas and backoff | P0 | No overlapping same-source runs |
| FR-03 | Normalize/validate listing data | P0 | Contract tests with missing fields |
| FR-04 | Classify engagement and remote policy with evidence | P0 | Fixtures covering all enums |
| FR-05 | Persist and deduplicate listings | P0 | Repeated ingestion creates one job |
| FR-06 | Extract canonical skills with evidence | P0 | Dictionary-based fixture tests |
| FR-07 | Compute counts, top 20 skills, by-source/by-type splits | P0 | Deterministic analytics tests |
| FR-08 | Telegram `/start`, `/hunt`, `/stats`, `/sources`, `/health` | P0 | Authorized webhook integration tests |
| FR-09 | Daily Telegram summary | P0 | Scheduled outbox delivery test |
| FR-10 | Track collection errors and freshness | P0 | Run metrics query |
| FR-11 | Budgets and skill co-occurrence | P1 | Analytics endpoint tests |
| FR-12 | Immediate notifications for newly found relevant jobs | P1 | Configurable rule test |
| FR-13 | JSON/CSV export with source rights respected | P1 | Export test |
| FR-14 | Playwright adapter for explicitly permitted source | P2 | Source approval + resource benchmark |

## Nonfunctional requirements
- **Cost:** target within Railway Hobby $5 included monthly usage; track total workspace usage and set alerts/hard limits as supported. No promise of zero overage.
- **Reliability:** persistent DB and queued tasks, restart recovery, idempotent ingest, retry/backoff.
- **Security:** server-only secrets, allowlisted Telegram user/chat, authenticated admin API, webhook secret.
- **Quality:** unknown values remain null, classify uncertain listings as unknown, explain skill matches.
- **Observability:** collection run status, fetched/new/updated/skipped counts, latency and error codes.
- **Compliance:** source-by-source allowed methods, retention, attribution and access controls.
- **Analytics honesty:** describe dataset as sampled sources, not representative of the whole freelance market.

## Out of scope v0.1
LLM, trained ranking model, embeddings, proposal generation, autonomous applications, browser vision agent, Flutter client, multi-tenant accounts, payments, unapproved scraping.

## Acceptance criteria
- At least two approved sources ingest real records (subject to access/permission; otherwise explicit blocker).
- Re-ingest is idempotent; `first_seen_at` preserved; `last_seen_at` updated.
- Engagement types and remote policies are stored independently.
- Railway restart retains database and pending tasks.
- `/hunt` queues work; `/stats` returns source/type-separated counts and top 20 skills.
- Daily report sends once per reporting window using outbox deduplication.
- All tests pass and resource consumption is measured.

## Success metrics
Unique eligible jobs/day, source coverage, collection success %, dedup rate, missing-field rate, published-to-first-seen delay (where published time exists), first-seen-to-notification delay, RAM/CPU and monthly usage. No arbitrary job-volume target.
