"""add_user_sessions_table

Revision ID: 79febacb41c1
Revises: c2756f59bd25
Create Date: 2025-10-16 19:19:27.443944

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '79febacb41c1'
down_revision: Union[str, None] = 'c2756f59bd25'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create user_sessions table
    op.create_table('user_sessions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('session_key', sa.String(length=100), nullable=False),
        sa.Column('current_user_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['current_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_sessions_current_user_id'), 'user_sessions', ['current_user_id'], unique=False)
    op.create_index(op.f('ix_user_sessions_session_key'), 'user_sessions', ['session_key'], unique=True)


def downgrade() -> None:
    # Drop user_sessions table
    op.drop_index(op.f('ix_user_sessions_session_key'), table_name='user_sessions')
    op.drop_index(op.f('ix_user_sessions_current_user_id'), table_name='user_sessions')
    op.drop_table('user_sessions')
