"""
Add avatar_url column to users table
"""
from alembic import op
import sqlalchemy as sa

revision = '20250808_add_avatar_url_to_users'
down_revision = '20250808_add_user_identities'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('avatar_url', sa.String(255), nullable=True))

def downgrade():
    op.drop_column('users', 'avatar_url')
