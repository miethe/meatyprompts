# ADR 001: Tenancy with Shared Schema and RLS

## Status
Accepted

## Context
A unified multi-tenant data model is required to allow organizations, teams and individual users to own resources in shared database schema. Row level security (RLS) in Postgres offers tenant isolation while maintaining a single schema.

## Decision
Use a shared PostgreSQL schema with tenant identifiers on all resource rows. Row level security policies are defined per table and rely on session variables `app.tenant_id` and `app.user_id`. Helper SQL functions expose these values to queries. Policies are created but left disabled until enforcement is required.

## Consequences
- Simplifies migrations and administration by keeping a single schema.
- Session context must be set for every connection, requiring middleware support.
- Future features can enable RLS without additional schema changes.
