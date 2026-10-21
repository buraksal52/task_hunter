import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Classification:
    engagement_type: str
    remote_policy: str
    confidence: float | None
    evidence: str


def classify_job(
    title: str,
    description: str | None,
    engagement_hint: str | None = None,
    remote_policy_hint: str | None = None,
) -> Classification:
    text = f"{title} {description or ''}".lower()
    remote_policy, remote_evidence = _classify_remote(text, remote_policy_hint)
    engagement, engagement_evidence = _classify_engagement(text, engagement_hint, remote_policy)
    evidence = "; ".join(item for item in (engagement_evidence, remote_evidence) if item)
    explicit = bool(engagement_hint or remote_policy_hint)
    confidence = (
        0.95 if explicit and engagement != "unknown" else 0.8 if engagement != "unknown" else None
    )
    return Classification(
        engagement, remote_policy, confidence, evidence or "no reliable classification evidence"
    )


def _classify_remote(text: str, hint: str | None) -> tuple[str, str]:
    if hint in {"remote", "hybrid", "onsite", "unknown"}:
        return hint, f"source remote policy={hint}"
    has_remote = bool(re.search(r"\bremote\b|work\s+from\s+home|distributed", text))
    has_hybrid = bool(re.search(r"\bhybrid\b", text))
    has_onsite = bool(re.search(r"\bonsite\b|on-site|on site", text))
    if (has_remote and has_onsite) or (has_hybrid and has_onsite):
        return "unknown", "contradictory remote-policy terms"
    if has_hybrid:
        return "hybrid", "text contains hybrid"
    if has_onsite:
        return "onsite", "text contains onsite"
    if has_remote:
        return "remote", "text contains remote/work from home"
    return "unknown", "no explicit remote-policy evidence"


def _classify_engagement(text: str, hint: str | None, remote_policy: str) -> tuple[str, str]:
    source = (hint or "").lower()
    if "intern" in source or re.search(r"\bintern(ship)?\b", text):
        return "internship", "source/text contains internship"
    if "full" in source and "time" in source:
        return "remote_full_time", "source marks full-time"
    if "contract" in source:
        if remote_policy == "remote":
            return "remote_contract", "source marks contract and remote policy is remote"
        return "unknown", "contract evidence without remote policy=remote"
    if "hour" in source or re.search(r"\bhourly\b", text):
        return "freelance_hourly", "source/text contains hourly"
    if "freelance" in source or re.search(r"\bfreelance\b", text):
        return "freelance_project", "source/text contains freelance"
    if "project" in source or re.search(r"\bproject\b", text):
        return "freelance_project", "source/text contains project"
    if re.search(r"\bfull[- ]time\b", text):
        return "remote_full_time", "text contains full-time"
    if re.search(r"\bcontract(?:or)?\b", text) and remote_policy == "remote":
        return "remote_contract", "text contains contract and remote policy is remote"
    if re.search(r"\bcontract(?:or)?\b", text):
        return "unknown", "contract evidence without remote policy=remote"
    return "unknown", "no reliable engagement evidence"
