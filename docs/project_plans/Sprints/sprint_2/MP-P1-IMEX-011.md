# User Story MP-P1-IMEX-011 — **Import/Export (CSV/JSON)**

> **Epic:** Phase 1 — Manual MVP
> **As a** signed-in creator, **I want** to import prompts from CSV/JSON and export my whole library (or a collection) as JSON, **so that** my data is portable and I can get started fast without manual re-entry. &#x20;

---

## 1 · Narrative

Phase-1 explicitly requires **CSV/JSON import with field mapping** and a **JSON export** of the user’s library (optionally per collection). Export format must be stable and future-proof (“data freedom”), and should align with our copy-variant/Prompt model payload so downstream tools don’t break. &#x20;

---

## 2 · Acceptance Criteria

| # | Behaviour                                                                                                                                                  | Measure / Test                                                                                                                                     |
| - | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | I can **upload** a CSV or JSON file, see a **mapping UI** (columns → fields), preview the first 20 rows, and run **validation** before importing.          | E2E: upload CSV with headers → mapping dialog shows our fields; preview shows parsed rows with per-cell errors. PRD requires import with mapping.  |
| 2 | I can choose **Dry-Run** to get a validation report (counts, row errors) **without** persisting.                                                           | API test: `POST /import?dry_run=true` returns `{valid_count, error_count, errors[]}` and **does not** write rows.                                  |
| 3 | **Commit import** creates prompts using our existing **Prompt** schema (header + latest version) and returns a summary (`created`, `skipped`, `errors`).   | Integration test asserts created rows map to `Prompt` fields as per model.                                                                         |
| 4 | **JSON export** downloads either **(a)** the whole user’s library or **(b)** a single collection as a **JSON array** of `Prompt` objects (stable key set). | API test: `GET /export` and `GET /export?collection_id=...` stream a JSON array matching `Prompt` response fields.                                 |
| 5 | **Security:** owner-scoped; unauthenticated blocked (401).                                                                                                 | API tests with/without auth (per Phase-1 API posture).                                                                                             |
| 6 | **Performance:** Import up to 500 rows synchronously (p95 ≤ 2s); Export p95 ≤ 500ms for ≤ 5k prompts.                                                      | Perf smoke: generate fixture set, measure. Phase-1 perf/NFRs apply.                                                                                |
| 7 | **Telemetry:** `import_started`, `import_completed`, `export_requested`, `export_completed` with counts; no raw content in logs.                           | Unit test asserts events; redact payloads (only sizes/hashes). PRD tracks import/export as part of data freedom.                                   |

---

## 3 · Context & Dependencies

* **Depends on:**

  * **MP-P1-AUTH-001** for `/me` and owner scoping.&#x20;
  * **MP-P1-DB-002** baseline schema (prompts + versions + collections).&#x20;
  * **MP-P1-API-003** Prompt CRUD, used by importer to create rows.&#x20;
* **Integrates with:**

  * **Collections** (optional export by collection).&#x20;
  * **Lookups** (models/purposes) for mapping suggestions and normalization.&#x20;
* **Out of scope (P1):** background jobs for very large files; XLSX; merge/dedupe wizard.

---

## 4 · Architecture & Implementation Details

## 4.1 Database & Schema

* **No new tables** required for P1 (synchronous import/export).
* (Placeholder) If we later support large files/asynchronous processing, add `import_jobs(id, owner_id, status, file_ref, counts, created_at, completed_at)` and a Celery worker. (Defer.)

## 4.2 API Endpoints

Add **private Phase-1** routes (owner-scoped), per PRD list: `POST /import`, `GET /export`.&#x20;

* **File:** `api/routes/imex.py`
* **Schemas (Pydantic):**

  * `ImportMapping`: `{ title: string, body: string, tags?: string, target_models?: string, providers?: string, use_cases?: string, link?: string, access_control?: string, ... }`
    (Fields correspond to our Prompt model & Manual form). &#x20;
  * `ImportPreviewRow`: `{ row_index, valid: bool, errors?: string[], mapped?: PromptCreate }`
  * `ImportResult`: `{ created: int, skipped: int, errors: ImportError[] }`
* **Handlers:**

  ```python
  @router.post("/import")
  async def import_prompts(file: UploadFile, mapping: ImportMapping, dry_run: bool = True) -> Union[ImportPreview, ImportResult]: ...
  @router.get("/export")
  async def export_prompts(collection_id: UUID | None = None) -> StreamingResponse: ...
  ```
* **Behaviours:**

  * **CSV:** detect delimiter, use headers; mapping UI chooses per-column mapping. Arrays (`tags`, `target_models`, `providers`, `use_cases`) parse from comma-separated strings; trim+lowercase where appropriate (tags).
  * **JSON:** accept either an **array of objects** or **NDJSON**; mapping maps object keys to fields; unknown keys ignored.
  * **Validation:** build `PromptCreate` and validate; on failure, include per-row error list (min: title, body, use\_cases, target\_models).&#x20;
  * **Export:** stream JSON array of **`Prompt`** responses (stable shape = our API model), optionally filtered by `collection_id`. &#x20;

## 4.3 Backend Services & Tasks

* **`services/import_service.py` (new)**

  * `parse_csv(file) -> list[dict]`
  * `apply_mapping(rows, mapping) -> list[PromptCreate|Error]`
  * `validate(rows) -> (valid[], errors[])`
  * `commit(db, owner_id, valid_rows) -> ImportResult` (calls `prompt_service.create_prompt` per row).&#x20;
