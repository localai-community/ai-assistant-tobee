"""merge_heads

Revision ID: 5503a7add7d9
Revises: fix_usersession_fk, add_view_prompts_context
Create Date: 2025-10-17 21:51:21.442850

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5503a7add7d9'
down_revision: Union[str, None] = ('fix_usersession_fk', 'add_view_prompts_context')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
