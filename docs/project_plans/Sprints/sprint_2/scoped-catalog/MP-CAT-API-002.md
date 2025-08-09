# MP-CAT-API-002 — **Catalog API, Auth Context & Caching (Models)**

> **Epic:** Catalogs & Metadata
> **As a** client app, **I want** endpoints to read the effective models list and manage my private entries, **so that** users can see “Official” + “Yours” and add their own safely.

---

## 1 · Narrative

*As a* developer, *I want* REST endpoints with proper auth context (user id/role), error mapping, and cache headers, *so that* the UI can fetch a fast, secure union of system and user entries and let users create/edit their private ones.

---

## 2 · Acceptance Criteria

| # | Behaviour                                                                                                              | Measure / Test                                               |
| - | ---------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| 1 | Middleware sets `app.user_id`, `app.role` Postgres settings each request                                               | Unit test stubs auth → verifies settings applied             |
| 2 | `GET /catalog/models?effective=true` returns system + user rows for caller, grouped via `section` = “Official”/“Yours” | Integration test: two users; correct grouping; no cross-leak |
| 3 | `POST /catalog/models` creates `scope='user'` bound to caller                                                          | 201 + body reflects `scope='user'`, `owner_id`               |
| 4 | `PUT/DELETE /catalog/models/{id}` only allowed for owner (user) or admin (system)                                      | 403/404 for non-owners; 200/204 for owners/admins            |
| 5 | Uniqueness conflicts map to `409 Conflict` with friendly message                                                       | Insert duplicate → 409                                       |
| 6 | System list uses ETag/Last-Modified; supports `If-None-Match` / `If-Modified-Since`                                    | Cache test returns 304; warm path P95 <150 ms                |
| 7 | OpenAPI updated; example payloads provided                                                                             | `/openapi.json` includes routes/schemas                      |

---

## 3 · Context & Dependencies

* **Depends on:** MP-CAT-DB-001 applied.
* **Forward hooks / future:** moderation (`/catalog/models/suggest`); workspace scope; admin seeding endpoint.

---

## 4 · Architecture & Implementation Details

## 4.1 Database & Schema

Uses `models_catalog` from MP-CAT-DB-001; no DB changes in this ticket.&#x20;

## 4.2 API Endpoints

* **File:** `backend/api/routes/catalog_models.py`
* **Routes:**

  * `GET /catalog/models?effective=true|false&scope=system|user` → list; computes `section` per row
  * `POST /catalog/models` → create user-private entry
  * `PUT /catalog/models/{id}` → update (owner or admin)
  * `DELETE /catalog/models/{id}` → delete (owner or admin)
* **Schemas (pydantic):** `ModelMeta`, `ModelCreate`, `ModelRead`
* **Errors:** 400 validation, 403/404 (RLS/ownership), 409 duplicate
  (Endpoint layout follows the project’s route/schema conventions.)&#x20;

## 4.3 Backend Services & Tasks

* **Auth Context Middleware:** resolve user/role → `SET app.user_id`, `SET app.role`.
* **CatalogService:** compose “effective list” (RLS narrows rows), map to `section`.
* **Caching:** Redis key `models:system:v{seed_version}`; compute ETag (stable hash over system rows); set `Last-Modified = max(updated_at)`.&#x20;

## 4.4 Frontend

None here; UI consumes these routes in MP-CAT-UI-003.&#x20;

## 4.5 Observability & Logging

* Spans: `catalog.models.get`, `catalog.models.post` with `user_id`, `scope`, row counts.
* Metrics: request counts, P95 latency, cache hit rate.
* Logs: structured (JSON) with route, status, error\_code.&#x20;

> **Stack:** FastAPI + SQLAlchemy + Postgres 15; Next.js web will consume these.&#x20;

---

## 5 · Testing Strategy

| Layer           | Tool               | New Tests / Assertions                                                             |
| --------------- | ------------------ | ---------------------------------------------------------------------------------- |
| **Unit**        | Pytest             | Middleware sets `app.*`; service maps `section` correctly                          |
| **Integration** | FastAPI TestClient | GET effective=true returns union; POST/PUT/DELETE ownership; 409 dupe; 403/404 RLS |
| **E2E**         | n/a                | n/a                                                                                |
| **Perf**        | k6                 | P95 <150 ms with warm Redis; 304 on ETag                                           |

Conform to the standard matrix.&#x20;

---

## 6 · Documentation & Artifacts

| File / Location                      | Update / Create                                   |
| ------------------------------------ | ------------------------------------------------- |
| `docs/api.md`                        | Add endpoints, examples                           |
| `docs/guides/catalogs.md`            | Add “effective list” semantics, conflict messages |
| `docs/adr/0xx_scoped_catalog_rls.md` | Link API implications                             |

Use the shared docs pattern.&#x20;

---

## 7 · Risks & Mitigations

| Risk                 | Impact                       | Mitigation                                 |   |
| -------------------- | ---------------------------- | ------------------------------------------ | - |
| Cache incoherence    | Stale “Official” list        | Seed version bump; pub/sub invalidation    |   |
| Mis-set auth context | Over-exposure or empty lists | Middleware tests; default-deny RLS         |   |
| ETag bugs            | Missed 304s or over-fetch    | Golden tests for ETag hash & last-modified |   |

---

## 8 · Future Considerations & Placeholders

* `/catalog/models/suggest` into moderation queue
* `workspace` scope enablement
* Soft-delete and deprecation periods

---

## 9 · Pseudocode & Developer Notes

```python
@router.get("/catalog/models")
async def list_models(effective: bool = False, scope: str | None = None):
    # auth ctx already set → RLS applies
    rows = repo.list(effective=effective, scope=scope)
    return [to_response(row) for row in rows]
```

(Follow project’s API and schema conventions.)&#x20;
