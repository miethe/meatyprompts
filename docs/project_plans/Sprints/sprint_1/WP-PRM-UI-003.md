# **User Story WP-PRM-UI-003 — Prompt Creation v2 & Prompt Card Enhancements (Web)**

**Epic:** Prompt Vault — Advanced Metadata & UX

---

## 1 · Narrative

As a **power-user** of MeatyPrompts on the web, I want the “New Prompt” flow to capture richer metadata (Models, Tools, Platforms, Purpose tags) and I want Prompt cards to surface these details (incl. version badge) with an inline detail/edit modal, so that I can organise, discover, and refine my prompt library with minimal friction while setting the stage for future version control.

---

## 2 · Acceptance Criteria

|  #  | Behaviour / Scenario                                                                                                                     | Measure / Test (RTL / Cypress)                                                                                                |
| :-: | ---------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
|  1  | The Manual Prompt form shows **multi-select “Creatable” dropdowns** for Models, Tools, Platforms                                         | Selecting option(s) stores array in form state; selecting “Create new …” sends `POST /lookups/{type}` & updates dropdown list |
|  2  | **Purpose tags** input chips on `Space` press; chips display coloured badge                                                              | Tag array updated; jest-axe shows WCAG-AA colour contrast                                                                     |
|  3  | Submitting form with valid data persists `platforms`, `purpose[]` and other fields to DB & returns version 1                             | Assert 201; response JSON includes `version: 1`                                                                               |
|  4  | Prompt Card renders title, tags row, **version chip** bottom-left                                                                        | Snapshot diff vs. Storybook reference                                                                                         |
|  5  | Clicking a Prompt Card opens **PromptDetailModal** (read-only)                                                                           | Dialog visible with populated fields                                                                                          |
|  6  | Clicking **Edit** in modal toggles inputs to editable; **Save** overwrites latest version (future “Save as new version” toggle disabled) | PUT request fired; card re-renders with new data                                                                              |
|  7  | Prompts page has filter bar (Models, Tools, Purpose)                                                                                     | Selecting filters updates query params & list shrinks accordingly                                                             |
|  8  | CI passes ESLint/TS, Vitest unit tests & Cypress E2E                                                                                     | Green build                                                                                                                   |

---

## 3 · Context & Dependencies

* **Depends on:** WP-APP-UI-001 (web scaffold), existing Prompt CRUD backend
* **Forward hooks:**

  * WP-PRM-VSN-004 — Full version branching & diff viewer
  * WP-PRM-AI-005 — AI-Automated prompt generation
  * MP-AUTH-SEC-001 — Auth guard for edit rights

---

## 4 · Architecture & Implementation Details

### 4.1 Database & Schema

| Table                | Change                                                                                                  |
| -------------------- | ------------------------------------------------------------------------------------------------------- |
| **prompt\_versions** | + `platforms TEXT[]` column (nullable) ; convert `purpose` → `purpose TEXT[]` for multi-tag support     |
| **LOOKUP tables**    | `models_lookup / tools_lookup / platforms_lookup / purposes_lookup` (`id UUID PK`, `value TEXT UNIQUE`) |

### 4.2 API

| Method   | Path                                    | Notes                              |
| -------- | --------------------------------------- | ---------------------------------- |
| **GET**  | `/api/v1/lookups/{type}`                | Return list for dropdowns          |
| **POST** | `/api/v1/lookups/{type}`                | Upsert new value                   |
| **GET**  | `/api/v1/prompts?model=&tool=&purpose=` | Overlap filter (`&&`)              |
| **PUT**  | `/api/v1/prompts/{id}`                  | Update latest version (v1 for now) |

> Prompt Pydantic models already support arrays for `models` & `tools`; we will extend with `platforms` and convert `purpose` to list.

Service layer: add `create_lookup`, `list_lookups`, `filter_prompts`, and extend `create_prompt` / `update_prompt` to persist `platforms` & `purpose` arrays.

### 4.3 Frontend (Next.js + Tailwind + shadcn/ui)

```
web/src/
 ├─ components/
 │   ├─ form/CreatableMultiSelect.tsx
 │   ├─ form/TagInput.tsx
 │   ├─ PromptCard.tsx
 │   ├─ PromptDetailModal.tsx
 │   └─ filters/PromptListFilters.tsx
 ├─ contexts/LookupContext.tsx
 ├─ lib/api/lookups.ts
 └─ types/Lookup.ts
```

* **CreatableMultiSelect:** wraps `@tanstack/react-select` `Creatable` in multi mode.
* **TagInput:** uses `@pathofdev/react-tag-input` for chip UX.
* **PromptCard:** add `<Badge>` row & `<Chip variant="subtle">v1</Chip>`.
* **PromptDetailModal:** shadcn `<Dialog>`; read-only → editable state toggle.
* **Filters:** sticky `<Sheet>` with three CreatableMultiSelect components bound to URL.

### 4.4 State Management

* Extend `PromptContext` with `lookups`, `filters`.
* SWR or React-Query for `/lookups/*` (stale-while-revalidate).

### 4.5 Observability

* Sentry span `lookup.create` on option add.
* Prometheus counter `prompt_version_write_total{action="update"}`.

---

## 5 · Testing Strategy

| Layer           | Tool                  | Focus                                                  |
| --------------- | --------------------- | ------------------------------------------------------ |
| **Unit**        | Vitest + RTL          | TagInput chip creation, CreatableSelect onCreateOption |
| **Integration** | RTL                   | ManualPromptForm → submit payload arrays               |
| **E2E**         | Cypress               | Add new Tool, create prompt, filter list, edit prompt  |
| **A11y/Perf**   | Lighthouse + jest-axe | Modal focus-trap, colour contrast                      |

---

## 6 · Risks & Mitigations

| Risk                                           | Impact      | Mitigation                                                                |
| ---------------------------------------------- | ----------- | ------------------------------------------------------------------------- |
| Lookup tables grow & slow dropdowns            | UX lag      | Paginate + cache; archival flag                                           |
| Multi-array migrations break existing data     | Data loss   | Write idempotent migration, back-fill default empty arrays                |
| Inline edit overwrites unique versioning later | History gap | Disable “Save as new version” now; warn in ADR that edits == v1 overwrite |

---

## 7 · Documentation & Artifacts

| File                              | Action                                              |
| --------------------------------- | --------------------------------------------------- |
| `docs/adr/004_lookup_strategy.md` | **NEW** — Why lookup tables vs enums                |
| `docs/api/prompts.md`             | Add filter query & lookup endpoints                 |
| `docs/ux/prompt_card.png`         | Figma snapshot with tags & version chip             |
| Storybook                         | Add PromptCard variants (tags, no tags, long title) |

---

## 8 · Future Placeholders

* **Version dropdown** on version chip (disabled).
* **Dynamic Card styling** by Model / Tool icon.
* **Semantic Search** (pgvector) integration.

---

## 9 · Pseudocode (excerpt)

```ts
// lib/api/lookups.ts
export async function createLookup(type: 'model'|'tool'|'platform'|'purpose', value: string) {
  const res = await fetch(`/api/v1/lookups/${type}`, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ value }),
  });
  if (!res.ok) throw new Error('Failed to create lookup');
  return res.json(); // returns {id, value}
}
```

---

Delivering this story will give users **richer metadata capture, discoverability filters, and an editable detail view** while providing the backend scaffolding needed for upcoming prompt versioning and AI-assisted creation.
