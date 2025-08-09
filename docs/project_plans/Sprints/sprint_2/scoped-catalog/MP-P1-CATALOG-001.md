# User Story MP-P1-CATALOG-001 — **Scoped Catalog & RLS Foundation**

> **Epic:** Platform Foundations → Catalogs & Metadata
> **As a** MeatyPrompts user, **I want** official pick-lists plus my own private entries, **so that** I can use a rich default set while customizing without exposing my additions to everyone.

---

## 1 · Narrative

*As a* creator configuring prompts, *I want* a single dropdown to show “Official” items plus “Mine,” with my additions saved for me only. *So that* I can work fast with a curated baseline and still extend the catalog without polluting everyone else’s lists.

This story implements the **scoped-catalog pattern** and **row-level security (RLS)** in Postgres, delivering a production-grade foundation for all pick-lists starting with **Models**. It also wires backend APIs, middleware to set session context for RLS, seed data, caching, and a reference UI dropdown with sectioned groups.

---

## 2 · Goals & Non-Goals

**Goals**

* Create canonical catalog schema for **Models** with `scope` (`system`, `workspace` \[placeholder], `user`) and ownership fields.
* Enable **Row-Level Security** policies to safely serve multi-tenant reads/writes from one table.
* Provide CRUD APIs for user-private entries and read APIs for “effective” lists (system + user \[+ workspace later]).
* Seed a curated **system** set; enforce uniqueness constraints per scope/owner/workspace.
* Deliver a reusable **UI dropdown** that groups options: Official / Workspace (placeholder) / Yours.
* Establish caching and ETag/Last-Modified semantics for system set.
* Document the pattern so other catalogs (providers, integrations, categories) can replicate.

**Non-Goals (future stories)**

* Admin UI for moderating user → system suggestions.
* Workspace scope behavior and UI.
* Versioning/deprecation windows for catalog entries.
* Full analytics dashboards.

---

## 3 · Acceptance Criteria (BDD)

**AC1 – Read “effective” models list**

* **Given** an authenticated user
* **When** the client calls `GET /catalog/models?effective=true`
* **Then** the response includes `scope='system'` plus entries with `owner_id = user.id`
* **And** excludes other users’ entries
* **And** returns grouped metadata `{section: 'Official'|'Workspace'|'Yours'}` per item.

**AC2 – Create a private model**

* **Given** an authenticated user
* **When** the client `POST`s `{provider, name, display_name, meta}` to `/catalog/models`
* **Then** a row is created with `scope='user'` and `owner_id=user.id`
* **And** subsequent reads include it under “Yours”.

**AC3 – Uniqueness within scope**

* **Given** a user already has a `{provider, name}` under `scope='user'`
* **When** they attempt to create the same combo again
* **Then** the API returns 409 Conflict with a helpful message.

**AC4 – Security by RLS**

* **Given** two different users
* **When** user A tries to read/update/delete user B’s private entry by ID
* **Then** the DB RLS policy prevents access and API returns 404/403 appropriately.

**AC5 – System set is read-only to non-admins**

* **Given** a non-admin user
* **When** they attempt to modify/delete a `scope='system'` row
* **Then** the request is denied (403).

**AC6 – Performance**

* **Given** a warm cache
* **When** the client queries system models
* **Then** the API responds with HTTP 304 when `If-None-Match` or `If-Modified-Since` matches, or returns in <150ms P95 with Redis cache hit.

---

## 4 · Architecture & Design

## 4.1 Data Model (Postgres via SQLAlchemy/Alembic)

* **Enum**

  * `catalog_scope`: `system | workspace | user`

* **Table: `models_catalog`**

  * `id UUID PK`
  * `scope catalog_scope NOT NULL DEFAULT 'system'`
  * `owner_id UUID NULL → users(id)` *(required for `user` scope)*
  * `workspace_id UUID NULL → workspaces(id)` *(placeholder for `workspace` scope)*
  * `provider TEXT NOT NULL`  — e.g., `OpenAI`, `Anthropic`
  * `name TEXT NOT NULL`      — e.g., `gpt-4o`, `claude-3.5-sonnet`
  * `display_name TEXT NOT NULL`
  * `meta JSONB NOT NULL DEFAULT '{}'` — ctx window, pricing, limits, tags
  * `alias_of_id UUID NULL → models_catalog(id)` — private alias of a system entry
  * `is_active BOOLEAN NOT NULL DEFAULT TRUE`
  * `created_at/updated_at TIMESTAMPTZ DEFAULT now()`
  * **Uniqueness**: `UNIQUE(scope, provider, name, COALESCE(owner_id,'00..00'), COALESCE(workspace_id,'00..00'))`
  * **Indexes**: `(scope, provider, name)`, `(owner_id)`, `(workspace_id)`

