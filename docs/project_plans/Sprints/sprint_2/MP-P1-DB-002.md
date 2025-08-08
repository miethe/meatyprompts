# User Story MP-P1-DB-002 — **Baseline Schema & Indexes**

> **Epic:** Phase 1 — Manual MVP
> **As a** platform engineer, **I want** a stable Phase-1 database schema with required tables, enums, system fields, and indexes, **so that** the API/UI can deliver prompt CRUD, basic filtering, and future-ready hooks without rework.

---

## 1 · Narrative

Phase-1 centers on a personal **Prompt Vault** with **create/edit**, **tags/models**, **basic filters**, and **future-ready scaffolding** (collections, share tokens, pgvector reserved). This story establishes the **Postgres schema + Alembic migrations** needed before API and UI stories proceed. It explicitly includes **owner scoping**, **system fields**, **reserved columns**, and **indexes** to hit the PRD’s performance target (search p95 <150 ms @ ≤5k prompts/user; list render p95 <200 ms).&#x20;

---

## 2 · Acceptance Criteria

| # | Behaviour                                                                                          | Measure / Test                                                                                                                                                          |
| - | -------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | Alembic migration creates/updates all Phase-1 tables, FKs, enums, system fields, reserved columns. | `alembic upgrade head` succeeds on fresh DB and from previous baseline; schema matches data dictionary.                                                                 |
| 2 | `prompts` are **owner-scoped**; queries can filter by `owner_id` and sort by `updated_at`.         | Index exists on `(owner_id, updated_at)`; EXPLAIN shows index usage; API list endpoint later returns correct per-user data.                                             |
| 3 | **Versioned prompt content** model exists and aligns with Phase-1 fields in UI form.               | Columns for `title`, `body`, `use_cases[]`, `target_models[]`, `providers[]`, `integrations[]`, `tags[]`, `access_control`, `link`, etc., exist and round-trip via ORM. |
| 4 | **Collections** tables exist and support many-to-many membership.                                  | `collections` and `collection_prompts` tables created with PK/FKs; unique composite key on (collection\_id, prompt\_id).                                                |
| 5 | **Share tokens** table exists (feature-flag path later).                                           | `share_tokens` with `token` unique, `revoked_at` nullable.                                                                                                              |
| 6 | **Lookup** tables (models/tools/platforms/purposes) exist or are confirmed present.                | `*_lookup` tables present with `value UNIQUE`; seed optional baseline; endpoints already reference them.                                                                |
| 7 | **Indexes** enable Phase-1 filters & search starter.                                               | Trigram/FTS or GIN indexes on `prompts.title` and version `body`; GIN on tags (if normalized) or array\_ops if stored as array. Meets p95 perf budget in perf check.    |
| 8 | **Reserved columns** exist but are unused.                                                         | `prompts.block_count INT DEFAULT 0`, `prompts.embedding VECTOR NULL`, `prompts.icon_url TEXT NULL`; `pgvector` installed.                                               |
| 9 | **Docs updated**: data dictionary + migration runbook.                                             | `docs/data-model.md` and `docs/runbooks/migrations.md` updated; table/column descriptions align with PRD.                                                               |

---

## 3 · Context & Dependencies

* **Depends on**

  * **MP-P1-AUTH-001** for user identities; DB must have `users` to FK `owner_id`.&#x20;
* **Unblocks**

  * **MP-P1-API-003** CRUD routes; **MP-P1-UI-004** card grid; **TAG-006 / SRCH-007** filters/search.&#x20;

---

## 4 · Architecture & Implementation Details

### 4.1 Current state (what exists)

* ORM models use a **header + version** split: `prompts` (id, title, tags, timestamps) and `prompt_versions` (versioned content + arrays for models/providers/use\_cases). This exists but **lacks owner scoping and several Phase-1 fields**, and uses `version` as **String**.
* Service code lists prompts by joining header + latest version, filtering **arrays** for `model/provider/use_case`. Indexing is needed on join + created/updated.

### 4.2 Target schema (Phase-1)

> We will **keep the header + version approach** for P1 (minimizes rework, matches current code), but add missing fields + indexes and owner scoping. We’ll also add **collections** and **share\_tokens** tables and confirm **lookup** tables.

**Tables & columns (DDL outline):**

* **users** (for FK): `id UUID PK, email, name, avatar_url, created_at` (from AUTH story).&#x20;

* **prompts** (header, owner-scoped)
  `id UUID PK, owner_id UUID FK -> users(id), title TEXT NOT NULL, tags TEXT[] NULL, is_favorite BOOL DEFAULT FALSE, is_archived BOOL DEFAULT FALSE, block_count INT DEFAULT 0, embedding VECTOR NULL, icon_url TEXT NULL, created_at TIMESTAMPTZ DEFAULT now(), updated_at TIMESTAMPTZ DEFAULT now()`
  **Indexes:** `IX_prompts_owner_updated (owner_id, updated_at DESC)`; optional `GIN(tags)` if normalized to join-table later.&#x20;

* **prompt\_versions** (versioned content)
  `id UUID PK, prompt_id UUID FK -> prompts(id), version INT NOT NULL, body TEXT NOT NULL, access_control prompt_access_control NOT NULL, use_cases TEXT[] NOT NULL, target_models TEXT[] NULL, providers TEXT[] NULL, integrations TEXT[] NULL, category TEXT NULL, complexity TEXT NULL, audience TEXT NULL, status TEXT NULL, input_schema JSONB NULL, output_format TEXT NULL, llm_parameters JSONB NULL, success_metrics JSONB NULL, sample_input JSONB NULL, sample_output JSONB NULL, related_prompt_ids UUID[] NULL, link TEXT NULL, created_at TIMESTAMPTZ DEFAULT now(), updated_at TIMESTAMPTZ DEFAULT now()`
  **Check/Enum:** `prompt_access_control` ENUM at least `('private','unlisted')` for P1 (UI shows extra values but keep feature-gated at API).&#x20;

  **Indexes:**

  * `IX_versions_prompt_desc (prompt_id, version DESC)` (latest lookup)
  * **Search starter:** trigram/TS index on `(body)`; trigram on `prompts.title`.

