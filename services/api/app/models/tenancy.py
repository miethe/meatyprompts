"""Tenancy related ORM models."""
from __future__ import annotations

from enum import Enum

import sqlalchemy as sa
from sqlalchemy import Column, Enum as SAEnum, ForeignKey, Index, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as SA_UUID
from sqlalchemy.sql import func

from .prompt import Base


class OrganizationORM(Base):
    """Organization container for grouping teams and workspaces."""

    __tablename__ = "organizations"
    id = Column(SA_UUID(as_uuid=True), primary_key=True)
    name = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


class TeamORM(Base):
    """Team within an organization."""

    __tablename__ = "teams"
    id = Column(SA_UUID(as_uuid=True), primary_key=True)
    org_id = Column(SA_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


class PrincipalORM(Base):
    """Security principal representing a user or service."""

    __tablename__ = "principals"
    id = Column(SA_UUID(as_uuid=True), primary_key=True)
    user_id = Column(SA_UUID(as_uuid=True), nullable=True)
    type = Column(String, nullable=False, server_default="user")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


class OrgMemberORM(Base):
    """Link principals to organizations."""

    __tablename__ = "org_members"
    org_id = Column(SA_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True)
    principal_id = Column(SA_UUID(as_uuid=True), ForeignKey("principals.id", ondelete="CASCADE"), primary_key=True)


class TeamMemberORM(Base):
    """Link principals to teams."""

    __tablename__ = "team_members"
    team_id = Column(SA_UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), primary_key=True)
    principal_id = Column(SA_UUID(as_uuid=True), ForeignKey("principals.id", ondelete="CASCADE"), primary_key=True)


class WorkspaceORM(Base):
    """Workspaces group resources within an organization."""

    __tablename__ = "workspaces"
    id = Column(SA_UUID(as_uuid=True), primary_key=True)
    org_id = Column(SA_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


class ResourceType(str, Enum):
    """Enumeration of resource envelope types."""

    prompt = "prompt"
    collection = "collection"
    model = "model"
    integration = "integration"
    tag = "tag"


class ResourceVisibility(str, Enum):
    """Visibility of a resource."""

    private = "private"
    internal = "internal"
    public = "public"


class ResourceORM(Base):
    """Envelope for tenant-scoped resources."""

    __tablename__ = "resources"
    id = Column(SA_UUID(as_uuid=True), primary_key=True)
    tenant_id = Column(SA_UUID(as_uuid=True), nullable=False)
    workspace_id = Column(SA_UUID(as_uuid=True), nullable=False)
    type = Column(SAEnum(ResourceType, name="resource_type"), nullable=False)
    visibility = Column(SAEnum(ResourceVisibility, name="resource_visibility"), nullable=False, server_default=ResourceVisibility.private.value)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_resources_tenant_workspace_updated", "tenant_id", "workspace_id", sa.text("updated_at DESC")),
        Index("ix_resources_tenant_type", "tenant_id", "type"),
        Index("ix_resources_tenant_visibility", "tenant_id", "visibility"),
    )


class ResourceACLORM(Base):
    """Access control entries for resources."""

    __tablename__ = "resource_acl"
    resource_id = Column(SA_UUID(as_uuid=True), ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True)
    principal_id = Column(SA_UUID(as_uuid=True), ForeignKey("principals.id", ondelete="CASCADE"), primary_key=True)
    permission = Column(String, nullable=False, server_default="read")


class AuditLogORM(Base):
    """Structured audit log for resource actions."""

    __tablename__ = "audit_log"
    id = Column(sa.BigInteger, primary_key=True, autoincrement=True)  # type: ignore[name-defined]
    tenant_id = Column(SA_UUID(as_uuid=True), nullable=True)
    workspace_id = Column(SA_UUID(as_uuid=True), nullable=True)
    resource_id = Column(SA_UUID(as_uuid=True), nullable=True)
    action = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
