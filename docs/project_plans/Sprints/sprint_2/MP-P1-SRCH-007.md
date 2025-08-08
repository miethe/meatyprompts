# User Story MP-P1-SRCH-007 — **Search / Filter / Sort (Vault)**

> **Epic:** Phase 1 — Manual MVP
> **As a** signed-in creator, **I want** fast search with filters and sorting in my Vault, **so that** I can quickly find the right prompt from a growing library.

---

## 1) Summary / Narrative

Deliver server-backed text search over **title + body** with common filters (**tags, favorite, archived, target\_models, providers, purposes/use\_cases, collections**) and stable sorts (**updated, created, title; relevance when a query is present**). Provide pagination (cursor preferred), perf budget **p95 ≤150 ms** for ≤5k prompts/user, and wire it to the existing Vault grid & Filters sheet.

---

## 2) Acceptance Criteria

| ID   | Criteria                                                                                                                                                                              |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| AC-1 | `GET /prompts` supports query `q` (text search) and filters: `tags[]`, `favorite`, `archived`, `target_models[]`, `providers[]`, `purposes[]` (alias `use_cases[]`), `collection_id`. |
| AC-2 | Sorts: `sort=updated_desc` (default), `created_desc`, `title_asc`, `relevance_desc` (only when `q` present).                                                                          |
| AC-3 | Pagination: `limit` (≤50) and cursor (`after`) that returns deterministic, duplicate-free pages; includes `next_cursor` in response when more results exist.                          |
| AC-4 | Response hydrates **header + latest version** consistently with other endpoints.                                                                                                      |
| AC-5 | Perf: search endpoint p95 ≤150 ms with realistic data (≤5k prompts/user, mixed filters).                                                                                              |
| AC-6 | UI: Filters panel debounces text search (300–500 ms), shows applied chips, “Clear all,” result count, and persists state in the URL.                                                  |
| AC-7 | Security: results are **owner-scoped** only. Requests without auth return **401**.                                                                                                    |
| AC-8 | Telemetry event `vault_search_performed` includes query length, filters used, result\_count, p95 bucket; no raw query text in logs (only length + hash).                              |

---

## 3) Context & Dependencies

* **Depends on:**

  * **MP-P1-DB-002** — owner scoping, indexes (trigram/FTS), arrays for tags/models; `prompts` + `prompt_versions`.
  * **MP-P1-API-003** — CRUD base and consistent hydration helper.
  * **MP-P1-TAG-006** — tag normalization + `/tags` suggestions (this story consumes tags; suggestions are not part of SRCH).
* **Planned later:** embeddings/semantic search (Phase 2), saved searches, collections (if not yet merged: filter is no-op until **COLL-010** lands).

---

## 4) Architecture & Implementation

### 4.1 API Design (FastAPI)

* **Route:** `GET /prompts`
* **Query params (all optional):**

  * `q: str` (text search), `tags: list[str]`, `favorite: bool`, `archived: bool`,
    `target_models: list[str]`, `providers: list[str]`, `purposes: list[str]` (alias `use_cases`), `collection_id: UUID`,
    `sort: enum(updated_desc|created_desc|title_asc|relevance_desc)`, `limit: int (≤50)`, `after: string (cursor)`
* **Response:**

  ```json
  {
    "items": [ { /* hydrated Prompt */ } ],
    "next_cursor": "opaque-string-or-null",
    "count": 37,        // items in this page
    "total_estimate": null // (optional; omit for P1 if expensive)
  }
  ```

### 4.2 Query Strategy (Postgres)

* **Owner scope:** `WHERE prompts.owner_id = :user_id`
* **Latest version join:** lateral or subquery on `(prompt_id, version DESC)` using index
* **Filters:**

  * **tags:** `:tags <@ prompts.tags` (array contains all provided) or ANY variant; start with **AND all** semantics
  * **favorite/archived:** booleans on header
  * **models/providers/purposes:** arrays on version: `:model = ANY(version.target_models)` etc.
  * **collection:** join `collection_prompts` on `prompt_id`
* **Search (`q`)** (P1 pragmatic):

  * Use `pg_trgm` similarity on title + body: `similarity(prompts.title, :q)` and `similarity(version.body, :q)`
  * Compute `relevance = 2.0*sim(title,q) + 1.0*sim(body,q)`; `WHERE (title ILIKE '%q%' OR body ILIKE '%q%' OR relevance > 0.1)`
  * Indexes required: `GIN(title gin_trgm_ops)`, `GIN(body gin_trgm_ops)`
  * If `sort=relevance_desc`, order by relevance, then `updated_at DESC, id`
* **Sorts:**

  * `updated_desc` (default): `ORDER BY prompts.updated_at DESC, prompts.id DESC`
  * `created_desc`: `ORDER BY prompts.created_at DESC, prompts.id DESC`
  * `title_asc`: `ORDER BY prompts.title ASC, prompts.id DESC`
  * `relevance_desc`: as above (only when `q` present)
* **Pagination (cursor):**

  * Cursor encodes the primary sort keys (e.g., `updated_at|id` or `relevance|updated_at|id`) + filter hash
  * Enforce stable secondary key `id` to avoid duplicates/missing rows across pages
  * Provide `limit` default 20; cap 50

### 4.3 Services & Project Structure

* **`search_service.py` (new):**

  * `build_query(filters: SearchFilters) -> sqlalchemy.Query`
  * `encode_cursor(row) -> str`, `decode_cursor(s) -> Cursor`
  * `score_relevance(title, body, q)` helper (server-side SQL expression)
