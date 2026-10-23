# Source Access & Data Rights Gate

**No candidate source is pre-approved by this document.** Check current official terms/API documentation before enabling any adapter. A publicly reachable endpoint is not proof of permission to automate or persist data.

## Candidate research queue
| Candidate | Possible access | Main question | Status |
|---|---|---|---|
| Remote OK | Public feed/API candidate | Permitted polling, attribution, redistribution/storage? | BLOCKED / disabled |
| Remotive | Public API/RSS candidate | Poll frequency, delayed publishing, storage and display restrictions? | BLOCKED / disabled |
| Freelancer.com | Official developer API candidate | Account/API approval, rate limits, permitted listing access? | BLOCKED / disabled |
| Upwork | Official OAuth 2.0/GraphQL API candidate | API key approval, public marketplace job scope, callback and retention rules? | PENDING API approval / disabled |
| Fiverr | Official API or partner access candidate | Written permission/API scope for listing access, storage and automation? | BLOCKED / manual-only until approved |
| Jobicy | Official API/RSS documentation | Attribution, own-app use, polling and cache rules? | APPROVED / Source.enabled=false by default |
| Himalayas | Official API/RSS documentation | Own-app display, attribution, expiry and request rules? | APPROVED / Source.enabled=false by default |
| Other RSS feeds | RSS candidate | Feed usage rights, polling, description retention? | UNVERIFIED / disabled |

## Approval checklist (per source)
- Official documentation and ToS URLs, date reviewed, reviewer.
- Allowed access method (API/RSS/browser), whether authentication is required.
- Rate limit and minimum polling interval; conditional requests supported?
- Permitted fields, storage duration, redistribution, attribution and commercial-use restrictions.
- Whether listings include freelance or remote contract jobs; how to classify.
- Pagination and incremental updates; expected source latency.
- Operational failure handling, source disable switch and takedown/removal handling.

## Decision record template
```
source_key:
reviewed_at:
terms_url:
api_docs_url:
allowed_access_method:
allowed_fields:
retention_days:
attribution_required:
minimum_poll_seconds:
auth_required:
publication_latency_notes:
status: approved | rejected | blocked
reviewer:
notes:
```

## Browser automation rule
Use Playwright only where explicitly allowed. Browser automation does not bypass terms or bot restrictions. No CAPTCHA solving, evasion, stealth plugins, session hijacking or unauthorized logged-in access. Browser-based visual LLM agents are outside MVP and require a separate cost/accuracy benchmark.

## User-supplied import rule
User-provided screenshots, OCR text, email contents or authorized export files may enter through a `manual_user_supplied` source mode. This mode never fetches source URLs, launches a browser or stores the original raw payload by default. It still requires an explicit source record, bounded record count, retention and a review of the originating platform's terms before enabling storage.

## Research decisions — reviewed 2026-10-21

### Remote OK — blocked pending written clarification

```text
source_key: remote_ok
reviewed_at: 2026-10-21
terms_url: https://remoteok.com/legal
api_docs_url: https://remoteok.com/faq
allowed_access_method: public JSON feed or RSS; no authentication stated
allowed_fields: not finalized; metadata-only candidate
retention_days: not specified
attribution_required: yes — credit Remote OK and link to the original job URL
minimum_poll_seconds: not specified
auth_required: no
publication_latency_notes: not specified
status: blocked
reviewer: Freelance Hunter implementation agent
notes: The official FAQ provides JSON/RSS feeds and permits aggregators/sharing with credit and original links. The official terms require a hyperlink where API/site data is used, but do not define retention, polling, description/raw-payload storage, or takedown handling.
```