* **Table: `catalog_suggestions`** *(scaffold for future moderation)*

  * `id UUID PK`
  * `suggester_id UUID NOT NULL → users(id)`
  * `payload JSONB NOT NULL`
  * `status TEXT NOT NULL DEFAULT 'pending'`
  * `created_at TIMESTAMPTZ DEFAULT now()`

* **RLS**

  * Enable RLS on `models_catalog`.
  * Per-request settings set by middleware:
    `SET app.user_id`, `SET app.workspace_id`, `SET app.role`.
  * **Policies:**

    * **SELECT**: allow `scope='system'` OR `scope='user' AND owner_id=app.user_id` OR `scope='workspace' AND workspace_id=app.workspace_id`.
    * **INSERT**: allow `scope='user' AND owner_id=app.user_id` OR (`scope='system'` AND `app.role='admin'`).
    * **UPDATE/DELETE**: same actor constraints as SELECT plus ownership.

* **Trigger**

  * `updated_at` ON UPDATE.

* **Prompt linkage (forward-looking)**

  * `prompt_target_models(prompt_id UUID FK → prompts, model_id UUID FK → models_catalog)` as the normalized replacement for any free-text “model name” fields.

## 4.2 API Endpoints (FastAPI)

* `GET /catalog/models`

  * Params: `effective: bool=false`, `scope: Optional[system|workspace|user]`
  * Returns list of entries; if `effective=true` → union of system + workspace (placeholder) + user for caller with `section` hint.

* `POST /catalog/models`

  * Auth required; body: `{provider, name, display_name, meta?, alias_of_id?}`
  * Creates `scope='user', owner_id=user.id`.

* `PUT /catalog/models/{id}`

  * Updates only if the caller owns the entry or is admin for system rows.

* `DELETE /catalog/models/{id}`

  * Soft/hard delete (for MVP: hard delete for user scope; system rows admin-only).

* **Admin (future)**

  * `POST /admin/catalog/models` to seed/maintain system set.
  * `POST /catalog/models/suggest` to open a suggestion.

**Conventions**

* ETag from a stable hash of system rows (`models:system:hash`); `Last-Modified` from max(`updated_at`) for system scope.
* Error map: 400 validation, 403 forbidden, 404 not found (including RLS-hidden), 409 uniqueness.

## 4.3 Service & Middleware

* **Auth middleware** resolves user + roles, sets Postgres settings:

  * `SET app.user_id = '{uuid}'`
  * `SET app.workspace_id = '{uuid|null}'`
  * `SET app.role = 'user|admin'`
* **Caching**: Redis key `models:system:v{seed_version}` stores serialized system list.
* **Invalidation**: on admin changes to system scope, bump `seed_version` or publish channel to evict.

## 4.4 Frontend (Web first; RN parity later)

* **Components**

  * `CatalogDropdown` (generic) with **sections**: “Official”, “Workspace” (hidden until enabled), “Yours”.
  * Uses React Query (or TanStack) to fetch `GET /catalog/models?effective=true`.
  * Accessibility via Headless UI `Listbox` or Radix UI Select; styled via Tailwind.
  * Shows `display_name` and subtle sublabel `{provider}/{name}`.
  * Inline “Add new” affordance opens `AddModelDialog` → POST → optimistic update under “Yours”.

* **State**

  * Client-side cache keyed by `['catalog','models','effective']`.
  * Respect ETag/If-None-Match automatically.

---

## 5 · Work Breakdown (tickets)

* **DB**

  * MP-P1-CAT-DB-001: Create `catalog_scope` enum, `models_catalog`, indexes, triggers.
  * MP-P1-CAT-DB-002: Enable RLS & policies; migration script with reversible down.
  * MP-P1-CAT-DB-003: Seed `scope='system'` models set; seed versioning.

* **API**

  * MP-P1-CAT-API-004: Auth middleware to set `app.*` settings per request.
  * MP-P1-CAT-API-005: Routes for GET/POST/PUT/DELETE with pydantic schemas.
  * MP-P1-CAT-API-006: ETag/Last-Modified + Redis caching for system scope.
  * MP-P1-CAT-API-007: Error normalization (409 on unique, 403/404 on RLS).

* **UI**

  * MP-P1-CAT-UI-008: `CatalogDropdown` with sections + loading/empty states.
  * MP-P1-CAT-UI-009: `AddModelDialog` with validation and optimistic insert.
  * MP-P1-CAT-UI-010: Wire into Prompt Create/Edit forms.

* **Docs / Ops**

  * MP-P1-CAT-DOC-011: “Scoped Catalog Pattern” ADR + how-to extend to other catalogs.
  * MP-P1-CAT-OPS-012: Admin seed procedure and cache invalidation runbook.

* **Tests**

  * MP-P1-CAT-TST-013: DB/RLS unit tests (two-user scenarios).
  * MP-P1-CAT-TST-014: API happy/edge paths (409, 403/404).
  * MP-P1-CAT-TST-015: UI e2e for sections and “Add new”.

