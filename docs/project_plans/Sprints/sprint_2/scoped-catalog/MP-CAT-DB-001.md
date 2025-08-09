# MP-CAT-DB-001 — **Scoped Catalog DB & RLS Foundation (Models)**

> **Epic:** Catalogs & Metadata
> **As a** MeatyPrompts user, **I want** official pick-lists plus my own private entries, **so that** I can use a curated baseline and extend it privately without exposing my additions.

---

## 1 · Narrative

*As a* creator configuring prompts, *I want* a single source of truth for “models” that supports **system** (official) and **user** (private) scope, guarded by **Row-Level Security (RLS)**, *so that* I can safely mix official items with my own without leaking data.

---

## 2 · Acceptance Criteria

| # | Behaviour                                                                                                          | Measure / Test                                                                       |
| - | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------ |
| 1 | Alembic migration creates `catalog_scope` enum and `models_catalog` table with columns, uniques, indexes, triggers | Migration applies cleanly up/down; schema matches spec via `\d+` and ORM reflection  |
| 2 | RLS enabled on `models_catalog` with default-deny                                                                  | `SELECT` denied without policies; test proves 0 rows visible by default              |
| 3 | RLS `SELECT` allows: `scope='system'` for all; `scope='user'` only for `owner_id=app.user_id`                      | SQL tests with two users: A sees A’s user items + all system; B cannot see A’s items |
| 4 | RLS `INSERT/UPDATE/DELETE` allows only owner for `scope='user'`; only admin can write `scope='system'`             | SQL tests show 403/permission error surfaces as 0 rows affected                      |
| 5 | Uniqueness per scope: `(scope, provider, name, owner_id?, workspace_id?)`                                          | Duplicate insert yields DB 23505; API will map to 409 in a later ticket              |
| 6 | Seed initial **system** set (OpenAI/Anthropic/Gemini, etc.)                                                        | Seed script populates N≥15 entries; repeatable & idempotent                          |
| 7 | Performance: “effective list” WHERE clause is index-backed                                                         | `EXPLAIN ANALYZE` shows index usage; P95 sub-ms on dev dataset                       |

*(Table/acceptance layout follows the standard story template.)*&#x20;

---

## 3 · Context & Dependencies

* **Depends on:** none (greenfield DB).
* **Forward hooks / future:** middleware to set `app.user_id/app.role` (MP-CAT-API-002); optional `workspace_id` scope and suggestion queue in future.

---

## 4 · Architecture & Implementation Details

## 4.1 Database & Schema

* **Enum:** `catalog_scope` = `system | workspace | user`.
* **Table:** `models_catalog`

  * `id UUID PK`, `scope catalog_scope NOT NULL DEFAULT 'system'`
  * `owner_id UUID NULL → users(id)` (required for `user`)
  * `workspace_id UUID NULL → workspaces(id)` *(placeholder)*
  * `provider TEXT NOT NULL`, `name TEXT NOT NULL`, `display_name TEXT NOT NULL`
  * `meta JSONB DEFAULT '{}'`, `alias_of_id UUID NULL → models_catalog(id)`
  * `is_active BOOLEAN DEFAULT TRUE`, `created_at/updated_at TIMESTAMPTZ DEFAULT now()`
  * **Unique:** `UNIQUE(scope, provider, name, COALESCE(owner_id,'00..00'), COALESCE(workspace_id,'00..00'))`
  * **Indexes:** `(scope, provider, name)`, `(owner_id)`, `(workspace_id)`
* **Trigger:** `updated_at` ON UPDATE.
* **RLS:** enable; **SELECT/INSERT/UPDATE/DELETE** policies as per ACs.
* **Migration file:** `backend/alembic/versions/{YYYYMMDD}_scoped_catalog_models.py`.&#x20;

## 4.2 API Endpoints

None in this ticket. (Exposed in MP-CAT-API-002.)&#x20;

## 4.3 Backend Services & Tasks

None in this ticket. (Service layer comes with API.)&#x20;

## 4.4 Frontend

None. (UI lands in MP-CAT-UI-003.)&#x20;

## 4.5 Observability & Logging

* Migration logs; audit DDL executed.
* Optional: emit metric “catalog.seed.count”.&#x20;

---

## 5 · Testing Strategy

| Layer           | Tool                 | New Tests / Assertions                              |
| --------------- | -------------------- | --------------------------------------------------- |
| **Unit**        | Pytest               | Uniqueness & trigger behaviour                      |
| **Integration** | Asyncpg / TestClient | RLS: cross-user visibility blocked; owner permitted |
| **E2E**         | n/a                  | n/a                                                 |
| **Perf**        | EXPLAIN ANALYZE      | Index usage for “effective list” query              |

Follow the standard testing matrix.&#x20;

---

## 6 · Documentation & Artifacts

| File / Location                      | Update / Create                             |
| ------------------------------------ | ------------------------------------------- |
| `docs/adr/0xx_scoped_catalog_rls.md` | Decision record for scoped catalogs + RLS   |
| `docs/guides/catalogs.md`            | How to add a new catalog using this pattern |
| `docs/api.md`                        | (TBD in API ticket)                         |

Use the common docs table format.&#x20;

---

## 7 · Risks & Mitigations

| Risk                 | Impact                  | Mitigation                          |   |
| -------------------- | ----------------------- | ----------------------------------- | - |
| Over-permissive RLS  | Data leakage            | Default-deny; DB-level tests        |   |
| Seed drift           | Inconsistent system set | Idempotent seed; lock seed version  |   |
| Slow effective query | Laggy dropdown          | Composite indexes; query plan check |   |

---

## 8 · Future Considerations & Placeholders

* `workspace` scope activation
* Moderation queue (`catalog_suggestions`)
* Soft-delete and validity windows (`valid_from/to`)
* Versioning of entries

---

## 9 · Pseudocode & Developer Notes

*No code necessary beyond migrations; follow backend stack (FastAPI + SQLAlchemy + Alembic; Postgres 15).*&#x20;
