"""MP-P1-COLL-010 add collections tables"""
from alembic import op
import sqlalchemy as sa

revision = 'e3b42cd1d5ab'
down_revision = '20250808_add_avatar_url_to_users'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'collections',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('owner_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_collections_owner_name', 'collections', ['owner_id', 'name'], unique=True)
    op.create_index('ix_collections_owner_updated', 'collections', ['owner_id', sa.text('updated_at DESC')])

    op.create_table(
        'collection_prompts',
        sa.Column('collection_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('collections.id', ondelete='CASCADE'), nullable=False, primary_key=True),
        sa.Column('prompt_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('prompts.id', ondelete='CASCADE'), nullable=False, primary_key=True),
    )
    op.create_index('ix_collection_prompts_prompt', 'collection_prompts', ['prompt_id'])
    op.create_index('ix_collection_prompts_collection', 'collection_prompts', ['collection_id'])


def downgrade() -> None:
    op.drop_index('ix_collection_prompts_collection', table_name='collection_prompts')
    op.drop_index('ix_collection_prompts_prompt', table_name='collection_prompts')
    op.drop_table('collection_prompts')
    op.drop_index('ix_collections_owner_updated', table_name='collections')
    op.drop_index('ix_collections_owner_name', table_name='collections')
    op.drop_table('collections')
