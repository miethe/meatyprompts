# User Story MP-P1-TAG-006 — **Tags & Target Models (freeform tags + user-managed model list)**

> **Epic:** Prompt CRUD & Metadata
> **As a** creator maintaining a personal prompt vault, **I want** to add freeform tags and select/manage target models, **so that** I can organize prompts and later filter/search them efficiently.

---

## 1 · Narrative

*As a* **prompt author**, *I want* **to assign tags (freeform, normalized) and choose one or more target models (from a user-managed list with the ability to add new entries)** *so that* **my prompts are easy to find and reuse and remain portable across model providers**. (PRD calls for freeform tags with suggestions and a user-managed target model list. )

---

## 2 · Acceptance Criteria

| # | Behaviour                                                                                                                                             | Measure / Test                                                                                                                                           |
| - | ----------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | When creating/editing a prompt, I can enter multiple **tags**; tags are lower-cased, trimmed, deduped on save.                                        | Create/edit via UI → POST/PUT returns tags all in lowercase; duplicates dropped; persisted in `prompts.tags`. Verify via API GET.                        |
| 2 | Tag input shows **type-ahead suggestions** from existing tags.                                                                                        | GET `/tags?limit=20&query=…` returns top matches; UI shows suggestions; RTL test verifies fetch + render.                                                |
| 3 | I can select one or more **target models** from a list and **add a new model** inline if it doesn’t exist.                                            | GET `/lookups/models` populates select; POST `/lookups/models` creates missing values; UI shows the newly added model selected.                          |
| 4 | On **create prompt**, tags are saved on the **header** record and models saved on the **version** record.                                             | Inspect DB via service return; tags appear on header, models on `prompt_versions.target_models`. Unit test asserts correct locations.                    |
| 5 | On **update prompt**, latest version is updated for `target_models` and header `tags` remain consistent with payload.                                 | PUT updates `prompt_versions.target_models` and header tags; integration test verifies response/DB. (Extend service to persist header tags if provided.) |
| 6 | **Validation**: max 20 tags/prompt; tag length 1–32; allowed charset `[a-z0-9._-]` after normalization; max 20 models; model length 1–64.             | Schema validation rejects bad input with 422; unit tests cover edge cases.                                                                               |
| 7 | **Performance**: `/tags` responds in <100ms p95 for ≤5k prompts; `/lookups/models` <100ms p95.                                                        | Add simple index/aggregation; local perf check or flamegraph. (NFR alignment.)                                                                           |
| 8 | **Observability**: create/update emits structured logs + trace spans; counters for `tags.suggest.hit`, `model.lookup.create`.                         | Assert metrics/logs in unit test via test logger; OTEL spans present.                                                                                    |
| 9 | **Compatibility**: Existing UI fields for tags and target models continue to work; naming drift (**use\_cases** vs **purposes**) is resolved/aliased. | ManualPromptForm uses correct lookup key(s); smoke test create/edit. (Unify in lookup hook / route.)                                                     |

---

## 3 · Context & Dependencies

**Depends on:**

* MP-P1-DB-002 — initial prompt tables & arrays are present (tags on header; models array on version). Already defined in models and service.
* MP-P1-API-003 — prompt CRUD endpoints (`POST/GET/PUT /prompts`), to carry the new/validated fields end-to-end. Endpoints exist; we’re extending behavior.

**Forward hooks / future features:**

* **Search & Filters (SRCH story)**: filtering by tags in list API; tag chips on Vault. (This story focuses on capture + suggestions; filtering is covered elsewhere per PRD 7.4.)
* **Import/Export**: includes tags & target\_models fields. Ensure shape aligns with this story.

---

## 4 · Architecture & Implementation Details

### 4.1 Database & Schema

* **Already present**

  * `PromptHeaderORM.tags: ARRAY(String)` — stores tags on the prompt header.
  * `PromptVersionORM.target_models: ARRAY(String)` — stores target model names on versions.

* **No new tables** required for tags (freeform).

* **Lookup tables for models/tools/platforms/purposes** already exist: `models_lookup`, `tools_lookup`, `platforms_lookup`, `purposes_lookup`.

* **Migration**: None required for schema; optional **seed** of baseline model names (OpenAI, Anthropic, etc.) into `models_lookup`. (Aligns with PRD “import baseline list”.)

### 4.2 API Endpoints