* **collections**
  `id UUID PK, owner_id UUID FK -> users(id), name TEXT NOT NULL, created_at, updated_at`
  **Unique:** `(owner_id, name)`; **Index:** `(owner_id, name)` for lookups.&#x20;

* **collection\_prompts** (bridge)
  `collection_id UUID FK, prompt_id UUID FK, PRIMARY KEY(collection_id, prompt_id)`; **Index:** `(prompt_id, collection_id)`.&#x20;

* **share\_tokens** (flagged)
  `id UUID PK, prompt_id UUID FK, token TEXT UNIQUE NOT NULL, created_at, revoked_at TIMESTAMPTZ NULL`.&#x20;

* **lookup tables** (already present): `models_lookup`, `tools_lookup`, `platforms_lookup`, `purposes_lookup` with `value UNIQUE`. Ensure migrations create them in shared metadata if not already.&#x20;

> Note: The PRD’s “normalized” model (join tables `prompt_tags` / `prompt_models`) is intentionally **deferred**; we keep arrays for P1 to reduce scope. We’ll revisit normalization during **SRCH-007** if we need richer tag analytics.&#x20;

### 4.3 Migrations & project structure

* **Files**

  * `backend/alembic/versions/20250808_p1_baseline.py` – full DDL above.
  * **Enum** creation for `prompt_access_control`.
  * **Extension**: ensure `CREATE EXTENSION IF NOT EXISTS pg_trgm;` and `pgvector`.&#x20;

* **ORM updates** (`app/models/prompt.py`)

  * Add `owner_id`, `is_favorite`, `is_archived`, reserved columns on **PromptHeaderORM**.
  * Change **PromptVersionORM.version** from `String` → `Integer`.
  * Consider leaving Pydantic `Prompt.version` as `int` in responses; update `PromptCreate` as needed.

* **Service adjustments (follow-up in API-003)**

  * When listing, **join by owner\_id**; when updating, ensure **latest version** selection via `(prompt_id, version DESC)` uses the new INT index.

### 4.4 Index strategy (Phase-1)

* **Read path:** vault list = **by owner, updated\_at desc** → composite B-tree `(owner_id, updated_at)`.&#x20;
* **Search starter:**

  * `CREATE INDEX ix_prompts_title_trgm ON prompts USING GIN (title gin_trgm_ops);`
  * `CREATE INDEX ix_versions_body_trgm ON prompt_versions USING GIN (body gin_trgm_ops);`
  * Future FTS materialization (deferred to SRCH-007).

---

## 5 · Testing Strategy

| Layer               | Tooling          | New tests / assertions                                                                                    |
| ------------------- | ---------------- | --------------------------------------------------------------------------------------------------------- |
| **Migration smoke** | Alembic + pytest | Upgrade/downgrade works; all tables present; enums/extensions exist.                                      |
| **Constraints**     | pytest           | Owner FK enforced; composite PKs; unique `(owner_id,name)` for collections; unique `share_tokens.token`.  |
| **Indexes**         | psql/pytest      | `pg_indexes` contains expected indexes; EXPLAIN on typical list/search shows index usage.                 |
| **ORM round-trip**  | pytest           | Insert PromptHeader + Version; list service returns hydrated Prompt with `title`, `tags`, arrays cleaned. |
| **Perf (light)**    | k6/Locust        | List 5k prompts/user: p95 query time meets budget (index verified).                                       |

---

## 6 · Documentation & Artifacts

* **docs/data-model.md** — ERD, table/column descriptions, enums, indexes, reserved fields.
* **docs/runbooks/migrations.md** — how to run/rollback, how to re-create extensions.
* **ADR**: `docs/adr/ADR-00X-db-p1-schema.md` — decide **arrays vs normalized** for tags/models in P1 (defer normalization).

---

## 7 · Risks & Mitigations

| Risk                                     | Impact                    | Mitigation                                                                                                  |
| ---------------------------------------- | ------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Version type change (`String`→`Integer`) | Runtime cast errors       | Migration includes safe cast (USING version::int) or recreates column with backfill; align Pydantic models. |
| Search perf misses targets               | Slow vault/search         | Add trigram indexes now; revisit FTS/materialized column in SRCH-007.                                       |
| Missing owner scoping                    | Data leakage across users | Mandatory `owner_id` FK + composite index; enforce in service layer and authz.                              |

---

## 8 · Open Questions (TBD)

1. **Access control enum** — Keep minimal `('private','unlisted')` or include UI’s broader values (`team-only`, `role-based`) now but feature-gate?&#x20;
2. **Tags normalization** — Stay as `TEXT[]` in header for P1 or add `prompt_tags` now? (Perf vs analytics trade-off.)&#x20;
3. **Link scope** — Keep `link` at **version** level (current ORM) or move to header as `link_url`? PRD suggests header; UI collects it once per prompt.&#x20;

---

## 9 · Definition of Done (DoD)

* Migrations applied, CI green; ORM models updated; indexes present; basic perf check passes; documentation + ADR merged; downstream API-003 & UI-004 can consume schema without changes.

> Ordering note: This story **precedes** API-003 and UI-004; it provides the foundation for the Phase-1 backlog and satisfies the PRD’s “Scalability & performance” and “Security/Privacy” NFR hooks.
