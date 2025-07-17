"""Add department_name to users table

Revision ID: c4d5e6f7g8h9
Revises: b2c3d4e5f6a7
Create Date: 2025-01-15 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4d5e6f7g8h9'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add department_name column to user table
    op.add_column('user', sa.Column('department_name', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove department_name column from user table
    op.drop_column('user', 'department_name') 