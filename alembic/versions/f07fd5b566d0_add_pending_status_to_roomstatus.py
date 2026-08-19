"""add pending status to roomstatus

Revision ID: f07fd5b566d0
Revises: f58063793051
Create Date: 2026-08-19 19:44:22.380669

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'f07fd5b566d0'
down_revision: Union[str, Sequence[str], None] = 'f58063793051'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE roomstatus ADD VALUE 'PENDING';")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("UPDATE room_booking SET status = 'CANCELLED' WHERE status = 'PENDING';")
    op.execute("ALTER TYPE roomstatus RENAME TO roomstatus_old;")
    op.execute("CREATE TYPE roomstatus AS ENUM ('CONFIRMED', 'CANCELLED');")
    op.execute("ALTER TABLE room_booking " \
    "ALTER COLUMN status TYPE roomstatus " \
    "USING status::text::roomstatus;")
    op.execute("DROP TYPE roomstatus_old;")
