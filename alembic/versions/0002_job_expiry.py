"""store source-reported job expiry"""

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision = "0002_job_expiry"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if "expires_at" not in {
        column["name"] for column in inspect(op.get_bind()).get_columns("jobs")
    }:
        op.add_column("jobs", sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("jobs", "expires_at")