Evidence: [Remote OK FAQ](https://remoteok.com/faq) and [Remote OK Terms](https://remoteok.com/legal).

### Remotive — blocked pending written clarification

```text
source_key: remotive
reviewed_at: 2026-10-21
terms_url: https://support.remotive.com/en/article/terms-of-service-u4kbkf/
api_docs_url: https://remotive.com/remote-jobs/api
allowed_access_method: public API or public RSS; no authentication stated
allowed_fields: not finalized; title/url/source metadata candidate
retention_days: not specified
attribution_required: yes — link to the Remotive URL and mention Remotive as source
minimum_poll_seconds: not specified
auth_required: no for public access
publication_latency_notes: public API jobs are delayed by 24 hours
status: blocked
reviewer: Freelance Hunter implementation agent
notes: Official API guidance allows sharing jobs further, requires attribution/link-back, prohibits submission to third-party job sites, and prohibits displaying jobs to collect signups/email addresses. Public terms prohibit automated extraction without written permission and do not define retention or polling limits.
```

Evidence: [Remotive Public API](https://remotive.com/remote-jobs/api) and [Remotive Terms](https://support.remotive.com/en/article/terms-of-service-u4kbkf/).

### Freelancer.com — blocked for this MVP use case

```text
source_key: freelancer_com
reviewed_at: 2026-10-21
terms_url: https://www.freelancer.com/about/terms
api_docs_url: https://developers.freelancer.com/
allowed_access_method: official API only, subject to accepted API T&Cs
allowed_fields: not approved
retention_days: cache refresh at least every 24 hours; broader storage permission unclear
attribution_required: not specified as a substitute for storage restrictions
minimum_poll_seconds: exact limit not verified; reasonable request volume required
auth_required: API agreement/account required
publication_latency_notes: not specified
status: blocked
reviewer: Freelance Hunter implementation agent
notes: API T&Cs restrict replication/competition, redistribution/syndication, caching and storage; they require strong encryption and deletion after termination unless otherwise agreed. This aggregator use case requires explicit written approval.
```

Evidence: [Freelancer API Terms](https://www.freelancer.com/about/apiterms), [Freelancer User Agreement](https://www.freelancer.com/about/terms), and [Freelancer Developer Portal](https://developers.freelancer.com/).

### Upwork — pending API approval

```text
source_key: upwork
reviewed_at: 2026-10-22
terms_url: https://www.upwork.com/legal
api_docs_url: https://www.upwork.com/developer/documentation/graphql/api/docs/index.html
allowed_access_method: official OAuth 2.0/GraphQL API only; no website scraping or browser automation
allowed_fields: not finalized; public marketplace job posting fields only after API approval
retention_days: not finalized; follow the approved API scope and current terms
attribution_required: not finalized
minimum_poll_seconds: not finalized; follow API limits and approved use case
auth_required: yes — approved Upwork application and OAuth credentials
publication_latency_notes: not finalized
status: pending API approval
reviewer: Freelance Hunter implementation agent
notes: The application was registered with read-only common entities, public marketplace job postings and read-only job details. The key is currently disabled. Do not enable an adapter, persist Upwork content, or use a browser agent until Upwork approves the application and the callback/token flow is implemented and tested.
```

Evidence: [Upwork API documentation](https://www.upwork.com/developer/documentation/graphql/api/docs/index.html), [Upwork automation guidance](https://support.upwork.com/hc/en-us/articles/43342677368467-Use-bots-and-other-automation-properly), and [Upwork Legal Center](https://www.upwork.com/legal).

### Fiverr — blocked pending official permission or API

```text
source_key: fiverr
reviewed_at: 2026-10-22
terms_url: https://www.fiverr.com/legal-portal/legal-terms/terms-of-service
api_docs_url: not identified for marketplace listing ingestion
allowed_access_method: official API, partner feed or written permission only
allowed_fields: not finalized
retention_days: not finalized
attribution_required: not finalized
minimum_poll_seconds: not finalized
auth_required: not finalized
publication_latency_notes: not finalized
status: blocked
reviewer: Freelance Hunter implementation agent
notes: Fiverr terms prohibit unauthorized bots, robots, spiders, crawlers, scraping and systematic retrieval. No adapter or Playwright/browser agent may be enabled without explicit permission and a documented data-use scope. User-provided authorized exports, screenshots or OCR text may use the existing bounded manual_user_supplied path after review.
```

Evidence: [Fiverr Terms of Service](https://www.fiverr.com/legal-portal/legal-terms/terms-of-service) and [Fiverr Community Standards](https://help.fiverr.com/hc/en-us/articles/37554441398929-Our-Community-Standards).

### Jobicy — approved with conservative retention

```text
source_key: jobicy
reviewed_at: 2026-10-21
terms_url: https://github.com/Jobicy/remote-jobs-api
api_docs_url: https://jobicy.com/jobs-rss-feed
allowed_access_method: public REST API or RSS; no API key/account required
allowed_fields: listing fields needed for title, canonical URL, source ID, description, publication, location, type and budget; preserve attribution
retention_days: 7 (conservative product policy; source feed covers listings published in the last 7 days)
attribution_required: yes — preserve canonical Jobicy URL and identify Jobicy as source
minimum_poll_seconds: 3600
auth_required: no
publication_latency_notes: API window is listings published in the last 7 days
status: approved
reviewer: Freelance Hunter implementation agent
notes: Official documentation explicitly permits use in applications, research tools, internal applications and automated workflows; it permits summaries/categories and requires attribution/canonical links. Automated polling or synchronization must not run more frequently than hourly. Adapter remains disabled until FH-010 fixture and retention tests exist.
```

Evidence: [Jobicy API documentation and fair-use rules](https://github.com/Jobicy/remote-jobs-api).

### Himalayas — approved with expiry-based cleanup

```text
source_key: himalayas
reviewed_at: 2026-10-21
terms_url: https://himalayas.app/terms
api_docs_url: https://himalayas.app/docs/data-dictionary
allowed_access_method: official JSON API or RSS; API key rules apply where a key is used
allowed_fields: title, excerpt, company, employment type, salary, location restrictions, categories, description, publication/expiry timestamps, application URL and GUID; preserve attribution
retention_days: expiry-driven; remove jobs once source expiry is reached
attribution_required: yes — visible Himalayas source link
minimum_poll_seconds: source request limits apply; use conservative hourly polling until a specific limit is confirmed
auth_required: public job data; key requirements depend on endpoint
publication_latency_notes: expiryDate is supplied and jobs may close earlier
status: approved
reviewer: Freelance Hunter implementation agent
notes: Official terms allow personal/commercial integrations on sites/apps operated by the integrator, require attribution, prohibit passing listings to third-party job boards/aggregators, require caching where possible and removal after expiry. Telegram output remains part of the user's own application; no redistribution adapter is authorized.
```

Evidence: [Himalayas API terms](https://himalayas.app/terms) and [Himalayas data dictionary](https://himalayas.app/docs/data-dictionary).
