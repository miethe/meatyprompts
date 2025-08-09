# User Story MP-P1-COLL-010 — **Collections CRUD + Vault Filter**

> **Epic:** Phase 1 — Manual MVP
> **As a** signed-in creator, **I want** to group prompts into **Collections** and filter my Vault by a collection, **so that** I can organize related prompts (projects, clients, topics) and find them faster.

---

## 1) Summary / Narrative

We’ll add **owner-scoped Collections** with simple CRUD and prompt membership management. Collections live at the **prompt header** level (not per version). The Vault can be filtered by a selected collection. Keep scope tight: no nested collections, no sharing, no ordering beyond name/updated\_at.

---

## 2) Acceptance Criteria

| ID   | Criteria                                                                                                                          |
| ---- | --------------------------------------------------------------------------------------------------------------------------------- |
| AC-1 | I can **create** a collection (name required), **rename**, and **delete** my own collections. Names are unique **per user**.      |
| AC-2 | I can **add/remove** a prompt to/from one or more collections. Membership changes persist and reflect immediately in the UI.      |
| AC-3 | Vault supports **filter by collection**; selecting a collection shows only prompts in that collection. “Clear” resets the filter. |
| AC-4 | Collections appear in a left sidebar section or filter control with counts (optional) and basic empty states.                     |
| AC-5 | Security: all endpoints are **owner-scoped**; cross-user access is blocked; unauthenticated requests get **401**.                 |
| AC-6 | NFRs: typical list/filter operations p95 ≤150ms; CRUD p95 ≤100ms; a11y for buttons/menus; telemetry events captured.              |

---

## 3) Context & Dependencies

* **Depends on:**

  * **MP-P1-AUTH-001** (sessions + `/me`) to scope by user.
  * **MP-P1-DB-002** baseline schema + indexes.
  * **MP-P1-API-003** hydration patterns for prompts.
* **Integrates with:**

  * **MP-P1-SRCH-007** (Vault filter wiring) — adds `collection_id` filter.
* **Out of scope (Phase-1):** shared/team collections, nested collections, drag-sort ordering, bulk actions, import/export of collections.

---

## 4) Architecture & Implementation

### 4.1 Data Model (Alembic migration)

Add two owner-scoped tables. Keep prompts unchanged; store membership in a bridge.

* **collections**

  * `id UUID PK`
  * `owner_id UUID NOT NULL FK -> users(id)`
  * `name TEXT NOT NULL` (unique per owner)
  * `created_at TIMESTAMPTZ DEFAULT now()`
  * `updated_at TIMESTAMPTZ DEFAULT now()`
  * **Constraints/Indexes:**

    * `UNIQUE (owner_id, name)`
    * `INDEX (owner_id, updated_at DESC)`

* **collection\_prompts** (bridge)

  * `collection_id UUID NOT NULL FK -> collections(id) ON DELETE CASCADE`
  * `prompt_id UUID NOT NULL FK -> prompts(id) ON DELETE CASCADE`
  * `PRIMARY KEY (collection_id, prompt_id)`
  * **Indexes:**

    * `INDEX (prompt_id)` for reverse lookups
    * (Optional) `INDEX (collection_id)` is implied by PK; keep explicitly for clarity if your DB tooling doesn’t.

**Notes**

* Collections apply to **prompt header** (not version). A prompt may belong to **many collections**.
* Deleting a collection removes memberships via cascade; prompts remain intact.

### 4.2 API (FastAPI)

**Routes (all owner-scoped; auth required):**

* `GET /collections` → list user’s collections (optionally include `count` per collection; see performance note).
* `POST /collections` `{ name }` → create; 409 if name taken for this owner.
* `PATCH /collections/{collection_id}` `{ name }` → rename; 409 on conflict.
* `DELETE /collections/{collection_id}` → delete (204).
* `GET /collections/{collection_id}/prompts?limit=&after=` → list prompts in a collection (hydrated Prompt items; optional but useful for empty states).
* `POST /collections/{collection_id}/prompts` `{ prompt_id }` → add membership (idempotent).
* `DELETE /collections/{collection_id}/prompts/{prompt_id}` → remove membership (204).

**Vault filter (extends existing list route):**

* `GET /prompts?...&collection_id=<uuid>` → returns only prompts in that collection (inner join on `collection_prompts`).

**Response shapes**

* `Collection`: `{ id, name, created_at, updated_at }` (+ optional `count` if requested via `?include=count`).
* Membership endpoints return `{ ok: true }` or the updated `Collection` with basic metadata.

**Validation**

* Name: trim; 1–64 chars; allowed charset conservative (letters, numbers, spaces, `-_.&/`); enforce uniqueness per owner.

**Performance note on counts:**

* If `count` is requested, compute `(SELECT COUNT(*) FROM collection_prompts WHERE collection_id=...)`. For large datasets, omit by default and show lazily in UI (toggleable). For P1, counts are **optional**.

### 4.3 Services

Create `collection_service.py`:

* `list_collections(owner_id, include_count=False)`
* `create_collection(owner_id, name)` (dedupe by `owner_id,name`)
* `rename_collection(owner_id, id, name)`
* `delete_collection(owner_id, id)`
* `add_prompt(owner_id, collection_id, prompt_id)` (verify ownership of prompt & collection)
* `remove_prompt(owner_id, collection_id, prompt_id)`

Extend `prompt_service.list_prompts(...)` to accept `collection_id` and join the bridge when present.

### 4.4 UI (React)

