"""create users table

Revision ID: 0001_create_users_table
Revises: 
Create Date: 2025-08-06

"""
from alembic import op
import sqlalchemy as sa

revision = '0001_create_users_table'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.dialects.postgresql.UUID(), primary_key=True, nullable=False),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False)
    )

def downgrade():
    op.drop_table('users')
