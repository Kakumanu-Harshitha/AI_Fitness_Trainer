"""add_totp_fields

Revision ID: ef85a51ff520
Revises: 5373d95b3c76
Create Date: 2026-02-22 19:27:29.128787

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ef85a51ff520'
down_revision: Union[str, Sequence[str], None] = '5373d95b3c76'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('totp_secret', sa.String(), nullable=True))
    op.add_column('users', sa.Column('is_totp_enabled', sa.Integer(), server_default='0', nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'is_totp_enabled')
    op.drop_column('users', 'totp_secret')