* **Sidebar**

  * Add a **Collections** section (collapsible) listing names.
  * “+ New Collection” opens a small input/confirm; list item has overflow menu for Rename/Delete.
  * Selecting a collection updates URL query (`?collection=<id>`) and refetches prompts.

* **Vault Filters Sheet**

  * Add a **Collection** single-select (mirrors sidebar selection).
  * Show an applied chip “Collection: X” with clear icon.

* **Prompt assignment**

  * In **PromptDetailModal** (recommended for P1): a **multi-select** to add/remove collections for this prompt.
  * (Optional defer) A lightweight “Add to collection” in **PromptCard** overflow menu.

* **Empty states**

  * No collections → suggest creating one.
  * Collection selected but has 0 prompts → CTA to add from modal.

* **A11y**

  * Ensure menu items and inputs are labeled; keyboard navigation across list, menus, and selects.

### 4.5 Observability

* Telemetry events:

  * `collection_created`, `collection_renamed`, `collection_deleted`
  * `collection_prompt_added`, `collection_prompt_removed`
  * `vault_filtered_collection` (when applying filter)
* Add trace spans around membership writes and filtered list queries; include `{collection_id, prompt_count}` where applicable.

---

## 5) Non-Functional Requirements

* **Perf:**

  * `GET /collections` p95 ≤100ms (without counts).
  * `GET /prompts?collection_id=...` p95 ≤150ms @ ≤5k prompts/user.
* **Security:** Strong owner checks on all routes; membership add/remove verifies **both** the collection and prompt belong to the caller.
* **A11y:** WCAG 2.1 AA for new components.
* **Data integrity:** PKs, FKs with cascades; idempotent membership operations.

---

## 6) Testing Strategy

| Layer             | Tooling            | Coverage                                                                                                                                        |
| ----------------- | ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Unit (backend)    | pytest             | Create/rename/delete collection; uniqueness per owner; membership add/remove idempotency; ownership enforcement.                                |
| Integration (API) | FastAPI TestClient | All routes 200/201/204; 401 without auth; 403 on cross-owner access; 409 on duplicate name; filter by `collection_id` returns expected prompts. |
| SQL/Perf          | EXPLAIN ANALYZE    | Filtered prompt list uses `collection_prompts` index; p95 budgets met on fixture dataset.                                                       |
| Unit (frontend)   | Jest + RTL         | Sidebar list renders; create/rename/delete flows; URL state sync; filter chip; modal multi-select saves and updates card grid.                  |
| E2E               | Cypress/Playwright | Create collection → assign two prompts → filter shows two → remove one → filter shows one → delete collection clears filter.                    |
| A11y              | axe                | No violations on sidebar, menus, modal inputs.                                                                                                  |

---

## 7) Documentation & Artifacts

* **`docs/api.md`** — Collections endpoints with examples; membership rules; error codes.
* **`docs/data-model.md`** — ERD update (collections + bridge).
* **`docs/guides/collections.md`** — How to use collections (with screenshots).
* **OpenAPI** — Schemas/params for new routes.
* **Runbook** — Safe rename/delete, handling name collisions, and how to backfill/merge collections (if needed).

---

## 8) Risks & Mitigations

| Risk                                                 | Impact            | Mitigation                                                                           |
| ---------------------------------------------------- | ----------------- | ------------------------------------------------------------------------------------ |
| Duplicate names across users vs. per user uniqueness | Confusion         | Enforce `(owner_id, name)` unique; return 409 on conflict with friendly message.     |
| Count query slowness with large libraries            | Slow UI           | Make counts optional; compute lazily; consider cached counts later.                  |
| Ownership bugs (adding someone else’s prompt)        | Data leak         | Double-check ownership in service; write integration tests for cross-owner attempts. |
| Filter + pagination edge cases                       | Missing/dupe rows | Use stable sort + cursor (per SRCH story); include `collection_id` in cursor hash.   |

---

## 9) Implementation Tasks (Dev-Ready)

**DB / Migration**

* [ ] Create `collections` + `collection_prompts` tables, constraints, and indexes.
* [ ] Add Alembic migration + downgrade.

**Backend**

* [ ] Implement `collection_service.py` (functions listed above).
* [ ] Add `api/routes/collections.py` with CRUD + membership endpoints.
* [ ] Extend `prompt_service.list_prompts` to respect `collection_id`.
* [ ] Update OpenAPI + error models.

**Frontend**

* [ ] Sidebar **Collections** section with create/rename/delete.
* [ ] Wire Vault filter (`?collection=<id>`) and applied chip.
* [ ] PromptDetailModal multi-select to add/remove collections (save on change).
* [ ] Optional: card overflow “Add to collection…” (can be deferred).

**Observability & Docs**

* [ ] Emit telemetry events and trace spans.
* [ ] Update docs (API, data model, user guide).
* [ ] Tests per Section 6.

---

## 10) Open Questions (TBD)

1. **Counts:** Do we show counts in the sidebar for P1, or defer to Phase-1b?
2. **Default sort for the sidebar:** `updated_at desc` or `name asc`? (Recommend `name asc` for discoverability.)
3. **Bulk assign:** Needed in P1, or defer? (Recommend defer.)
4. **Collections in duplication:** When a prompt is duplicated, should memberships copy? (Recommend **no** in P1; keep it explicit.)

---

## Definition of Done

* Collections tables live with constraints and indexes; API endpoints work and are documented.
* Vault filter by collection functions end-to-end.
* Prompt assignment to/from collections works via the modal (and optionally card menu).
* Tests (unit, integration, E2E, a11y) pass; perf targets met; telemetry events visible in dev; docs updated.
