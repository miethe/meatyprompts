# User Story MP-TENANCY-DB-001 — **Tenancy Foundations (Schema, Principals, Workspaces, Resources, RLS in “shadow”)**

> **Epic:** Tenancy & Access Control
> **As a** developer and system admin, **I want** a unified multi-tenant data model and RLS scaffolding, **so that** all future resources can live in personal/team/org containers with enforceable boundaries before any UI or product semantics are layered on.

## 1 · Narrative

*As a* platform dev, *I want* organizations, teams, principals, workspaces, and a resource envelope with RLS policies in place (not yet enforced), *so that* we can adopt this container model across all future features without per-tenant forks.

## 2 · Acceptance Criteria

| # | Behaviour                                                                                                                                     | Measure / Test                                                             |
| - | --------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| 1 | Alembic creates `organizations`, `teams`, `org_members`, `team_members`, `principals`, `workspaces`, `resources`, `resource_acl`, `audit_log` | Migration runs clean on a fresh DB; re-runs idempotently (no-op)           |
| 2 | `resources` envelope exists and supports types: `prompt`, `collection`, `model`, `integration`, `tag`                                         | DB constraints + enum checks present; insert/select smoke tests            |
| 3 | SQL helper functions exist: `current_tenant()`, `caller_principals()`                                                                         | Unit tests validate outputs for seeded org/team/user matrix                |
| 4 | RLS policies defined on `resources` (read/write) but **not enforced** (shadow mode)                                                           | Queries succeed with/without session vars; policy toggles verified         |
| 5 | Session context setter available in backend (sets `SET app.user_id/app.tenant_id`)                                                            | Middleware unit test asserts per-request variables applied to pooled conns |
| 6 | Seed script creates a “Personal Org” + Personal Workspace for a test user                                                                     | `make db.seed` produces expected rows; counts/asserts pass                 |
| 7 | Observability fields present (`tenant_id`, `workspace_id`) in audit logs                                                                      | Insert via helper emits `audit_log` row; JSON log contains IDs             |

## 3 · Context & Dependencies

* **Depends on:** empty or disposable dev DB; baseline tech stack (FastAPI, SQLAlchemy, Alembic, Postgres) ready.&#x20;
* **Forward hooks / future features:** UI workspace switcher; prompt CRUD layered onto `resources`; ACL editor.

## 4 · Architecture & Implementation Details

## 4.1 Database & Schema

* Create core tables exactly as outlined in our previous plan (orgs, teams, memberships, principals, workspaces, resources, resource\_acl, audit\_log).
* Indexes: `(tenant_id, workspace_id, updated_at)`, `(tenant_id, type)`, `(tenant_id, visibility)` on `resources`.
* Alembic migration file: `backend/alembic/versions/{YYYYMMDD}_tenancy_foundations.py`. Template and model sections follow your story format.&#x20;

## 4.2 API Endpoints

* No public surface yet. Add a small **internal** route for health checks and to return `current_tenant()` for test purposes (e.g., `GET /_int/tenancy/ping`).&#x20;

## 4.3 Backend Services & Tasks

* `backend/domain/tenancy/`: CRUD services for orgs/teams/memberships/principals/workspaces.
* `backend/domain/resources/`: resource envelope helpers (create envelope, attach ACL).
* `backend/infra/db/rls.py`: session context setter that runs on every DB acquire.

## 4.4 Frontend

* None (foundation only). Scaffolding for future workspace switcher lives in a placeholder component.

## 4.5 Observability & Logging

* Structured logs add `tenant_id`, `workspace_id`, `resource_id` where present; basic span naming per your template’s observability guidance.&#x20;

## 5 · Testing Strategy

* **Unit:** SQL functions, envelope creation, ACL inserts.
* **Integration:** Seed → run policy toggles (shadow on/off) → assert reads unaffected while unenforced.
* **Perf smoke:** Seed 10k `resources` within one tenant; list query under 300ms p95 (dev).

## 6 · Documentation & Artifacts

| File / Location               | Update / Create                                                         |   |
| ----------------------------- | ----------------------------------------------------------------------- | - |
| `docs/adr/001_tenancy_rls.md` | Decision: shared-schema + RLS; switch criteria for schema/db-per-tenant |   |
| `docs/guides/tenancy.md`      | How to add a new resource under the envelope                            |   |
| `docs/api.md`                 | Internal `_int/tenancy/ping` and session context notes                  |   |

## 7 · Risks & Mitigations

| Risk                        | Impact                    | Mitigation                                                                |
| --------------------------- | ------------------------- | ------------------------------------------------------------------------- |
| Pooling misses session vars | RLS later misbehaves      | Force-set vars on every acquire; regression test with concurrent requests |
| Enum/constraint drift       | Future migrations brittle | Centralize enums; use CHECKs with values tested in CI                     |

## 8 · Future Considerations & Placeholders

* Data residency flag on `organizations.data_region` for later region pinning.
* `catalog_items` overlay table (global/org/team/user).
