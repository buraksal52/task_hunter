# Source Access & Data Rights Gate

**No candidate source is pre-approved by this document.** Check current official terms/API documentation before enabling any adapter. A publicly reachable endpoint is not proof of permission to automate or persist data.

## Candidate research queue
| Candidate | Possible access | Main question | Status |
|---|---|---|---|
| Remote OK | Public feed/API candidate | Permitted polling, attribution, redistribution/storage? | UNVERIFIED / disabled |
| Remotive | Public API candidate | Poll frequency, delayed publishing, storage and display restrictions? | UNVERIFIED / disabled |
| Freelancer.com | Official developer API candidate | Account/API approval, rate limits, permitted listing access? | UNVERIFIED / disabled |
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
