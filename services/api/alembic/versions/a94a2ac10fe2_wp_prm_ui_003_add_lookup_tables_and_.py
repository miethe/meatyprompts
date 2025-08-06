"""WP-PRM-UI-003 Add lookup tables and prompt version metadata

Revision ID: a94a2ac10fe2
Revises: 91ad97bd25b5
Create Date: 2025-08-06 17:24:01.016618

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a94a2ac10fe2'
down_revision = '91ad97bd25b5'
branch_labels = None
depends_on = None


def upgrade():
    # Create lookup tables
    op.create_table('models_lookup',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('value', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('value')
    )
    op.create_table('tools_lookup',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('value', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('value')
    )
    op.create_table('platforms_lookup',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('value', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('value')
    )
    op.create_table('purposes_lookup',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('value', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('value')
    )

    # Add 'platforms' column to 'prompt_versions'
    op.add_column('prompt_versions', sa.Column('platforms', postgresql.ARRAY(sa.String()), nullable=True))

    # Alter 'purpose' column to be an array
    op.alter_column('prompt_versions', 'purpose',
               existing_type=sa.String(),
               type_=postgresql.ARRAY(sa.String()),
               existing_nullable=True,
               postgresql_using='ARRAY[purpose]')


def downgrade():
    # Alter 'purpose' column back to a single string
    op.alter_column('prompt_versions', 'purpose',
               existing_type=postgresql.ARRAY(sa.String()),
               type_=sa.String(),
               existing_nullable=True,
               postgresql_using='purpose[1]')

    # Drop 'platforms' column
    op.drop_column('prompt_versions', 'platforms')

    # Drop lookup tables
    op.drop_table('purposes_lookup')
    op.drop_table('platforms_lookup')
    op.drop_table('tools_lookup')
    op.drop_table('models_lookup')
