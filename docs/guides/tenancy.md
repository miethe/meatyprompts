# Tenancy Guide

This guide explains how to add a new resource under the multi-tenant envelope.

1. Create a row in the `resources` table with the tenant and workspace identifiers for the resource.
2. Store the actual resource data in its domain table and reference the `resources.id`.
3. If access control is needed, add entries to `resource_acl` for the principals that should have access.
4. Use the `current_tenant()` and `caller_principals()` SQL helpers in queries to respect tenant boundaries.

Session variables `app.user_id` and `app.tenant_id` are set automatically by the API middleware and can be used in database functions and policies.
