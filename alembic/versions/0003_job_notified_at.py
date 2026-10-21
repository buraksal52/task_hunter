"""track successful notification acknowledgement"""

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision = "0003_job_notified_at"
down_revision = "0002_job_expiry"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if "notified_at" not in {
        column["name"] for column in inspect(op.get_bind()).get_columns("jobs")
    }:
        op.add_column("jobs", sa.Column("notified_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("jobs", "notified_at")
