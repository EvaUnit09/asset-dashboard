"""Add assigned_user_name to assets table

Revision ID: d5e6f7g8h9i0
Revises: c4d5e6f7g8h9
Create Date: 2025-01-18 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5e6f7g8h9i0'
down_revision: Union[str, Sequence[str], None] = 'c4d5e6f7g8h9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add assigned_user_name column to asset table (skip if exists)
    from sqlalchemy import inspect
    from alembic import context
    
    conn = context.get_bind()
    inspector = inspect(conn)
    
    # Check if column already exists
    columns = [col['name'] for col in inspector.get_columns('asset')]
    if 'assigned_user_name' not in columns:
        op.add_column('asset', sa.Column('assigned_user_name', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove assigned_user_name column from asset table
    op.drop_column('asset', 'assigned_user_name')