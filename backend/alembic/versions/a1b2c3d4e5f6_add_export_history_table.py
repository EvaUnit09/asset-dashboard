"""Add export_history table for PDF export tracking

Revision ID: a1b2c3d4e5f6
Revises: 97a592f9fb09
Create Date: 2025-01-07 11:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '97a592f9fb09'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create export_history table
    op.create_table(
        'export_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('config_json', sa.String(), nullable=False),
        sa.Column('created_at', sa.Date(), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False),
        sa.Column('download_count', sa.Integer(), nullable=False),
        sa.Column('export_type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop export_history table
    op.drop_table('export_history') 