"""Initial database

Revision ID: eb6d37adeb40
Revises:
Create Date: 2026-06-11 20:42:48.607846

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "eb6d37adeb40"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String(100), nullable=False),
        sa.Column("first_name", sa.String(255), nullable=False),
        sa.Column("last_name", sa.String(255), nullable=True),
        sa.Column(
            "email", sa.String(100), nullable=False, unique=True
        ),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(100), nullable=True),
        sa.Column(
            "is_active", sa.Boolean, nullable=False, default=False
        ),
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
