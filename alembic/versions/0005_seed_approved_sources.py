"""seed approved source metadata in a disabled state"""

from datetime import UTC, datetime

import sqlalchemy as sa

from alembic import op

revision = "0005_seed_approved_sources"
down_revision = "0004_collection_duration"
branch_labels = None
depends_on = None


def upgrade() -> None:
    sources = sa.table(
        "sources",
        sa.column("source_key", sa.String),
        sa.column("name", sa.String),
        sa.column("enabled", sa.Boolean),
        sa.column("policy_status", sa.String),
        sa.column("access_method", sa.String),
        sa.column("terms_url", sa.String),
        sa.column("policy_verified_at", sa.DateTime),
        sa.column("minimum_poll_seconds", sa.Integer),
        sa.column("retention_days", sa.Integer),
        sa.column("description_storage_allowed", sa.Boolean),
        sa.column("attribution_required", sa.Boolean),
        sa.column("created_at", sa.DateTime),
    )
    op.bulk_insert(
        sources,
        [
            {
                "source_key": "jobicy",
                "name": "Jobicy",
                "enabled": False,
                "policy_status": "approved",
                "access_method": "public_json_api",
                "terms_url": "https://jobicy.com/",
                "policy_verified_at": datetime(2026, 10, 21, tzinfo=UTC),
                "minimum_poll_seconds": 3600,
                "retention_days": 7,
                "description_storage_allowed": True,
                "attribution_required": True,
                "created_at": datetime(2026, 10, 21, tzinfo=UTC),
            },
            {
                "source_key": "himalayas",
                "name": "Himalayas",
                "enabled": False,
                "policy_status": "approved",
                "access_method": "public_json_api",
                "terms_url": "https://himalayas.app/",
                "policy_verified_at": datetime(2026, 10, 21, tzinfo=UTC),
                "minimum_poll_seconds": 86400,
                "retention_days": None,
                "description_storage_allowed": True,
                "attribution_required": True,
                "created_at": datetime(2026, 10, 21, tzinfo=UTC),
            },
        ],
    )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM sources WHERE source_key IN ('jobicy', 'himalayas')"))