* **Prompt CRUD (existing)**

  * `POST /prompts` — accepts `tags[]`, `target_models[]`; persists to header/version respectively. (Verify normalization on service layer.)
  * `PUT /prompts/:id` — extend to update header `tags` when provided (today, PUT primarily updates version fields).

* **New (this story)**

  * `GET /tags?query=&limit=` — returns top tags (by frequency) optionally filtered by prefix.

    * Implementation: simple aggregate over `prompts.tags` (unnest array) grouped by tag, ordered by count desc, limited.
    * Response shape: `[{ tag: string, count: number }]`.
    * (PRD lists `/tags` endpoint.)

* **Lookups (existing)**

  * `GET /lookups/models` — list of model values for select.
  * `POST /lookups/models` — create if not exists; returns canonical value.
  * Service uses type mapping for models/tools/platforms/purposes.

* **Naming drift fix** (minor): UI refers to `use_cases`; backend lookup type is `purposes`. Decision: **alias in UI hook** or **add server alias** `/lookups/use_cases` → `purposes`. (Implement least-risky path this sprint—UI alias.)

### 4.3 Backend Services & Tasks

* **Prompt Service (`app/services/prompt_service.py`)**

  * **Create**: already persists tags on header and target\_models on version. Enforce lower-casing and dedupe for tags before insert.
  * **Update**: extend `update_prompt` to also set header tags if provided (whitelist + write to header).
  * **List**: currently supports filters by model/provider/use\_case; tags filter is part of the search story (not here).

* **Lookup Service (`app/services/lookup_service.py`)**

  * Already supports list + create with de-duplication check. Keep stored values case-preserving but **compare case-insensitive** when creating; store canonical lowercase key if we choose strict normalization.

* **Tags Service (new utility)**

  * `tags_service.top_tags(db, limit, query_prefix)` — perform `unnest(prompts.tags)` aggregate and return counts.

### 4.4 Frontend (React)

* **Files likely impacted**

  * **`ManualPromptForm.tsx`** — has fields for `tags` and `target_models` and the “creatable” behavior that POSTS to lookups on new values. Confirm it uses `/lookups/models` and not a stale key. Add **typeahead suggestions** for tags wired to `/tags`. (The form already pulls lookups and shows help text.)
  * **Lookup Context/Hooks** — ensure keys match server: `models`, `tools`, `platforms`, **`purposes`** (map UI alias `use_cases`→`purposes`).

* **UI behaviors**

  * Tags input: creatable multi-select; normalize to lowercase on blur/commit; dedupe chips client-side.
  * Target models: multi-select backed by `/lookups/models`; allow **inline create** → optimistic add, then confirm from POST.
  * Empty state: show example tag chips (placeholder) per PRD UX notes.

* **Accessibility**

  * Ensure inputs have labels, aria-describedby for help text; keyboard add/remove tokens.

### 4.5 Observability & Logging

* **Tracing**: spans — `tags.suggest.query`, `lookups.models.list`, `lookups.models.create`, `prompt.tags.normalize`. Capture user\_id, prompt\_id, counts. (Project uses OpenTelemetry.)
* **Metrics**: Counters `tags_suggest_requests_total`, `tags_suggest_hits_total`; Histogram `tags_suggest_latency_ms`.
* **Logging**: JSON logs include normalization actions and dedupe count.

---

## 5 · Testing Strategy

| Layer                 | Tool               | New Tests / Assertions                                                                                                                          |
| --------------------- | ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **Unit (backend)**    | Pytest             | Tag normalization/dedupe; `/tags` aggregation (limits, prefix filter); lookup create idempotency; update service writes header tags.            |
| **Integration (API)** | FastAPI TestClient | `POST/PUT /prompts` with various tags/models; `GET /tags` top-N; `GET/POST /lookups/models` happy + duplicate.                                  |
| **Unit (frontend)**   | Jest               | Tag input normalization; select adds new model via POST then selects it; hooks map `use_cases`→`purposes`.                                      |
| **E2E**               | Cypress            | Create prompt with tags + model; refresh → values persist; edit adds a tag; suggestions appear as typing; create-new model inline success path. |
| **Perf/A11y**         | Lighthouse/axe     | Form inputs labelled; no contrast regressions; `/tags` p95 <100ms locally with sample dataset.                                                  |

(Testing framework coverage and patterns per user stories template.)

---

## 6 · Documentation & Artifacts

