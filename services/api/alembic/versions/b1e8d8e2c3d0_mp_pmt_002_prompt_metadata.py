"""MP-PMT-002 expand prompt metadata"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'b1e8d8e2c3d0'
down_revision = 'a94a2ac10fe2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # prompts table
    op.add_column('prompts', sa.Column('title', sa.String(), nullable=True))
    op.add_column('prompts', sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True))
    op.add_column(
        'prompts',
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    # Set a default value for existing rows
    op.execute("UPDATE prompts SET title = 'Untitled' WHERE title IS NULL")
    # Now alter the column to be NOT NULL
    op.alter_column('prompts', 'title', nullable=False)
    op.drop_column('prompts', 'slug')
    op.drop_column('prompts', 'latest_version_id')
    op.drop_column('prompts', 'created_by')

    # prompt_versions table
    op.drop_column('prompt_versions', 'title')
    op.alter_column('prompt_versions', 'purpose', new_column_name='use_cases')
    op.drop_column('prompt_versions', 'models')
    op.drop_column('prompt_versions', 'tools')
    op.drop_column('prompt_versions', 'platforms')
    op.drop_column('prompt_versions', 'tags')
    op.drop_column('prompt_versions', 'visibility')
    op.alter_column('prompt_versions', 'version', type_=sa.String())
    op.add_column('prompt_versions', sa.Column('description', sa.String(), nullable=True))
    op.add_column('prompt_versions', sa.Column('access_control', sa.String(), nullable=False, server_default='private'))
    op.add_column('prompt_versions', sa.Column('target_models', postgresql.ARRAY(sa.String()), nullable=True))
    op.add_column('prompt_versions', sa.Column('providers', postgresql.ARRAY(sa.String()), nullable=True))
    op.add_column('prompt_versions', sa.Column('integrations', postgresql.ARRAY(sa.String()), nullable=True))
    op.add_column('prompt_versions', sa.Column('category', sa.String(), nullable=True))
    op.add_column('prompt_versions', sa.Column('complexity', sa.String(), nullable=True))
    op.add_column('prompt_versions', sa.Column('audience', sa.String(), nullable=True))
    op.add_column('prompt_versions', sa.Column('status', sa.String(), nullable=True))
    op.add_column('prompt_versions', sa.Column('input_schema', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('prompt_versions', sa.Column('output_format', sa.String(), nullable=True))
    op.add_column('prompt_versions', sa.Column('llm_parameters', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('prompt_versions', sa.Column('success_metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('prompt_versions', sa.Column('sample_input', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('prompt_versions', sa.Column('sample_output', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('prompt_versions', sa.Column('related_prompt_ids', postgresql.ARRAY(sa.UUID()), nullable=True))
    op.add_column('prompt_versions', sa.Column('link', sa.String(), nullable=True))
    op.add_column(
        'prompt_versions',
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )


def downgrade() -> None:
    op.drop_column('prompt_versions', 'updated_at')
    op.drop_column('prompt_versions', 'link')
    op.drop_column('prompt_versions', 'related_prompt_ids')
    op.drop_column('prompt_versions', 'sample_output')
    op.drop_column('prompt_versions', 'sample_input')
    op.drop_column('prompt_versions', 'success_metrics')
    op.drop_column('prompt_versions', 'llm_parameters')
    op.drop_column('prompt_versions', 'output_format')
    op.drop_column('prompt_versions', 'input_schema')
    op.drop_column('prompt_versions', 'status')
    op.drop_column('prompt_versions', 'audience')
    op.drop_column('prompt_versions', 'complexity')
    op.drop_column('prompt_versions', 'category')
    op.drop_column('prompt_versions', 'integrations')
    op.drop_column('prompt_versions', 'providers')
    op.drop_column('prompt_versions', 'target_models')
    op.drop_column('prompt_versions', 'access_control')
    op.drop_column('prompt_versions', 'description')
    op.alter_column('prompt_versions', 'version', type_=sa.INTEGER())
    op.add_column('prompt_versions', sa.Column('visibility', sa.String(), nullable=True))
    op.add_column('prompt_versions', sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True))
    op.add_column('prompt_versions', sa.Column('platforms', postgresql.ARRAY(sa.String()), nullable=True))
    op.add_column('prompt_versions', sa.Column('tools', postgresql.ARRAY(sa.String()), nullable=True))
    op.add_column('prompt_versions', sa.Column('models', postgresql.ARRAY(sa.String()), nullable=False))
    op.alter_column('prompt_versions', 'use_cases', new_column_name='purpose')
    op.add_column('prompt_versions', sa.Column('title', sa.String(), nullable=False))

    op.add_column('prompts', sa.Column('created_by', sa.UUID(), nullable=True))
    op.add_column('prompts', sa.Column('latest_version_id', sa.UUID(), nullable=True))
    op.add_column('prompts', sa.Column('slug', sa.String(), nullable=True))
    op.drop_column('prompts', 'updated_at')
    op.drop_column('prompts', 'tags')
    op.drop_column('prompts', 'title')
