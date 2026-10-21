-- Logical SQLite reference schema. Alembic migrations become production authority.
PRAGMA foreign_keys = ON;
CREATE TABLE sources (
 id INTEGER PRIMARY KEY, source_key TEXT NOT NULL UNIQUE, name TEXT NOT NULL,
 enabled INTEGER NOT NULL DEFAULT 0 CHECK(enabled IN (0,1)),
 policy_status TEXT NOT NULL DEFAULT 'unverified' CHECK(policy_status IN ('unverified','approved','rejected','blocked')),
 access_method TEXT, terms_url TEXT, policy_verified_at TEXT,
 minimum_poll_seconds INTEGER, retention_days INTEGER,
 description_storage_allowed INTEGER NOT NULL DEFAULT 0,
 attribution_required INTEGER NOT NULL DEFAULT 0,
 last_success_at TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE collection_runs (
 id INTEGER PRIMARY KEY, source_id INTEGER NOT NULL REFERENCES sources(id),
 status TEXT NOT NULL CHECK(status IN ('queued','running','succeeded','failed','skipped')),
 started_at TEXT, finished_at TEXT, fetched_count INTEGER NOT NULL DEFAULT 0,
 new_count INTEGER NOT NULL DEFAULT 0, updated_count INTEGER NOT NULL DEFAULT 0,
 skipped_count INTEGER NOT NULL DEFAULT 0, error_code TEXT, error_message TEXT
);
CREATE INDEX ix_collection_runs_source_started ON collection_runs(source_id, started_at);
CREATE TABLE collection_tasks (
 id INTEGER PRIMARY KEY, source_id INTEGER REFERENCES sources(id),
 run_id INTEGER REFERENCES collection_runs(id), idempotency_key TEXT NOT NULL UNIQUE,
 status TEXT NOT NULL DEFAULT 'queued' CHECK(status IN ('queued','running','succeeded','failed','skipped')),
 scheduled_at TEXT NOT NULL, lease_owner TEXT, lease_until TEXT,
 attempts INTEGER NOT NULL DEFAULT 0, max_attempts INTEGER NOT NULL DEFAULT 3,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_collection_tasks_status_schedule ON collection_tasks(status, scheduled_at);
CREATE TABLE jobs (
 id INTEGER PRIMARY KEY, source_id INTEGER NOT NULL REFERENCES sources(id),
 external_id TEXT NOT NULL, title TEXT NOT NULL, description TEXT, url TEXT NOT NULL,
 engagement_type TEXT NOT NULL DEFAULT 'unknown' CHECK(engagement_type IN ('freelance_project','freelance_hourly','remote_contract','remote_full_time','internship','unknown')),
 remote_policy TEXT NOT NULL DEFAULT 'unknown' CHECK(remote_policy IN ('remote','hybrid','onsite','unknown')),
 classification_confidence REAL, classification_evidence TEXT,
 budget_type TEXT NOT NULL DEFAULT 'unknown' CHECK(budget_type IN ('fixed','hourly','unknown')),
 budget_min REAL, budget_max REAL, currency TEXT,
 published_at TEXT, first_seen_at TEXT NOT NULL, last_seen_at TEXT NOT NULL,
 content_hash TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 UNIQUE(source_id, external_id)
);
CREATE INDEX ix_jobs_published ON jobs(published_at);
CREATE INDEX ix_jobs_first_seen ON jobs(first_seen_at);
CREATE INDEX ix_jobs_type_remote ON jobs(engagement_type, remote_policy);
CREATE TABLE skills (
 id INTEGER PRIMARY KEY, canonical_name TEXT NOT NULL UNIQUE, category TEXT NOT NULL
);
CREATE TABLE skill_aliases (
 id INTEGER PRIMARY KEY, skill_id INTEGER NOT NULL REFERENCES skills(id),
 alias TEXT NOT NULL, match_rule TEXT NOT NULL DEFAULT 'word_boundary', UNIQUE(skill_id, alias)
);
CREATE TABLE job_skills (
 job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
 skill_id INTEGER NOT NULL REFERENCES skills(id), confidence REAL,
 evidence TEXT, extractor_version TEXT NOT NULL,
 PRIMARY KEY(job_id, skill_id)
);
CREATE INDEX ix_job_skills_skill ON job_skills(skill_id);
CREATE TABLE job_snapshots (
 id INTEGER PRIMARY KEY, job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
 content_hash TEXT NOT NULL, changed_at TEXT NOT NULL, snapshot_data TEXT,
 UNIQUE(job_id, content_hash)
);
CREATE TABLE notification_outbox (
 id INTEGER PRIMARY KEY, event_key TEXT NOT NULL UNIQUE,
 event_type TEXT NOT NULL, payload_json TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','sending','sent','failed')),
 attempts INTEGER NOT NULL DEFAULT 0, next_attempt_at TEXT,
 sent_at TEXT, telegram_message_id TEXT, last_error_code TEXT,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_notification_status_next ON notification_outbox(status, next_attempt_at);
CREATE TABLE telegram_updates (
 update_id INTEGER PRIMARY KEY, received_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE daily_metrics (
 metric_date TEXT NOT NULL, source_id INTEGER REFERENCES sources(id),
 engagement_type TEXT NOT NULL, metric_key TEXT NOT NULL,
 metric_value REAL NOT NULL, computed_at TEXT NOT NULL,
 UNIQUE(metric_date, source_id, engagement_type, metric_key)
);
