"""
Add oauth_provider and picture columns to users table

Revision ID: 20250306_add_oauth_cols
Revises: 20250305_add_craving_fields
Create Date: 2025-03-06 11:00:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20250306_add_oauth_columns_to_users"
down_revision = "20250305_add_craving_fields"
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add the missing OAuth-specific columns to the users table.
    op.add_column("users", sa.Column("oauth_provider", sa.String(), nullable=True))
    op.add_column("users", sa.Column("picture", sa.String(), nullable=True))

def downgrade() -> None:
    # Drop the columns if we need to roll back.
    op.drop_column("users", "picture")
    op.drop_column("users", "oauth_provider")