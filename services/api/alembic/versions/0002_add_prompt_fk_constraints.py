"""add foreign key constraints between prompts and prompt_versions

Revision ID: 0002_add_prompt_fk_constraints
Revises: 3f8c8a7b4f5c
Create Date: 2025-08-06

"""
from alembic import op
import sqlalchemy as sa

revision = '0002_add_prompt_fk_constraints'
down_revision = '3f8c8a7b4f5c'
branch_labels = None
depends_on = None

def upgrade():
    op.create_foreign_key(
        'fk_prompts_latest_version_id',
        'prompts', 'prompt_versions',
        ['latest_version_id'], ['id']
    )
    op.create_foreign_key(
        'fk_prompt_versions_prompt_id',
        'prompt_versions', 'prompts',
        ['prompt_id'], ['id'], ondelete='CASCADE'
    )

def downgrade():
    op.drop_constraint('fk_prompts_latest_version_id', 'prompts', type_='foreignkey')
    op.drop_constraint('fk_prompt_versions_prompt_id', 'prompt_versions', type_='foreignkey')
