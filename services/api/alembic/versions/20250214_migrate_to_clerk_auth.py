"""Migrate to Clerk-based authentication"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250214_migrate_to_clerk_auth'
down_revision = 'd1e3b4c5f6a7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply Clerk auth migrations."""
    op.add_column(
        'users',
        sa.Column('clerk_user_id', sa.String(length=255), nullable=False),
    )
    op.create_unique_constraint('uq_users_clerk_user_id', 'users', ['clerk_user_id'])
    op.drop_table('user_identities')
    try:
        sa.Enum(name='authprovider').drop(op.get_bind())
    except Exception:
        pass


def downgrade() -> None:
    """Revert Clerk auth migrations."""
    op.create_table(
        'user_identities',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('provider', sa.Enum('github', 'magic', name='authprovider'), nullable=False),
        sa.Column('provider_user_id', sa.String(length=255), nullable=False),
        sa.Column('access_token_encrypted', sa.String(length=255), nullable=True),
        sa.Column('refresh_token_encrypted', sa.String(length=255), nullable=True),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.drop_constraint('uq_users_clerk_user_id', 'users', type_='unique')
    op.drop_column('users', 'clerk_user_id')
