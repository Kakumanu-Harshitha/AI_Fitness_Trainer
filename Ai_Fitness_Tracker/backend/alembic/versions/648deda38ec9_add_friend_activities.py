"""add_friend_activities

Revision ID: 648deda38ec9
Revises: b6455633a97c
Create Date: 2026-01-30 21:24:17.921586

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = '648deda38ec9'
down_revision: Union[str, Sequence[str], None] = 'b6455633a97c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('friend_activities',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('activity_type', sa.String(), nullable=False),
    sa.Column('details', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_friend_activities_id'), 'friend_activities', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_friend_activities_id'), table_name='friend_activities')
    op.drop_table('friend_activities')
