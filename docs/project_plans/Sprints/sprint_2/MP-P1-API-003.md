# User Story MP-P1-API-003 — **Prompts CRUD API (Phase 1)**

> **Epic:** Phase 1 — Manual MVP
> **As a** signed-in creator, **I want** a private CRUD API for prompts, **so that** the web app (and future clients) can create, read, update, and list prompt versions reliably.

---

## 1 · Narrative

*As a* **user**, *I want* to **POST, GET (list + by id), and PUT** prompts with required metadata and system timestamps, *so that* the Vault UI can persist and retrieve my prompts quickly and consistently with the PRD’s Phase-1 scope (search and other actions come later). The API must align with the schema and acceptance criteria defined in the PRD for Phase 1 (Create/Edit; Tags/Models) and the private route layout for `/prompts`. &#x20;

---

## 2 · Acceptance Criteria

| # | Behaviour                                                                                    | Measure / Test                                                                                       |
| - | -------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| 1 | **Create** a prompt with `title`, `body`, `use_cases`, `access_control` (+ optional fields). | `POST /prompts` → **201** with full Prompt payload (incl. header `title` & `tags`, version `"1"`).   |
| 2 | **List** prompts with optional filters (model, provider, use\_case).                         | `GET /prompts?model=gpt-4o` returns **200** and only matching rows; order desc by `created_at`.      |
| 3 | **Get by ID** returns latest version joined with header fields.                              | `GET /prompts/{id}` → **200** Prompt (has `title`, `tags`); **404** if not found. **(New)**          |
| 4 | **Update** latest version fields without version bump.                                       | `PUT /prompts/{prompt_id}` → **200** Prompt, `updated_at` changes, fields updated per whitelist.     |
| 5 | **Validation errors** yield **400** with details.                                            | Send invalid payload (e.g., missing `title`) → **400**.                                              |
| 6 | **Contract** matches PRD (private API shape for `/prompts`).                                 | OpenAPI shows routes: `POST /prompts`, `GET /prompts`, `GET /prompts/:id`, `PUT /prompts/:id`.       |

> Notes: “Duplicate”, “Favorite”, “Archive”, “Search (query/tags)”, “Collections”, “Import/Export”, “Share” are separate stories per PRD timeline (Sprints 2–3).&#x20;

---

## 3 · Context & Dependencies

* **Depends on**

  * Phase-1 schema for `prompts` + `prompt_versions` (already present). &#x20;
  * Auth middleware (session/JWT) to keep the API private (implementation out-of-scope here).&#x20;
* **Forward hooks / future features**

  * Search (query/tags) will expand list filters and add FTS/trigram in a later story.&#x20;
  * Duplicate/version bump, favorite/archive endpoints (later stories).&#x20;

---

## 4 · Architecture & Implementation Details

### 4.1 Database & Schema

* **Tables (exist):**

  * `prompts (id, title, tags, created_at, updated_at)` — header-level fields.&#x20;
  * `prompt_versions (id, prompt_id, version, body, access_control, …, created_at, updated_at)` — versioned fields.&#x20;
* **Indexes:** ensure index on `prompt_versions.created_at` for default sort; join queries rely on FK `prompt_id`. *(Add Alembic migration if missing.)*
* **Model contracts:** Pydantic `Prompt` uses `from_attributes=True` and **must** include header fields (`title`, `tags`) in responses.&#x20;

### 4.2 API Endpoints

* **File:** `backend/api/routes/prompts.py`

  * ✅ `POST /prompts` (exists): returns a fully hydrated `Prompt`. **No change.** &#x20;
  * ✅ `GET /prompts` (exists): supports `model`, `provider`, `use_case`. **No change now**; search/tags later. &#x20;
  * 🆕 `GET /prompts/{id}`: fetch latest version joined with header; **404** if not found. *(Add route.)*
  * ⚠️ `PUT /prompts/{prompt_id}` (exists): **Fix** to return a hydrated `Prompt` (header + tags) rather than raw ORM version. &#x20;
  * *(DELETE is intentionally deferred; “Archive” will cover soft delete in Sprint 2.)*&#x20;

**Contract (per PRD, Phase-1 private API):** `/prompts` resources are in scope now; other actions (duplicate, favorite, archive) follow later.&#x20;

### 4.3 Backend Services & Tasks

