"""
Add user_identities table for multi-provider auth support
"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg

# revision identifiers, used by Alembic.
revision = '20250808_add_user_identities'
down_revision = 'fc8a67ff2575'  # Set to previous migration revision if needed
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'user_identities',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', pg.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('provider', sa.Enum('github', 'magic', name='authprovider'), nullable=False),
        sa.Column('provider_user_id', sa.String(255), nullable=False),
        sa.Column('access_token_encrypted', sa.String(255), nullable=True),
        sa.Column('refresh_token_encrypted', sa.String(255), nullable=True),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_unique_constraint('uq_user_identities_provider_user', 'user_identities', ['provider', 'provider_user_id'])

def downgrade():
    op.drop_constraint('uq_user_identities_provider_user', 'user_identities', type_='unique')
    op.drop_table('user_identities')
