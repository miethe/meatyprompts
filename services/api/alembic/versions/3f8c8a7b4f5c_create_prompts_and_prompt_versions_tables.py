"""create prompts and prompt_versions tables

Revision ID: 3f8c8a7b4f5c
Revises: 0001_create_users_table
Create Date: 2025-08-05 14:30:33.773753

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3f8c8a7b4f5c'
down_revision = '0001_create_users_table'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'prompts',
        sa.Column('id', sa.dialects.postgresql.UUID(), nullable=False),
        sa.Column('slug', sa.TEXT(), nullable=True),
        sa.Column('latest_version_id', sa.dialects.postgresql.UUID(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_by', sa.dialects.postgresql.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_table(
        'prompt_versions',
        sa.Column('id', sa.dialects.postgresql.UUID(), nullable=False),
        sa.Column('prompt_id', sa.dialects.postgresql.UUID(), nullable=True),
        sa.Column('version', sa.INTEGER(), nullable=False),
        sa.Column('title', sa.TEXT(), nullable=False),
        sa.Column('purpose', sa.TEXT(), nullable=True),
        sa.Column('models', sa.ARRAY(sa.TEXT()), nullable=False),
        sa.Column('tools', sa.ARRAY(sa.TEXT()), nullable=True),
        sa.Column('tags', sa.ARRAY(sa.TEXT()), nullable=True),
        sa.Column('body', sa.TEXT(), nullable=False),
        sa.Column('visibility', sa.TEXT(), server_default='private', nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prompt_versions_prompt_id_version'), 'prompt_versions', ['prompt_id', 'version'], unique=True)


def downgrade():
    op.drop_table('prompts')
    op.drop_index(op.f('ix_prompt_versions_prompt_id_version'), table_name='prompt_versions')
    op.drop_table('prompt_versions')
