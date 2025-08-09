# User Story MP-TENANCY-APP-002 — **Apply Tenancy to Prompts + UI; Enforce RLS**

> **Epic:** Tenancy & Access Control
> **As a** user, **I want** to create and see prompts within my active workspace and set visibility (private/team/org/public), **so that** collaboration maps to my org/team while my drafts stay private.

## 1 · Narrative

*As a* user, I can switch workspaces (Personal, any Team, Organization) and create/edit prompts there. Visibility defaults to **private**. RLS is now **enforced**, so API/DB paths respect workspace and ACL semantics automatically.

## 2 · Acceptance Criteria

| # | Behaviour                                                                                    | Measure / Test                                                          |
| - | -------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| 1 | Prompts adopt the `resources` envelope (1:1 id), created within the active workspace         | Creating a prompt yields `resources` + `prompts` rows; FKs valid        |
| 2 | Visibility selector on create/edit: `private`, `team`, `org`, `public`, `unlisted` (flagged) | UI shows control; API persists; default = `private`                     |
| 3 | Workspace switcher (Personal/Team/Org) drives queries via `workspace_id`                     | Switching changes list results; state survives refresh                  |
| 4 | RLS **enforced**: only authorized principals can read/write                                  | Matrix tests pass: owner/teammate/org-mate/stranger × visibility × verb |
| 5 | Public resources are readable without auth; writes prohibited                                | GET works anonymously; POST/PUT/DELETE forbidden                        |
| 6 | Audit entries for create/update/delete appear with tenant/workspace/resource/principal       | Log assertions in integration tests                                     |
| 7 | Perf sanity: list 1k prompts in tenant under 300ms p95 (dev with RLS on)                     | Measured in CI perf step                                                |

## 3 · Context & Dependencies

* **Depends on:** MP-TENANCY-DB-001 completed; baseline web/backend stack in place.&#x20;
* **Forward hooks:** ACL editor, external collaborators, SSO/SAML/SCIM.

## 4 · Architecture & Implementation Details

## 4.1 Database & Schema

* `prompts.id` becomes **FK to `resources.id`**; remove old `owner_id` if present.
* Add `visibility` and `workspace_id` to resource envelope (already present from DB story).
* Ensure partial index to speed common list: `(tenant_id, workspace_id, type='prompt')`.

## 4.2 API Endpoints

* **Prompts**: extend existing routes to accept `workspace_id` (query or body) and `visibility`.
* Default workspace = caller’s **Personal Workspace**.
* Update OpenAPI with new fields and examples.

## 4.3 Backend Services & Tasks

* `ResourcesService.create(type='prompt', workspace_id, visibility)` wraps prompt creation.
* Enforce **RLS ON** for reads; keep a feature flag for writes if you want a staged rollout.
* Audit decorator captures `resource_id`, `tenant_id`, `workspace_id`, `principal_id`.

## 4.4 Frontend

* **Workspace Switcher**: control in header/sidebar.
* **Prompt Create/Edit**: add Visibility selector control; show workspace & visibility badges on cards.
* Empty state messaging reflects the current workspace (e.g., “No prompts in *Team: Growth* yet”).
* Baseline UI remains Next.js + Tailwind/Radix per Phase-1 baseline.&#x20;

## 4.5 Observability & Logging

* Add `tenant_id`, `workspace_id`, `visibility` tags to list/detail/create spans and to structured logs.
* Dashboards: per-workspace counts, top visibilities, RLS deny count.

## 5 · Testing Strategy

* **Matrix integration tests** for `{private, team, org, public, unlisted}` × `{owner, teammate, org-mate, stranger}` × `{read, write}`.
* **Anon public read** tests for `public`.
* **Perf smoke** with 10k prompts in one tenant (subset loaded per list) under budget.

## 6 · Documentation & Artifacts

| File / Location               | Update / Create                                                                 |   |
| ----------------------------- | ------------------------------------------------------------------------------- | - |
| `docs/guides/workspaces.md`   | Switching workspaces; defaults; what each scope means                           |   |
| `docs/api.md`                 | Updated `POST/PUT /prompts` payloads; `workspace_id` behaviour; visibility enum |   |
| `docs/adr/001_tenancy_rls.md` | Add enforcement decision + rollout notes                                        |   |
| `docs/ux/figma.md`            | Workspace switcher + visibility control annotations                             |   |

## 7 · Risks & Mitigations

| Risk                         | Impact                   | Mitigation                                                                  |
| ---------------------------- | ------------------------ | --------------------------------------------------------------------------- |
| UI points at wrong workspace | Surprise “missing data”  | Persist workspace in URL/query or local storage; add banner on empty states |
| Public leakage via logs      | Sensitive fields exposed | Scrub body content from logs; log IDs/metadata only                         |

## 8 · Future Considerations & Placeholders

* `resource_acl` editor UI for explicit grants.
* External collaborators as principals (`kind='external_user'`).
* Data region routing keyed by `organizations.data_region`.
