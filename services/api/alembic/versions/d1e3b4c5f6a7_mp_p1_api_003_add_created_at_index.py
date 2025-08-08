"""MP-P1-API-003 add index on prompt_versions.created_at"""

from alembic import op
import sqlalchemy as sa

revision = 'd1e3b4c5f6a7'
down_revision = 'b1e8d8e2c3d0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        'ix_prompt_versions_created_at',
        'prompt_versions',
        ['created_at'],
    )


def downgrade() -> None:
    op.drop_index('ix_prompt_versions_created_at', table_name='prompt_versions')
