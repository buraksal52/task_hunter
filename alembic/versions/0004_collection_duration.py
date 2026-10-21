"""store collection run duration"""

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision = "0004_collection_duration"
down_revision = "0003_job_notified_at"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if "duration_ms" not in {
        column["name"] for column in inspect(op.get_bind()).get_columns("collection_runs")
    }:
        op.add_column("collection_runs", sa.Column("duration_ms", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("collection_runs", "duration_ms")
