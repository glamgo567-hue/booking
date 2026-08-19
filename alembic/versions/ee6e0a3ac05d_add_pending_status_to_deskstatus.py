"""add pending status to deskstatus

Revision ID: ee6e0a3ac05d
Revises: f07fd5b566d0
Create Date: 2026-08-19 21:29:22.414863

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'ee6e0a3ac05d'
down_revision: Union[str, Sequence[str], None] = 'f07fd5b566d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE deskstatus ADD VALUE 'PENDING';")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("UPDATE desk_booking SET status = 'CANCELLED' WHERE status = 'PENDING';")
    op.execute("ALTER TYPE deskstatus RENAME TO deskstatus_old;")
    op.execute("CREATE TYPE deskstatus AS ENUM ('CONFIRMED', 'CANCELLED');")
    op.execute("ALTER TABLE desk_booking " \
    "ALTER COLUMN status TYPE deskstatus " \
    "USING status::text::deskstatus;")
    op.execute("DROP TYPE deskstatus_old;")