"""MP-TENANCY-DB-001 tenancy foundations"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '20250901_tenancy_foundations'
down_revision = '20250808_add_avatar_url_to_users'
branch_labels = None
depends_on = None

def upgrade() -> None:
    org_table = op.create_table(
        'organizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_table(
        'teams',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_table(
        'principals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('type', sa.Text(), nullable=False, server_default='user'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_table(
        'org_members',
        sa.Column('org_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('principal_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('principals.id', ondelete='CASCADE'), primary_key=True),
    )

    op.create_table(
        'team_members',
        sa.Column('team_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('teams.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('principal_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('principals.id', ondelete='CASCADE'), primary_key=True),
    )

    op.create_table(
        'workspaces',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    resource_type = sa.Enum('prompt','collection','model','integration','tag', name='resource_type')
    resource_visibility = sa.Enum('private','internal','public', name='resource_visibility')
    resource_type.create(op.get_bind(), checkfirst=True)
    resource_visibility.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'resources',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', resource_type, nullable=False),
        sa.Column('visibility', resource_visibility, nullable=False, server_default='private'),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_resources_tenant_workspace_updated', 'resources', ['tenant_id','workspace_id', sa.text('updated_at DESC')])
    op.create_index('ix_resources_tenant_type', 'resources', ['tenant_id','type'])
    op.create_index('ix_resources_tenant_visibility', 'resources', ['tenant_id','visibility'])

    op.create_table(
        'resource_acl',
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('resources.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('principal_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('principals.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('permission', sa.Text(), nullable=False, server_default='read'),
    )

    op.create_table(
        'audit_log',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.Text(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.execute("""
    CREATE OR REPLACE FUNCTION current_tenant() RETURNS uuid AS $$
        SELECT current_setting('app.tenant_id', true)::uuid
    $$ LANGUAGE SQL STABLE;
    """)

    op.execute("""
    CREATE OR REPLACE FUNCTION caller_principals() RETURNS uuid[] AS $$
        SELECT array_agg(id) FROM principals WHERE user_id = current_setting('app.user_id', true)::uuid
    $$ LANGUAGE SQL STABLE;
    """)

    op.execute("""
    CREATE POLICY resources_read ON resources FOR SELECT
        USING (tenant_id = current_setting('app.tenant_id', true)::uuid);
    """)
    op.execute("""
    CREATE POLICY resources_write ON resources FOR UPDATE
        USING (tenant_id = current_setting('app.tenant_id', true)::uuid);
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS resources_write ON resources")
    op.execute("DROP POLICY IF EXISTS resources_read ON resources")
    op.execute("DROP FUNCTION IF EXISTS caller_principals")
    op.execute("DROP FUNCTION IF EXISTS current_tenant")
    op.drop_table('audit_log')
    op.drop_table('resource_acl')
    op.drop_index('ix_resources_tenant_visibility', table_name='resources')
    op.drop_index('ix_resources_tenant_type', table_name='resources')
    op.drop_index('ix_resources_tenant_workspace_updated', table_name='resources')
    op.drop_table('resources')
    sa.Enum(name='resource_visibility').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='resource_type').drop(op.get_bind(), checkfirst=True)
    op.drop_table('workspaces')
    op.drop_table('team_members')
    op.drop_table('org_members')
    op.drop_table('principals')
    op.drop_table('teams')
    op.drop_table('organizations')