* **File:** `app/services/prompt_service.py`

  * **Add** `get_prompt_by_id(id: UUID) -> Prompt` that joins header + latest version and returns hydrated `Prompt`.
  * **Fix** `update_prompt(...)` to return hydrated `Prompt` (align with create/list). *(Currently returns `PromptVersionORM` only.)*&#x20;
  * **List** already joins header + versions and maps to `Prompt`. Reuse mapping helper. &#x20;

### 4.4 Frontend (Wire-up only)

* Data hooks call the above endpoints for Vault screens (no UI scope here). PRD expects CRUD in Sprint 1 to unblock UI.&#x20;

### 4.5 Observability & Logging

* Add spans: `prompts.create`, `prompts.list`, `prompts.get`, `prompts.update`; include `user_id`, `prompt_id`.
* Structured error logs for 4xx/5xx.

---

## 5 · Testing Strategy

| Layer           | Tool                    | New Tests / Assertions                                                                |
| --------------- | ----------------------- | ------------------------------------------------------------------------------------- |
| **Unit**        | Pytest                  | Service: create/list/get/update happy paths; update whitelist respected.              |
| **Integration** | FastAPI TestClient      | End-to-end for POST/GET list/GET id/PUT; 400/404 paths; response has `title`, `tags`. |
| **Contract**    | Schemathesis / pydantic | OpenAPI matches models; regression when adding GET by id.                             |

> Include negative tests for invalid payloads; ensure `Prompt` shape is identical across create/list/get/update.

---

## 6 · Documentation & Artifacts

| File / Location              | Update / Create                                 |
| ---------------------------- | ----------------------------------------------- |
| `docs/api.md`                | Add `GET /prompts/{id}`; update `PUT` return.   |
| `docs/adr/0xx_prompt_api.md` | Record decision to hydrate responses uniformly. |
| OpenAPI (generated)          | Ensure new route + examples are present.        |
| Data dictionary              | Confirm header vs. version field ownership.     |

---

## 7 · Risks & Mitigations

| Risk                                         | Impact                                  | Mitigation                                                                           |
| -------------------------------------------- | --------------------------------------- | ------------------------------------------------------------------------------------ |
| Returning mixed shapes across endpoints      | Frontend bugs / confusion               | Hydrate consistently from service; single mapper.                                    |
| Update semantics vs. versioning expectations | Confusion vs. duplicate/version feature | Document: `PUT` updates latest version; “Duplicate/Version” handled in later story.  |
| Missing search/tags filters today            | Temporary UX gap                        | Tracked in Search story (Sprint 2).                                                  |

---

## 8 · Future Considerations & Placeholders

* Expand list filters to `query`, `tags`, `favorite`, `archived`; add trigram/FTS and perf budget per PRD. &#x20;
* Add `POST /prompts/{id}/duplicate`, `favorite`, `archive` in their dedicated stories.&#x20;

---

## 9 · Implementation Tasks (Dev-Ready)

* **API**

  * Add `GET /prompts/{id}` route + handler in `backend/api/routes/prompts.py`.
  * Adjust `PUT /prompts/{prompt_id}` to return hydrated `Prompt`.&#x20;
* **Service**

  * Implement `get_prompt_by_id` and `to_prompt(version, header)` mapper; reuse in list/create/update.&#x20;
* **Schema/Indexes**

  * Verify index on `prompt_versions.created_at`; add Alembic migration if absent.
* **Docs/Tests**

  * Update OpenAPI examples and write unit/integration tests as above.

---

## 10 · Gaps / Clarifications (TBD)

* **`detailed-impl.md`** was not attached/found; if it specifies pagination, sorting enums, or error codes beyond the above, please share.
* Confirm **DELETE** policy in Phase 1 (hard delete vs. wait for “Archive” in S2). PRD timeline implies archive/favorites in S2; propose **no DELETE** now.&#x20;
* Confirm **owner scoping** (multi-user tenancy) for these routes; current models don’t show `owner_id`—will be needed before GA search/indexes.&#x20;

---

**Current State Summary (what already exists):**

* Models for header/version + Pydantic `Prompt` with `from_attributes`. ✔️  &#x20;
* Routes: `POST /prompts`, `GET /prompts` (filters), `PUT /prompts/{prompt_id}`. ✔️ &#x20;
* Service: `create_prompt` (hydrates), `list_prompts` (hydrates), `update_prompt` (**returns raw ORM; fix**).  &#x20;

> This story delivers a **complete, consistent CRUD surface** for prompts per Phase-1, unblocking the Vault UI and setting clean seams for Sprint-2 features.
