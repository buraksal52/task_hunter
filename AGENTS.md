# Agent Instructions — Freelance Hunter

You are the implementation agent for Freelance Hunter. Treat `docs/PRD.md`, `docs/TECH_SPEC.md`, `docs/DATA_MODEL.md`, `docs/SOURCE_POLICY.md`, and the current sprint as authoritative. Report conflicts; do not silently broaden scope.

## Execution protocol
1. Read the docs and identify the active sprint. Produce a short implementation plan and list assumptions.
2. Work on one backlog ticket at a time; use the stated acceptance criteria.
3. Add or update tests with each feature. Run `ruff check`, `pytest`, and migration checks before marking done.
4. Update `backlog/SPRINT_01.md` checkboxes, `docs/DECISIONS.md`, and README when behavior changes.
5. At the end of each work session, report: completed IDs, tests run/results, blockers, costs/risks, next ticket.
6. Never claim deployment, policy approval, API access or Telegram delivery unless verified.

## Safety and correctness
- No CAPTCHA bypass, anti-bot evasion, unauthorized scraping, or automation against platform terms.
- Source terms must be checked before writing an enabled adapter. Unknown policy means **disabled**.
- Never log tokens, API keys, complete private Telegram payloads or personal identifiers.
- Telegram webhook must validate `X-Telegram-Bot-Api-Secret-Token` and chat/user allowlist; reject unauthorized commands.
- All administrative API endpoints must authenticate. Keep `/health/live` minimal.
- Use UTC-aware datetimes; nullable published/budget fields stay null, never invented.
- A source returning zero results does not prove prior jobs have closed.
- Preserve jobs across process restarts via volume; do not rely on FastAPI BackgroundTasks for durable work.
- One SQLite writer pattern; WAL, busy timeout, bounded transactions, durable task leases, and notification outbox.
- Store source content only to the extent permitted; enforce retention per source.
- Do not add LLM, Celery, Redis, PostgreSQL, microservices, Flutter, browser automation, or auto-apply in Sprint 1.
- Cost is a constraint: benchmark resource use and avoid always-loaded ML models or Chromium.

## Definition of done per ticket
Implementation + tests + documentation updates + passing checks + no exposed secrets + clear verification steps. Never mark a ticket complete for a stub alone unless the ticket explicitly calls for a stub.