* **`services/export_service.py` (new)**

  * `iter_prompts(db, owner_id, collection_id=None) -> iterator[Prompt]` (reuse list/hydration)&#x20;
  * `stream_json(iterator)` returns a `StreamingResponse` (chunked JSON array).

**Normalization rules (CSV/JSON):**

* `tags` → lowercase, dedupe; `target_models/providers/use_cases` → arrays; `related_prompt_ids` → UUID\[];
* `access_control` → enum as in form; `link` → URL string; `sample_input/output`, `llm_parameters`, `input_schema` accept JSON; validation is identical to the manual form.&#x20;

## 4.4 Frontend (React)

* **Entry points**

  * **Vault Toolbar:** “Import” and “Export” buttons.
  * **Export**: dropdown → “All prompts (JSON)” / “Current collection (JSON)”.
* **Import UI**

  * Stepper Modal: **Upload** → **Map fields** (autodetect headers) → **Preview & Validate** → **Import**.
  * For arrays: show chip preview (split by commas) to hint parsing rules.
  * Dry-run first; on success, enable **Import** CTA with counts.
* **Where to slot UI in current code:**

  * Add “Import” choice near **NewPromptModal** step 0 (next to “Manual”). We already have a stubbed stepper; extend to add Import path.&#x20;
  * In **PromptDetailModal**, no changes (import/export live at list level).&#x20;

## 4.5 Observability & Logging

* **Tracing:** `import.start`, `import.row_validated`, `import.commit`, `export.start`, `export.stream_chunk` (attrs: counts, file\_type, mapping\_hash).
* **Metrics:** counters `imex_import_total{status}`, histograms `imex_import_row_latency_ms`, `imex_export_latency_ms`.
* **Telemetry:** user-level events only store counts/hashes, not row content (privacy).

---

## 5 · Non-Functional Requirements

* **Performance:** meet budgets outlined in AC and Phase-1 NFRs (search/list budgets still apply globally).&#x20;
* **Security/Privacy:** owner scoping; size limits (e.g., 2 MB CSV/JSON); rate-limit import requests; reject rows with HTML/script injection in text fields.
* **Portability:** **Export format guarantees** documented as stable; aligns with `Prompt` API and **copy JSON variant**.&#x20;
* **A11y:** keyboard navigable stepper; form labels; error summaries.

---

## 6 · Testing Strategy

| Layer             | Tool               | Coverage                                                                                                                               |
| ----------------- | ------------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| Unit (backend)    | pytest             | CSV parser: delimiters, quotes, BOM; JSON array/NDJSON; mapping & normalization; invalid rows (missing title/body/arrays).             |
| Integration (API) | FastAPI TestClient | `POST /import?dry_run=true` preview; `POST /import` commit creates prompts; `GET /export` streams valid JSON; 401 without auth.        |
| Contract          | Snapshot           | Exported object keys match **`Prompt`** response model; fail if drift detected.                                                        |
| Frontend unit     | Jest + RTL         | Mapping UI renders detected headers; array splitting UX; dry-run error table; disable Import until no blocking errors.                 |
| E2E               | Cypress            | Upload CSV → map → dry-run → import 3 prompts → appear in grid; export JSON → file downloads; per-collection export filters correctly. |
| Perf              | Bench              | Import 500 rows under 2s; export ≤ 500ms @ 5k prompts (local fixtures).                                                                |

---

## 7 · Documentation & Artifacts

* **`docs/guides/import_export.md`** — file formats, mapping examples, limits, error resolution tips.
* **`docs/api.md`** — `POST /import`, `GET /export` with payload/response examples; note per-collection export. &#x20;
* **ADR:** **ADR-00X Export Format Guarantee** — export == `Prompt` schema; copy-JSON parity.&#x20;

---

## 8 · Risks & Mitigations

| Risk                                                          | Impact              | Mitigation                                                        |
| ------------------------------------------------------------- | ------------------- | ----------------------------------------------------------------- |
| CSV dialect differences (commas vs semicolons, quoted fields) | Parsing errors      | Use `csv.Sniffer`; show header preview; allow delimiter override. |
| Payload drift between export and API `Prompt`                 | Downstream breakage | Snapshot test against `Prompt` model; gate changes via ADR.       |
| Huge files stall request                                      | Timeouts            | Enforce row/file caps; future: async job table + worker (defer).  |
| Dirty/unknown columns                                         | User confusion      | Mapping UI with “ignored columns”; clear docs/examples.           |
| Tag/model normalization inconsistencies                       | Messy data          | Lowercase/dedupe; validate models/purposes; suggest via lookups.  |

---

## 9 · Future Considerations & Placeholders

* **Asynchronous import jobs** (large files), resumable uploads, and email notifications.
* **XLSX** support; **NDJSON export** for streaming pipelines.
* **Merge-on-title** or **upsert** mode (skip/create/update) with conflict rules.
* **Template packs** (starter seed) leveraging the same import path.&#x20;

---

## 10 · Pseudocode & Developer Notes (minimal)

* **Importer flow:** read file → detect type → parse → map → validate (`PromptCreate`) → if `dry_run` return preview; else `create_prompt()` per row.&#x20;
* **Exporter flow:** query owner-scoped prompts (and optional collection join) → stream `Prompt` objects as JSON array; ensure field order stable.

---

# Definition of Done

* Import and export routes shipped and documented; UI stepper for import and toolbar export available.
* Dry-run + commit paths work; owner-scoped; P1 perf budgets met; telemetry emitted.
* Export payload equals **`Prompt`** API schema; contract test in CI; docs & ADR merged.&#x20;