*(Codes use: DB/API/UI/DOC/OPS/TST as per our story taxonomy.)*

---

## 6 · Schema & API Details

**Pydantic**

```python
class ModelMeta(BaseModel):
    context_window: int | None = None
    max_output_tokens: int | None = None
    pricing: dict[str, float] | None = None
    tags: list[str] | None = None

class ModelCreate(BaseModel):
    provider: str
    name: str
    display_name: str
    meta: ModelMeta | dict | None = None
    alias_of_id: UUID | None = None  # optional private alias

class ModelRead(BaseModel):
    id: UUID
    scope: Literal['system','workspace','user']
    section: Literal['Official','Workspace','Yours']  # computed
    provider: str
    name: str
    display_name: str
    meta: dict
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

**Routes**

* `GET /catalog/models?effective=true|false&scope=…`
* `POST /catalog/models` → `ModelRead`
* `PUT /catalog/models/{id}` → `ModelRead`
* `DELETE /catalog/models/{id}` → `204 No Content`

---

## 7 · Security, Privacy, Compliance

* **RLS** is the primary barrier; APIs never broaden queries beyond RLS scope.
* **Least privilege**: non-admins cannot create/modify `system` rows.
* **IDOR-safe by design**: even if an ID is guessed, RLS hides non-owned rows.
* **Auditability**: log create/update/delete with `(user_id, model_id)`; future: write-ahead audit table.

---

## 8 · Migration Plan

1. Create enum, table, indexes, triggers.
2. Enable RLS with strict default-deny; then add policies.
3. Seed system entries (`seed_version=1` recorded in app config).
4. If existing prompts store a **free-text model**, do a best-effort map to system; otherwise create per-user private entries and link via `prompt_target_models` (if that table exists in your branch) — or record a **TODO** migration step in the prompts schema story.

Rollback leaves system intact; user rows are dropped with table if necessary.

---

## 9 · Performance & Observability

* Redis cache for `scope='system'` list; TTL = 1h; manual invalidation on admin updates.
* ETag computed as stable checksum of serialized system rows; `Last-Modified = max(updated_at)` for system scope.
* Metrics: count of catalog reads/writes, cache hit rate, RLS-blocked attempts (as WARN).

---

## 10 · UX Notes

* Section headers in dropdown: “Official”, “Workspace” (hidden until non-empty), “Yours”.
* “Add new” CTA only visible in “Yours.”
* Validation: live uniqueness check scoped to “Yours;” collate a friendly message if conflict.
* Subtle lock icon on “Official” items to signal read-only.

---

## 11 · Testing Strategy

* **DB/RLS**: `pytest` with two users and optional workspace; assert allowed/denied cases at SQL level (asyncpg).
* **API**: contract tests for filters, effective view, ETag/304, conflicts.
* **UI**: Playwright flows: load dropdown, see sections, create new, see optimistic update; reload shows persistence.
* **Perf**: simple load test (k6) for `GET effective=true` to verify <150ms P95 on warm cache.

---

## 12 · Documentation

* ADR: *ADR-00X Scoped Catalog & RLS* — rationale, alternatives rejected (“attach list to users”), extension recipe for new catalogs.
* README section: how to seed/update system set; how to add a new catalog (table, RLS, API, UI hook).
* OpenAPI updated; example payloads.

---

## 13 · Dependencies & Placeholders

* **Depends on**: Auth middleware that provides `user_id` and `role` (existing or in parallel ticket).
* **Placeholders**: `workspace_id` column and “Workspace” section are scaffolded; behavior activates once workspaces land.
* **Future**: moderation queue using `catalog_suggestions`; versioning/deprecation fields (`valid_from/to`), alias UX.

---

## 14 · Risks & Mitigations

* **RLS misconfig** → 403/404 surprises: cover with DB-level tests and explicit default-deny policy.
* **Cache incoherence** → stale system lists: invalidate via seed-version bump on admin changes.
* **Name collisions** across providers: uniqueness includes `(provider, name)`; display both in UI.

---

## 15 · Estimate

* DB & migrations: **0.5–1 day**
* RLS + middleware + tests: **1 day**
* API endpoints + tests: **1 day**
* UI dropdown + dialog + e2e: **1–1.5 days**
* Docs/ADR, seeds, ops notes: **0.5 day**
  **Total:** \~4–5.5 dev-days for MVP foundation.

---

## 16 · Definition of Done

* All ACs met; tests passing in CI; OpenAPI updated; seeds generated; dropdown integrated into Prompt forms; ADR merged; rollout notes prepared.

---

**Next up after this foundation:** replicate the pattern for **Providers** and **Integrations**, then wire **workspace** scope behavior once multi-user teams are enabled.
