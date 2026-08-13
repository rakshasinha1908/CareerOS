"""simplify companies for career pages

Revision ID: d668139cb2a0
Revises: f733ef695445
Create Date: 2026-08-13 19:52:46.722869

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d668139cb2a0"
down_revision: Union[str, Sequence[str], None] = "f733ef695445"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Reuse the existing website data as the career page URL.
    op.alter_column(
        "companies",
        "website",
        new_column_name="career_url",
        existing_type=sa.String(length=500),
        existing_nullable=True,
    )

    # Every company must have a career page in the new model.
    op.alter_column(
        "companies",
        "career_url",
        existing_type=sa.String(length=500),
        nullable=False,
    )

    # Remove company metadata that is not part of the V0 model.
    op.drop_column("companies", "notes")
    op.drop_column("companies", "size")
    op.drop_column("companies", "industry")
    op.drop_column("companies", "headquarters")


def downgrade() -> None:
    """Downgrade schema."""

    # Restore the old column name.
    op.alter_column(
        "companies",
        "career_url",
        new_column_name="website",
        existing_type=sa.String(length=500),
        existing_nullable=False,
    )

    op.alter_column(
        "companies",
        "website",
        existing_type=sa.String(length=500),
        nullable=True,
    )

    # Restore removed columns.
    op.add_column(
        "companies",
        sa.Column(
            "headquarters",
            sa.String(length=200),
            nullable=True,
        ),
    )

    op.add_column(
        "companies",
        sa.Column(
            "industry",
            sa.String(length=150),
            nullable=True,
        ),
    )

    op.add_column(
        "companies",
        sa.Column(
            "size",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "companies",
        sa.Column(
            "notes",
            sa.Text(),
            nullable=True,
        ),
    )