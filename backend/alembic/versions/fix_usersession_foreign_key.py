"""Fix UserSession foreign key to allow NULL on user delete

Revision ID: fix_usersession_fk
Revises: 79febacb41c1
Create Date: 2025-10-16 20:27:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fix_usersession_fk'
down_revision: Union[str, None] = '79febacb41c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the existing foreign key constraint
    op.drop_constraint('user_sessions_current_user_id_fkey', 'user_sessions', type_='foreignkey')
    
    # Alter the column to allow NULL
    op.alter_column('user_sessions', 'current_user_id',
               existing_type=sa.VARCHAR(length=36),
               nullable=True)
    
    # Create the new foreign key constraint with ON DELETE SET NULL
    op.create_foreign_key('user_sessions_current_user_id_fkey', 'user_sessions', 'users', 
                         ['current_user_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    # Drop the new foreign key constraint
    op.drop_constraint('user_sessions_current_user_id_fkey', 'user_sessions', type_='foreignkey')
    
    # Alter the column back to NOT NULL
    op.alter_column('user_sessions', 'current_user_id',
               existing_type=sa.VARCHAR(length=36),
               nullable=False)
    
    # Create the old foreign key constraint without ON DELETE
    op.create_foreign_key('user_sessions_current_user_id_fkey', 'user_sessions', 'users', 
                         ['current_user_id'], ['id'])
