# Implementation Guide: Prompt Creation (Manual + AI-Automated Scaffolding)

This document outlines the steps required to implement the "Prompt Creation" feature, as described in User Story WP-PRM-UI-002.

## 1. Database Schema

Create a new Alembic migration to add the `prompts` and `prompt_versions` tables to the database.

**Migration File:** `services/api/alembic/versions/3f8c8a7b4f5c_create_prompts_and_prompt_versions_tables.py`

```python
"""create prompts and prompt_versions tables

Revision ID: 3f8c8a7b4f5c
Revises:
Create Date: 2025-08-05 14:30:33.773753

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3f8c8a7b4f5c'
down_revision = None
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
        sa.ForeignKeyConstraint(['latest_version_id'], ['prompt_versions.id'], ),
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
        sa.ForeignKeyConstraint(['prompt_id'], ['prompts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prompt_versions_prompt_id_version'), 'prompt_versions', ['prompt_id', 'version'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_prompt_versions_prompt_id_version'), table_name='prompt_versions')
    op.drop_table('prompt_versions')
    op.drop_table('prompts')
```

**Run the migration:**

```bash
python -m alembic -c services/api/alembic.ini upgrade head
```

## 2. Backend (FastAPI)

Create Pydantic models, a new `prompts` router, and a service layer to handle the business logic of creating a new prompt.

**(Further implementation details for the backend, frontend, and testing would be included here.)**
