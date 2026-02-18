"""add_theme_to_user_settings

Revision ID: 2bdecc54941e
Revises: 5503a7add7d9
Create Date: 2026-02-19 01:23:17.902668

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2bdecc54941e'
down_revision: Union[str, None] = '5503a7add7d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user_settings', sa.Column('theme', sa.String(length=20), nullable=True))
    op.execute("UPDATE user_settings SET theme = 'system' WHERE theme IS NULL")


def downgrade() -> None:
    op.drop_column('user_settings', 'theme')
