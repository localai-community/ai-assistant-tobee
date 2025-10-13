"""add_unified_reasoning_fields_to_user_settings

Revision ID: c2756f59bd25
Revises: add_chat_docs
Create Date: 2025-10-13 21:59:30.486113

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c2756f59bd25'
down_revision: Union[str, None] = 'add_chat_docs'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add use_unified_reasoning column
    op.add_column('user_settings', sa.Column('use_unified_reasoning', sa.Boolean(), nullable=True))
    # Set default value for existing rows
    op.execute("UPDATE user_settings SET use_unified_reasoning = 0 WHERE use_unified_reasoning IS NULL")
    
    # Add selected_reasoning_mode column
    op.add_column('user_settings', sa.Column('selected_reasoning_mode', sa.String(length=50), nullable=True))
    # Set default value for existing rows
    op.execute("UPDATE user_settings SET selected_reasoning_mode = 'auto' WHERE selected_reasoning_mode IS NULL")


def downgrade() -> None:
    # Remove the added columns
    op.drop_column('user_settings', 'selected_reasoning_mode')
    op.drop_column('user_settings', 'use_unified_reasoning')
