from sqlalchemy import select

from app.analytics.skills import EXTRACTOR_VERSION, extract_skills
from app.collection.ingest import ingest_raw_jobs
from app.db.models import JobSkill, Skill, Source
from app.sources.base import RawJob


def test_skill_extractor_handles_aliases_and_collision_guards():
    matches = {
        item["canonical_name"]
        for item in extract_skills(
            "Build a Next.js app with React, TypeScript, Node.js, C++ and C#. Golang is useful."
        )
    }
    assert {"Next.js", "React", "TypeScript", "Node.js", "C++", "C#", "Go"} <= matches
    assert "Java" not in matches
    assert not extract_skills("Please go to the office and write C code")


def test_ingest_persists_versioned_job_skills(client):
    with client.app.state.session_factory() as session:
        source = Source(
            source_key="jobicy",
            name="Jobicy",
            enabled=True,
            policy_status="approved",
            description_storage_allowed=True,
        )
        session.add(source)
        session.commit()
        ingest_raw_jobs(
            session,
            source,
            [
                RawJob(
                    source_key="jobicy",
                    external_id="skill-1",
                    url="https://example.test/1",
                    title="Python FastAPI",
                    description="Docker and PostgreSQL",
                )
            ],
        )
        rows = session.execute(
            select(Skill.canonical_name, JobSkill.confidence, JobSkill.extractor_version).join(
                JobSkill, JobSkill.skill_id == Skill.id
            )
        ).all()
        assert {row[0] for row in rows} >= {"Python", "FastAPI", "Docker", "PostgreSQL"}
        assert all(row[1] == 1.0 and row[2] == EXTRACTOR_VERSION for row in rows)
