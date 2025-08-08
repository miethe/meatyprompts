"""MP-P1-DB-002 baseline schema and indexes"""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision = 'fc8a67ff2575'
down_revision = 'd1e3b4c5f6a7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    access_enum = sa.Enum('private', 'unlisted', name='prompt_access_control')
    access_enum.create(op.get_bind(), checkfirst=True)

    op.add_column('prompts', sa.Column('owner_id', sa.dialects.postgresql.UUID(), nullable=False))
    op.create_foreign_key(None, 'prompts', 'users', ['owner_id'], ['id'])
    op.add_column('prompts', sa.Column('is_favorite', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('prompts', sa.Column('is_archived', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('prompts', sa.Column('block_count', sa.Integer(), server_default='0', nullable=False))
    op.add_column('prompts', sa.Column('embedding', Vector(1536), nullable=True))
    op.add_column('prompts', sa.Column('icon_url', sa.Text(), nullable=True))
    op.create_index('ix_prompts_owner_updated', 'prompts', ['owner_id', sa.text('updated_at DESC')])
    op.create_index(
        'ix_prompts_title_trgm',
        'prompts',
        ['title'],
        postgresql_using='gin',
        postgresql_ops={'title': 'gin_trgm_ops'},
    )
    op.create_index('ix_prompts_tags', 'prompts', ['tags'], postgresql_using='gin')

    op.alter_column(
        'prompt_versions',
        'version',
        existing_type=sa.String(),
        type_=sa.Integer(),
        postgresql_using='version::integer',
    )
    op.alter_column('prompt_versions', 'access_control', server_default=None)
    op.alter_column(
        'prompt_versions',
        'access_control',
        existing_type=sa.String(),
        type_=access_enum,
        existing_nullable=False,
        postgresql_using='access_control::prompt_access_control',
    )
    op.alter_column('prompt_versions', 'access_control', server_default='private')
    op.create_index(
        'ix_prompt_versions_prompt_desc',
        'prompt_versions',
        ['prompt_id', sa.text('version DESC')],
    )
    op.create_index(
        'ix_prompt_versions_body_trgm',
        'prompt_versions',
        ['body'],
        postgresql_using='gin',
        postgresql_ops={'body': 'gin_trgm_ops'},
    )

    op.create_table(
        'collections',
        sa.Column('id', sa.dialects.postgresql.UUID(), primary_key=True),
        sa.Column('owner_id', sa.dialects.postgresql.UUID(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('owner_id', 'name', name='uq_collections_owner_name'),
    )
    op.create_index('ix_collections_owner_name', 'collections', ['owner_id', 'name'])

    op.create_table(
        'collection_prompts',
        sa.Column('collection_id', sa.dialects.postgresql.UUID(), sa.ForeignKey('collections.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('prompt_id', sa.dialects.postgresql.UUID(), sa.ForeignKey('prompts.id', ondelete='CASCADE'), primary_key=True),
    )
    op.create_index('ix_collection_prompts_prompt_id', 'collection_prompts', ['prompt_id', 'collection_id'])

    op.create_table(
        'share_tokens',
        sa.Column('id', sa.dialects.postgresql.UUID(), primary_key=True),
        sa.Column('prompt_id', sa.dialects.postgresql.UUID(), sa.ForeignKey('prompts.id'), nullable=False),
        sa.Column('token', sa.Text(), nullable=False, unique=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('revoked_at', sa.TIMESTAMP(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('share_tokens')
    op.drop_index('ix_collection_prompts_prompt_id', table_name='collection_prompts')
    op.drop_table('collection_prompts')
    op.drop_index('ix_collections_owner_name', table_name='collections')
    op.drop_table('collections')

    op.drop_index('ix_prompt_versions_body_trgm', table_name='prompt_versions')
    op.drop_index('ix_prompt_versions_prompt_desc', table_name='prompt_versions')
    op.alter_column(
        'prompt_versions',
        'access_control',
        existing_type=sa.Enum('private', 'unlisted', name='prompt_access_control'),
        type_=sa.String(),
        existing_nullable=False,
    )
    op.alter_column(
        'prompt_versions',
        'version',
        existing_type=sa.Integer(),
        type_=sa.String(),
    )
    op.drop_index('ix_prompts_tags', table_name='prompts')
    op.drop_index('ix_prompts_title_trgm', table_name='prompts')
    op.drop_index('ix_prompts_owner_updated', table_name='prompts')
    op.drop_column('prompts', 'icon_url')
    op.drop_column('prompts', 'embedding')
    op.drop_column('prompts', 'block_count')
    op.drop_column('prompts', 'is_archived')
    op.drop_column('prompts', 'is_favorite')
    op.drop_constraint(None, 'prompts', type_='foreignkey')
    op.drop_column('prompts', 'owner_id')
    sa.Enum('private', 'unlisted', name='prompt_access_control').drop(op.get_bind(), checkfirst=False)
