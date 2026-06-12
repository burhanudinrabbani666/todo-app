"""add phone number column

Revision ID: 32cdd9976a38
Revises: eb6d37adeb40
Create Date: 2026-06-11 20:51:10.924700

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "32cdd9976a38"
down_revision: Union[str, Sequence[str], None] = "eb6d37adeb40"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users", sa.Column("phone_number", sa.Integer, nullable=False)
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
