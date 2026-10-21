"""Curated, deterministic skill taxonomy and evidence-based extraction."""

from __future__ import annotations

import re
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import JobSkill, Skill, SkillAlias

EXTRACTOR_VERSION = "taxonomy-1"


@dataclass(frozen=True)
class SkillDefinition:
    canonical_name: str
    category: str
    aliases: tuple[str, ...]


TAXONOMY: tuple[SkillDefinition, ...] = (
    SkillDefinition("Python", "language", ("python",)),
    SkillDefinition("JavaScript", "language", ("javascript", "js")),
    SkillDefinition("TypeScript", "language", ("typescript", "ts")),
    SkillDefinition("Go", "language", ("golang", "go language", "go programming")),
    SkillDefinition("Java", "language", ("java",)),
    SkillDefinition("C++", "language", ("c++", "cpp")),
    SkillDefinition("C#", "language", ("c#", "csharp")),
    SkillDefinition("Rust", "language", ("rust",)),
    SkillDefinition("PHP", "language", ("php",)),
    SkillDefinition("Ruby", "language", ("ruby",)),
    SkillDefinition("Kotlin", "language", ("kotlin",)),
    SkillDefinition("Swift", "language", ("swift",)),
    SkillDefinition("SQL", "data", ("sql",)),
    SkillDefinition("HTML", "frontend", ("html", "html5")),
    SkillDefinition("CSS", "frontend", ("css", "css3")),
    SkillDefinition("React", "frontend", ("react", "react.js", "reactjs")),
    SkillDefinition("Next.js", "frontend", ("next.js", "nextjs", "next js")),
    SkillDefinition("Vue.js", "frontend", ("vue", "vue.js", "vuejs")),
    SkillDefinition("Angular", "frontend", ("angular", "angular.js", "angularjs")),
    SkillDefinition("Node.js", "backend", ("node.js", "nodejs", "node js")),
    SkillDefinition("Express", "backend", ("express", "express.js", "expressjs")),
    SkillDefinition("FastAPI", "backend", ("fastapi", "fast api")),
    SkillDefinition("Django", "backend", ("django",)),
    SkillDefinition("Flask", "backend", ("flask",)),
    SkillDefinition(".NET", "backend", (".net", "dotnet", "asp.net", "aspnet")),
    SkillDefinition("Spring", "backend", ("spring", "spring boot", "springboot")),
    SkillDefinition("GraphQL", "backend", ("graphql",)),
    SkillDefinition("REST API", "backend", ("rest api", "restful api", "restful")),
    SkillDefinition("Docker", "devops", ("docker", "dockerized")),
    SkillDefinition("Kubernetes", "devops", ("kubernetes", "k8s")),
    SkillDefinition("Terraform", "devops", ("terraform",)),
    SkillDefinition("AWS", "cloud", ("aws", "amazon web services")),
    SkillDefinition("Azure", "cloud", ("azure", "microsoft azure")),
    SkillDefinition("GCP", "cloud", ("gcp", "google cloud", "google cloud platform")),
    SkillDefinition("PostgreSQL", "database", ("postgresql", "postgres")),
    SkillDefinition("MySQL", "database", ("mysql",)),
    SkillDefinition("MongoDB", "database", ("mongodb", "mongo")),
    SkillDefinition("Redis", "database", ("redis",)),
    SkillDefinition("Git", "tools", ("git", "github", "gitlab")),
    SkillDefinition("CI/CD", "devops", ("ci/cd", "continuous integration", "continuous delivery")),
)


def _pattern(alias: str) -> re.Pattern[str]:
    escaped = re.escape(alias.lower()).replace(r"\ ", r"\s+")
    return re.compile(rf"(?<!\w){escaped}(?!\w)", re.IGNORECASE)


def _contextual_go(text: str) -> list[tuple[str, str]]:
    patterns = (r"\b(?:golang|go\s+(?:language|programming|development|developer))\b",)
    return [
        (match.group(0), match.group(0))
        for pattern in patterns
        for match in re.finditer(pattern, text, re.I)
    ]


def extract_skills(text: str | None) -> list[dict[str, str | float]]:
    """Return unique canonical matches with short source evidence."""
    if not text:
        return []
    results: dict[str, dict[str, str | float]] = {}
    for definition in TAXONOMY:
        matches: list[re.Match[str]] = []
        for alias in definition.aliases:
            matches.extend(_pattern(alias).finditer(text))
        if definition.canonical_name == "Go":
            matches = [match for match in matches if match.group(0).lower() != "go"]
            matches.extend(
                match
                for _, value in _contextual_go(text)
                for match in [_pattern(value).search(text)]
                if match
            )
        if not matches:
            continue
        match = sorted(matches, key=lambda item: item.start())[0]
        start = max(0, match.start() - 45)
        end = min(len(text), match.end() + 45)
        results[definition.canonical_name] = {
            "canonical_name": definition.canonical_name,
            "confidence": 1.0,
            "evidence": text[start:end].strip(),
        }
    return list(results.values())


def ensure_taxonomy(session: Session) -> dict[str, Skill]:
    """Seed the curated taxonomy and aliases without creating duplicates."""
    skills: dict[str, Skill] = {}
    for definition in TAXONOMY:
        skill = session.scalar(
            select(Skill).where(Skill.canonical_name == definition.canonical_name)
        )
        if skill is None:
            skill = Skill(canonical_name=definition.canonical_name, category=definition.category)
            session.add(skill)
            session.flush()
        skills[definition.canonical_name] = skill
        existing = {
            alias.alias
            for alias in session.scalars(select(SkillAlias).where(SkillAlias.skill_id == skill.id))
        }
        for alias in definition.aliases:
            if alias not in existing:
                session.add(SkillAlias(skill_id=skill.id, alias=alias))
    session.flush()
    return skills


def persist_job_skills(session: Session, job_id: int, text: str | None) -> None:
    skills = ensure_taxonomy(session)
    session.query(JobSkill).filter(JobSkill.job_id == job_id).delete(synchronize_session=False)
    for match in extract_skills(text):
        session.add(
            JobSkill(
                job_id=job_id,
                skill_id=skills[str(match["canonical_name"])].id,
                confidence=float(match["confidence"]),
                evidence=str(match["evidence"]),
                extractor_version=EXTRACTOR_VERSION,
            )
        )
