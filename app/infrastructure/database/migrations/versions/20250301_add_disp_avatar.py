"""
Add display_name and avatar_url columns to users

Revision ID: 20250301_add_disp_avatar
Revises: 20250229_set_users_id_restart
Create Date: 2025-03-01 10:00:00
"""
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

revision: str = "20250301_add_disp_avatar"
down_revision: Union[str, None] = "20250229_set_users_id_restart"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column("users", sa.Column("display_name", sa.String(), nullable=True))
    op.add_column("users", sa.Column("avatar_url", sa.String(), nullable=True))

def downgrade() -> None:
    op.drop_column("users", "avatar_url")
    op.drop_column("users", "display_name")