* **`prompt_service.list_prompts(...)` (extend):**

  * Delegate to `search_service` for query building
  * Map ORM → hydrated Pydantic `Prompt` (reuse existing mapper)
* **Input validation:**

  * Normalize tags to lowercase; coerce `purposes` alias; dedupe arrays; clamp limits

### 4.4 UI / Web

* **`PromptListFilters.tsx` (wire-up):**

  * Add text input for **Search** with 300–500 ms debounce
  * Multi-selects for tags/models/providers/purposes; boolean toggles for favorite/archived
  * Collection select (hide if collections disabled)
  * “Apply” and “Clear all” actions; reflect state in **URL query string**
* **`index.tsx` (Vault page):**

  * Use TanStack Query with queryKey `[ "prompts", filters ]`
  * Read/write URL state → filters; read `next_cursor` for infinite scroll (optional) or “Load more”
  * Show result count and duration (optional small telemetry)

### 4.5 Indexes & Migrations (DB-002 alignment)

Ensure these exist (add migration if missing):

* `CREATE INDEX ix_prompts_owner_updated ON prompts (owner_id, updated_at DESC, id DESC);`
* `CREATE INDEX ix_versions_prompt_desc ON prompt_versions (prompt_id, version DESC);`
* `CREATE EXTENSION IF NOT EXISTS pg_trgm;`
* `CREATE INDEX ix_prompts_title_trgm ON prompts USING GIN (title gin_trgm_ops);`
* `CREATE INDEX ix_versions_body_trgm ON prompt_versions USING GIN (body gin_trgm_ops);`
* Optional when collections land: `CREATE INDEX ix_coll_prompts_prompt ON collection_prompts (prompt_id);`

---

## 5) Non-Functional Requirements

* **Perf:** p95 ≤150 ms for typical queries (≤5k prompts/user); warm cache assumption
* **Security:** owner scoping mandatory; reject unauthenticated; rate-limit `q` searches (e.g., 30/min per user)
* **A11y:** filter controls fully labeled; chips keyboard-removable; focus management preserved
* **Stability:** backward compatible URL params; ignore unknown filters
* **Observability:** traces around search; counters for cache hits/misses (if added later)

---

## 6) Testing Strategy

| Layer             | Tooling                  | Coverage                                                                                                                    |
| ----------------- | ------------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| Unit (backend)    | pytest                   | Query builder: combinations of filters; cursor encode/decode; relevance calculation present only when `q` given             |
| Integration (API) | FastAPI TestClient       | End-to-end `GET /prompts` with owner scoping; 401 w/o auth; tags “AND” semantics; sort correctness; pagination with `after` |
| SQL/Perf          | EXPLAIN ANALYZE in tests | Representative queries use intended indexes; p95 budget met on fixture dataset (\~5k rows)                                  |
| Frontend unit     | Jest + RTL               | Debounce behavior; URL state sync; applied chip rendering; Clear all                                                        |
| E2E               | Playwright/Cypress       | Type search → results update; combine filters; paginate; refresh (URL persists state)                                       |

---

## 7) Documentation & Artifacts

* **`docs/api.md`** — Document `/prompts` params, sorts, samples; cursor format (opaque)
* **`docs/search.md`** — Query semantics, AND logic for tags, relevance formula (high-level), perf tips
* **`docs/telemetry/events.md`** — `vault_search_performed` schema (fields, PII policy)
* **OpenAPI** — Update schema for new params + examples

---

## 8) Risks & Mitigations

| Risk                                          | Impact        | Mitigation                                                                                            |                       |
| --------------------------------------------- | ------------- | ----------------------------------------------------------------------------------------------------- | --------------------- |
| Trigram search still slow on very long bodies | p95 breaches  | Add body length clamp in scoring; consider partial index; revisit FTS/materialized column if needed   |                       |
| Cursor bugs yield duplicates/missing rows     | Bad UX        | Always include stable tiebreaker (`id`); unit tests with edge cases around equal timestamps/relevance |                       |
| “OR vs AND” ambiguity for tags                | Confusion     | Start with **AND**; document; add \`tags\_mode=any                                                    | all\` later if needed |
| Collections not yet shipped                   | Filter broken | Hide control unless collections feature flag enabled; server silently ignores param if unsupported    |                       |

---

## 9) Implementation Tasks (Dev-ready)

**Backend**

* [ ] Add `search_service.py` with query builder + cursor helpers
* [ ] Extend `GET /prompts` to accept new params; integrate with `prompt_service.list_prompts`
* [ ] Add/verify indexes (DB-002 migration if missing)
* [ ] Add rate-limit on search requests (simple in-memory or Redis)
* [ ] Telemetry event on success (duration, result\_count, hash(q), filters\_used)

**Frontend**

* [ ] Wire `PromptListFilters` inputs to URL + query hook (debounce text)
* [ ] Show applied filter chips; add **Clear all**
* [ ] Implement “Load more” using `next_cursor` (or simple paging)
* [ ] Display small result count and (optional) query time

**Docs/CI**

* [ ] Update OpenAPI + docs; add EXPLAIN/perf checks in CI (smoke)

---

## 10) Open Questions (TBD)

1. Do we need **OR** semantics for tags in P1 (`any`) or keep **AND** only?
2. Should we expose **relevance** score to clients (even if just for debugging)?
3. Cursor vs offset for P1? (Recommended: cursor; fallback: offset with warning about sort changes.)
4. Accept **`use_cases[]`** as client param and alias to `purposes[]` server-side? (Recommended yes for compatibility.)

---

## Definition of Done

* All ACs pass; indexes present; API documented; Vault filters/search wired and fast; telemetry emitted; tests green (unit, integration, UI, and perf smoke).
