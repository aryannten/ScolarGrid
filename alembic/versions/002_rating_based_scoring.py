"""rating_based_scoring

Revision ID: 002
Revises: 001
Create Date: 2026-03-26 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add cached average rating support and decimal scores."""
    op.add_column(
        "users",
        sa.Column(
            "average_rating",
            sa.DECIMAL(precision=3, scale=2),
            nullable=False,
            server_default="0.00",
        ),
    )
    op.create_check_constraint(
        "check_user_average_rating",
        "users",
        "average_rating >= 0 AND average_rating <= 5",
    )
    op.alter_column(
        "users",
        "score",
        existing_type=sa.Integer(),
        type_=sa.DECIMAL(precision=10, scale=2),
        existing_nullable=False,
        postgresql_using="score::numeric(10,2)",
    )
    op.execute("UPDATE users SET average_rating = 0.00 WHERE average_rating IS NULL")
    op.execute("UPDATE users SET score = ROUND(COALESCE(score, 0)::numeric, 2)")
    op.create_index(
        "idx_notes_uploader_status_rating",
        "notes",
        ["uploader_id", "status", "average_rating"],
        unique=False,
    )


def downgrade() -> None:
    """Revert cached average rating support and restore integer scores."""
    op.drop_index("idx_notes_uploader_status_rating", table_name="notes")
    op.alter_column(
        "users",
        "score",
        existing_type=sa.DECIMAL(precision=10, scale=2),
        type_=sa.Integer(),
        existing_nullable=False,
        postgresql_using="ROUND(score)::integer",
    )
    op.drop_constraint("check_user_average_rating", "users", type_="check")
    op.drop_column("users", "average_rating")
