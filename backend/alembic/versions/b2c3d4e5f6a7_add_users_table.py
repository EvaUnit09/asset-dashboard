"""Add users table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2025-01-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table (skip if exists)
    from sqlalchemy import inspect
    from alembic import context
    
    conn = context.get_bind()
    inspector = inspect(conn)
    
    if 'user' not in inspector.get_table_names():
        op.create_table(
            'user',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('first_name', sa.String(), nullable=True),
            sa.Column('last_name', sa.String(), nullable=True),
            sa.Column('username', sa.String(), nullable=True),
            sa.Column('email', sa.String(), nullable=True),
            sa.Column('county', sa.String(), nullable=True),
            sa.Column('department_id', sa.String(), nullable=True),
            sa.Column('location_id', sa.String(), nullable=True),
            sa.Column('assets_count', sa.Integer(), nullable=True),
            sa.Column('license_count', sa.Integer(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )


def downgrade() -> None:
    # Drop users table
    op.drop_table('user') 