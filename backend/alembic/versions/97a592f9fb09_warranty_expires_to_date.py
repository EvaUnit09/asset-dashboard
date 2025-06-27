"""Warranty_expires to date

Revision ID: 97a592f9fb09
Revises: 641895e746f5
Create Date: 2025-06-26 13:49:51.240275

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '97a592f9fb09'
down_revision: Union[str, Sequence[str], None] = '641895e746f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'asset',
        'warranty_expires',
        type_=sa.Date(),
        postgresql_using='warranty_expires::date'
    )
    


def downgrade() -> None:
    op.alter_column(
        'asset',
        'warranty_expires',
        type_=sa.String(),
        postgresql_using='warranty_expires::text'
    )
