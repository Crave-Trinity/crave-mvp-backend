"""
Create voice_logs table

Revision ID: 20250302_create_voice_logs_table
Revises: 20250301_add_disp_avatar
Create Date: 2025-03-02 12:00:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "20250302_create_voice_logs_table"
down_revision: Union[str, None] = "20250301_add_disp_avatar"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "voice_logs",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("user_id", sa.Integer, nullable=False, index=True),
        sa.Column("file_path", sa.String, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=False), server_default=sa.text("now()"), nullable=False),
        sa.Column("transcribed_text", sa.String, nullable=True),
        sa.Column("transcription_status", sa.String, nullable=True),
        sa.Column("is_deleted", sa.Boolean, server_default="false", nullable=False),
    )
    op.execute('CREATE INDEX IF NOT EXISTS "ix_voice_logs_user_id" ON voice_logs ("user_id")')

def downgrade() -> None:
    op.execute('DROP INDEX IF EXISTS "ix_voice_logs_user_id"')
    op.drop_table("voice_logs")