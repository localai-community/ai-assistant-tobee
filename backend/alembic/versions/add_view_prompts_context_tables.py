"""add_view_prompts_context_tables

Revision ID: add_view_prompts_context
Revises: bb12bbfc360e
Create Date: 2025-10-17 21:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_view_prompts_context'
down_revision: Union[str, None] = '79febacb41c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create user_questions table
    op.create_table('user_questions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('conversation_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('question_timestamp', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_questions_conversation_id'), 'user_questions', ['conversation_id'], unique=False)
    op.create_index(op.f('ix_user_questions_user_id'), 'user_questions', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_questions_question_timestamp'), 'user_questions', ['question_timestamp'], unique=False)

    # Create ai_prompts table
    op.create_table('ai_prompts',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('question_id', sa.String(length=36), nullable=False),
        sa.Column('conversation_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('final_prompt', sa.Text(), nullable=False),
        sa.Column('model_used', sa.String(length=50), nullable=False),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('max_tokens', sa.Integer(), nullable=True),
        sa.Column('prompt_timestamp', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['question_id'], ['user_questions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_prompts_question_id'), 'ai_prompts', ['question_id'], unique=False)
    op.create_index(op.f('ix_ai_prompts_conversation_id'), 'ai_prompts', ['conversation_id'], unique=False)
    op.create_index(op.f('ix_ai_prompts_user_id'), 'ai_prompts', ['user_id'], unique=False)

    # Create context_awareness_data table
    op.create_table('context_awareness_data',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('question_id', sa.String(length=36), nullable=False),
        sa.Column('conversation_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('context_type', sa.String(length=50), nullable=False),
        sa.Column('context_data', sa.JSON(), nullable=False),
        sa.Column('context_metadata', sa.JSON(), nullable=True),
        sa.Column('context_timestamp', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['question_id'], ['user_questions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_context_awareness_data_question_id'), 'context_awareness_data', ['question_id'], unique=False)
    op.create_index(op.f('ix_context_awareness_data_conversation_id'), 'context_awareness_data', ['conversation_id'], unique=False)
    op.create_index(op.f('ix_context_awareness_data_user_id'), 'context_awareness_data', ['user_id'], unique=False)
    op.create_index(op.f('ix_context_awareness_data_context_type'), 'context_awareness_data', ['context_type'], unique=False)


def downgrade() -> None:
    # Drop context_awareness_data table
    op.drop_index(op.f('ix_context_awareness_data_context_type'), table_name='context_awareness_data')
    op.drop_index(op.f('ix_context_awareness_data_user_id'), table_name='context_awareness_data')
    op.drop_index(op.f('ix_context_awareness_data_conversation_id'), table_name='context_awareness_data')
    op.drop_index(op.f('ix_context_awareness_data_question_id'), table_name='context_awareness_data')
    op.drop_table('context_awareness_data')

    # Drop ai_prompts table
    op.drop_index(op.f('ix_ai_prompts_user_id'), table_name='ai_prompts')
    op.drop_index(op.f('ix_ai_prompts_conversation_id'), table_name='ai_prompts')
    op.drop_index(op.f('ix_ai_prompts_question_id'), table_name='ai_prompts')
    op.drop_table('ai_prompts')

    # Drop user_questions table
    op.drop_index(op.f('ix_user_questions_question_timestamp'), table_name='user_questions')
    op.drop_index(op.f('ix_user_questions_user_id'), table_name='user_questions')
    op.drop_index(op.f('ix_user_questions_conversation_id'), table_name='user_questions')
    op.drop_table('user_questions')
