# User Story MP-P1-DUP-009 — **Duplicate & Version Bump (“Save as new”)**

> **Epic:** Phase 1 — Manual MVP
> **As a** signed-in creator, **I want** to duplicate a prompt with a one-click “Save as new” action that bumps the version and updates the title, **so that** I can iterate quickly without overwriting prior work.&#x20;

---

## 1 · Narrative

*As a* power user refining prompts, *I want* an explicit **Duplicate** action that creates a **new version** of the current prompt, **increments** the version number, and **suffixes the title with `(vX)`**, *so that* I can preserve history and keep my Vault tidy while iterating. This capability is in scope for Phase-1 and appears in the PRD/API list as `POST /prompts/:id/duplicate`. &#x20;

---

## 2 · Acceptance Criteria

| #    | Behaviour                                                                                                                                                                       | Measure / Test                                                                                                |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| AC-1 | From **Prompt Detail** and **Card** menus, I can choose **Duplicate**.                                                                                                          | UI renders a Duplicate control in modal/footer and on card actions; RTL asserts presence.                     |
| AC-2 | Calling `POST /prompts/:id/duplicate` creates a **new PromptVersion** row under the same header with **version = latest + 1**, copies all versioned fields, updates timestamps. | API returns the new version; DB shows new row with incremented `version` and fresh `created_at/updated_at`.   |
| AC-3 | Header **title** is updated to include **`(vX)`** where `X` is the new version.                                                                                                 | After duplicate, `GET /prompts/:id` hydration shows title with suffix. (Spec mandates suffix.)                |
| AC-4 | **Tags** stay on the header; models/providers/use\_cases stay on the version; **no schema changes** required.                                                                   | Verify persisted fields match existing ORM split (header vs. version).                                        |
| AC-5 | **Security**: owner-scoped; 401 if unauthenticated.                                                                                                                             | API tests with/without session/JWT. (Follows Phase-1 NFR security posture.)                                   |
| AC-6 | **Telemetry** event `prompt_duplicated` captured with `{prompt_id, new_version}`; p95 latency ≤150ms server-side.                                                               | Assert event emitted; perf smoke meets NFR.                                                                   |

---

## 3 · Context & Dependencies

* **Depends on**

  * **MP-P1-DB-002** baseline schema (prompts + prompt\_versions split) & indexes.&#x20;
  * **MP-P1-API-003** CRUD & hydration patterns we extend for duplicate.&#x20;
* **Related**

  * **Copy variants** and **Editor** are separate flows; duplication should not alter copy behaviour or editor autosave.&#x20;
* **Planned later**

  * Collections: duplicated versions remain in the same collections only when that story defines semantics (for P1, **no collection changes**).&#x20;

---

## 4 · Architecture & Implementation Details

## 4.1 Database & Schema

* **No new tables**. Use existing ORM split:

  * Header: id/title/tags/timestamps.&#x20;
  * Version: `version`, `body`, `access_control`, `target_models`, `providers`, `use_cases`, `…`, timestamps. &#x20;
* **Version type** is currently **String**. For P1, treat as a numeric string and **increment**; DB-002 may later migrate to INT (already implied in PRD). &#x20;

## 4.2 API Endpoints

* **File:** `api/routes/prompts.py`
* **New route:**

  ```py
  @router.post("/prompts/{prompt_id}/duplicate", response_model=Prompt)
  def duplicate_prompt_endpoint(prompt_id: uuid.UUID, db: Session = Depends(get_db)):
      return prompt_service.duplicate_prompt(db=db, prompt_id=prompt_id)
  ```

  (Existing routes: POST/GET/PUT for prompts are already present.) &#x20;

## 4.3 Backend Services & Tasks

* **File:** `services/prompt_service.py`
* **New service function `duplicate_prompt(db, prompt_id)`**

  * Load **latest version** for `prompt_id` ordered by `version DESC`. (Pattern exists in `update_prompt`.)&#x20;
  * Compute `new_version = str(int(latest.version) + 1)` (if non-numeric, fallback to suffix `-copy` and set `new_version = "1"`; log a warning).
  * Create **PromptVersionORM** with copied fields (body, access\_control, target\_models, providers, use\_cases, etc.).&#x20;
  * Set timestamps to `now()`.
  * **Update header title** to include ` (v{new_version})` per spec.&#x20;
  * Commit & return hydrated `Prompt` (reuse list/hydration mapping used in service).&#x20;
* **Telemetry:** emit `prompt_duplicated` with attributes; follow PRD telemetry posture.&#x20;

## 4.4 Frontend (React)

* **Prompt Detail Modal**: add **Duplicate** button next to **Edit** in footer; on click, call API then open the new version in the modal.&#x20;
* **Prompt Card**: add Duplicate entry in the card actions (e.g., overflow menu). Version pill already displays `vX`.&#x20;
* **State refresh**: after success, re-fetch `/prompts` or update the local cache (TanStack Query key) so the new version appears at the top (sorted by updated).
* **A11y**: ensure buttons have `aria-label="Duplicate prompt"`.

## 4.5 Observability & Logging