| File / Location                | Update / Create                                                                                 |
| ------------------------------ | ----------------------------------------------------------------------------------------------- |
| `docs/api.md`                  | Document `GET /tags` + examples; note tag normalization rules; list `/lookups/models` behavior. |
| `docs/guides/metadata.md`      | How to use tags & target models in the UI; screenshots of creatable selects.                    |
| `docs/adr/0xx_lookup_scope.md` | **ADR**: Global vs per-user lookup lists; MVP choice + risks.                                   |
| OpenAPI                        | Ensure `/tags` and `/lookups/*` show in spec.                                                   |
| Seed data                      | `seeds/models_lookup.json` and loader script (optional baseline).                               |

(Artifacts format per story template.)

---

## 7 · Risks & Mitigations

| Risk                                          | Impact                              | Mitigation                                                                                                     |
| --------------------------------------------- | ----------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Tag taxonomy bloat / synonyms                 | Messy UX, poor findability          | Normalize to lowercase; later: synonym map, merge tools (Phase 2).                                             |
| Global lookup tables vs “user-managed” intent | Confusion or unwanted shared values | ADR; MVP uses global + baseline; add owner scoping later or tenant-aware tables.                               |
| Case/spacing inconsistencies                  | Duplicate tags/models               | Strict client-side normalization for tags; server validation; for models keep canonical form (e.g., `gpt-4o`). |
| Performance of `/tags` with large data        | Slow suggestions                    | Index/GIN on tags; cached top-N in Redis later if needed. (NFR alignment.)                                     |

---

## 8 · Future Considerations & Placeholders

* **Auto-tagging & AI suggestions** (explicitly out of Phase 1) — reserve API shape for later.
* **Per-user / per-workspace lookups** — add `owner_id` to lookup tables and scoped endpoints.
* **Tag synonyms / merge tool** — background job to propose merges.
* **Analytics** — track tag usage, model popularity for recommendations.

---

## 9 · Pseudocode & Developer Notes (minimal)

* **Server tag normalization** (before persist):

  * `tags = sorted(unique([slugify_lower(t) for t in tags]))`
* **`/tags` query**:

  * `SELECT tag, COUNT(*) AS cnt FROM (SELECT UNNEST(tags) AS tag FROM prompts) t WHERE tag ILIKE :prefix GROUP BY tag ORDER BY cnt DESC LIMIT :limit;`

---

## Implementation Tasks (dev-ready)

**Backend**

* [ ] `tags_service.py`: implement `top_tags(db, limit=20, query_prefix=None)` aggregate.
* [ ] `api/routes/tags.py`: add `GET /tags` with `limit`, `query` params; pydantic response schema. (Wire to service.)
* [ ] `prompt_service.update_prompt`: allow optional header tag update (normalize/dedupe) in addition to version fields.
* [ ] `lookup_service.create_lookup_value`: compare case-insensitive; cap length; trim.
* [ ] Optional seed: `alembic/versions/…_seed_models_lookup.py` or a separate seed script.

**Frontend**

* [ ] `ManualPromptForm.tsx`:

  * Wire tags input to `GET /tags` suggestions; normalize to lowercase on commit; dedupe.
  * Ensure target\_models select uses `/lookups/models` and POSTs on create; optimistic UI then reconcile.
  * Update hook/context to map `use_cases` → `purposes` until backend alias exists.
* [ ] Add unit tests for inputs and network calls.

**Docs & Ops**

* [ ] Update `docs/api.md` & `OpenAPI` for `/tags`.
* [ ] Add OTEL spans and counters in lookups/tags routes.
* [ ] Add Jest/Pytest/RTL/Cypress tests per Section 5.

---

## Open Questions (TBD)

1. **Scope of “user-managed” models**: Should `models_lookup` be **per-user** (requires `owner_id`) or **global baseline** for MVP? (Recommend MVP = global; revisit post-MVP.)
2. Do we allow **spaces** in tags after normalization, or force `kebab_case`? (Current suggestion allows `[a-z0-9._-]`.)
3. Tag **limits** (count/length) — confirm product limits above are acceptable for MVP.

---

## Traceability

* PRD “Tags & Target Models”: tags are freeform w/ suggestions; target models user-managed importable baseline.
* API shape includes `/prompts` carrying `tags[]` & `target_models[]` and `/tags`.
* Current models/services already store `tags` on header and `target_models` on version.

---

**Definition of Done**

* UX lets users add/select **tags** and **target models** with suggestions & inline create.
* Backed by persisted data (correct tables/columns), with normalized tags and validated models.
* `/tags`, `/lookups/models` endpoints fully wired; logs, metrics, and tests green; docs updated.
