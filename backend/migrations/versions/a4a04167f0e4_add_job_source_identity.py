"""add job source identity

Revision ID: a4a04167f0e4
Revises: fa39a0d85305
Create Date: 2026-09-02
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a4a04167f0e4"
down_revision: Union[str, Sequence[str], None] = "fa39a0d85305"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "jobs",
        sa.Column(
            "source",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "jobs",
        sa.Column(
            "source_job_id",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_jobs_company_source_source_job_id",
        "jobs",
        ["company_id", "source", "source_job_id"],
        unique=False,
    )

    op.create_index(
        "ix_jobs_company_url",
        "jobs",
        ["company_id", "url"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        "ix_jobs_company_url",
        table_name="jobs",
    )

    op.drop_index(
        "ix_jobs_company_source_source_job_id",
        table_name="jobs",
    )

    op.drop_column(
        "jobs",
        "source_job_id",
    )

    op.drop_column(
        "jobs",
        "source",
    )