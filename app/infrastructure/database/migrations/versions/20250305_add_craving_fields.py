"""
Add missing craving fields to match the front-end CravingEntity

Revision ID: 20250305_add_craving_fields
Revises: 20250302_create_voice_logs_table
Create Date: 2025-03-05
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20250305_add_craving_fields"
down_revision = "20250302_create_voice_logs_table"
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Ensure the pgcrypto extension is enabled for gen_random_uuid()
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    
    # Convert existing `intensity` column to float
    op.alter_column(
        "cravings",
        "intensity",
        existing_type=sa.Integer(),
        type_=sa.Float(precision=53),
        existing_nullable=False,
        postgresql_using="intensity::double precision"
    )

    # Add new columns
    op.add_column("cravings", sa.Column(
        "craving_uuid",
        postgresql.UUID(as_uuid=True),
        nullable=False,
        server_default=sa.text("gen_random_uuid()")
    ))
    op.create_unique_constraint("uq_cravings_craving_uuid", "cravings", ["craving_uuid"])
    op.create_index("ix_cravings_craving_uuid", "cravings", ["craving_uuid"])

    op.add_column("cravings", sa.Column("confidence_to_resist", sa.Float(precision=53), nullable=True))
    op.add_column("cravings", sa.Column("emotions", postgresql.JSON, nullable=True))
    op.add_column("cravings", sa.Column("is_archived", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("cravings", sa.Column(
        "timestamp",
        sa.DateTime(timezone=True),
        nullable=True,  # temporarily allow null
        server_default=sa.text("now()")
    ))

    # Backfill timestamp for existing rows
    op.execute("UPDATE cravings SET timestamp = created_at WHERE timestamp IS NULL")

    # Alter column to be non-nullable now that data is present
    op.alter_column("cravings", "timestamp", nullable=False)

def downgrade() -> None:
    op.alter_column(
        "cravings",
        "intensity",
        existing_type=sa.Float(precision=53),
        type_=sa.Integer(),
        existing_nullable=False,
        postgresql_using="intensity::integer"
    )
    op.drop_column("cravings", "timestamp")
    op.drop_column("cravings", "is_archived")
    op.drop_column("cravings", "emotions")
    op.drop_column("cravings", "confidence_to_resist")
    op.drop_index("ix_cravings_craving_uuid", table_name="cravings")
    op.drop_constraint("uq_cravings_craving_uuid", "cravings", type_="unique")
    op.drop_column("cravings", "craving_uuid")