* **Tracing**: `duplicate.start` → `duplicate.persisted` with `{prompt_id, new_version}`.
* **Metrics**: counter `prompts_duplicate_total`; histogram `prompts_duplicate_latency_ms`.
* **Logging**: structured log with obfuscated title (length only) + ids.

---

## 5 · Testing Strategy

| Layer             | Tooling            | Coverage                                                                                                                                          |
| ----------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Unit (backend)    | pytest             | `duplicate_prompt` increments version, copies fields, updates timestamps; title suffix applied; non-numeric version fallback path.                |
| Integration (API) | FastAPI TestClient | `POST /prompts/{id}/duplicate` → 201; response has incremented `version` and suffixed title; 401 without auth (when auth middleware is enabled).  |
| SQL/Perf          | EXPLAIN ANALYZE    | Latest version lookup uses `ORDER BY version DESC` and prompt\_id index; p95 under NFR budget.                                                    |
| Frontend unit     | Jest/RTL           | Buttons render; clicking Duplicate calls API and displays the new version in UI (modal + card).                                                   |
| E2E               | Cypress            | From modal → Duplicate → title shows `(vX)`; close & verify card shows `vX` pill.                                                                 |

---

## 6 · Documentation & Artifacts

| File / Location             | Update / Create                                                                          |
| --------------------------- | ---------------------------------------------------------------------------------------- |
| `docs/api.md`               | Add `POST /prompts/{id}/duplicate` with request/response example and title suffix rule.  |
| `docs/telemetry/events.md`  | Define `prompt_duplicated` event schema & dashboard counters.                            |
| `docs/guides/versioning.md` | Explain versions, duplication behaviour, and UI cues (`vX` pills).                       |
| OpenAPI                     | Add the new route under Prompts; mark as private Phase-1 API.                            |

---

## 7 · Risks & Mitigations

| Risk                                                                                 | Impact                    | Mitigation                                                                         |
| ------------------------------------------------------------------------------------ | ------------------------- | ---------------------------------------------------------------------------------- |
| **Version stored as string** may sort incorrectly lexicographically (`"10"` < `"2"`) | Wrong “latest” pick       | Cast to INT when computing next; enforce numeric regex; DB-002 to migrate to INT.  |
| Title suffix drift (double `(vX)`)                                                   | Messy titles              | When applying suffix, strip any trailing `(vN)` before adding new.                 |
| Concurrency (two duplicates at once)                                                 | Duplicate version numbers | Use transaction + `SELECT … FOR UPDATE` on latest row or retry on conflict.        |
| Collections semantics not yet final                                                  | UX confusion              | For P1 keep collections unchanged; document behaviour; revisit in COLL-010.        |

---

## 8 · Future Considerations & Placeholders

* **Branching / rollback** UI later (Phase-2 “Prompt Vault” ambitions include branching).&#x20;
* **Semantic versioning** (e.g., `1.1`) if a minor-version concept is introduced later—reserve only in docs; P1 sticks to integers.
* **Activity log** (“duplicated from X at time Y”)—event only in P1; UI feed later.

---

## 9 · Developer Notes (minimal pseudocode)

```python
# services/prompt_service.py
def duplicate_prompt(db: Session, prompt_id: UUID) -> Prompt:
    latest = (db.query(PromptVersionORM)
                .filter(PromptVersionORM.prompt_id == prompt_id)
                .order_by(PromptVersionORM.version.desc())
                .first())                                # existing pattern used in update() :contentReference[oaicite:40]{index=40}
    if not latest:
        raise NotFound

    # Compute next version (string → int → string); fallback if non-numeric
    try:
        new_ver = str(int(latest.version) + 1)
    except ValueError:
        new_ver = "1"

    # Copy fields into new version
    new_v = PromptVersionORM(
        prompt_id=prompt_id, version=new_ver,
        body=latest.body, access_control=latest.access_control,
        target_models=latest.target_models, providers=latest.providers,
        integrations=latest.integrations, use_cases=latest.use_cases,
        category=latest.category, complexity=latest.complexity,
        audience=latest.audience, status=latest.status,
        input_schema=latest.input_schema, output_format=latest.output_format,
        llm_parameters=latest.llm_parameters, success_metrics=latest.success_metrics,
        sample_input=latest.sample_input, sample_output=latest.sample_output,
        related_prompt_ids=latest.related_prompt_ids, link=latest.link,
    )
    db.add(new_v)

    # Suffix title on header
    header = db.query(PromptHeaderORM).get(prompt_id)
    header.title = re.sub(r"\s\(v\d+\)$", "", header.title) + f" (v{new_ver})"  # :contentReference[oaicite:41]{index=41}

    db.commit(); db.refresh(new_v)
    return hydrate_prompt(new_v)  # reuse existing mapping :contentReference[oaicite:42]{index=42}
```

---

# Definition of Done

* New **POST `/prompts/{id}/duplicate`** route deployed and documented.&#x20;
* Duplicating from **Card** and **Detail** produces a new version with **incremented version** and **title suffix `(vX)`**; timestamps updated; owner-scoped; telemetry captured.&#x20;
* Tests (unit, integration, E2E) pass; perf budget respected; OpenAPI & guides updated.
