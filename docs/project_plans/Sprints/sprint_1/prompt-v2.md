# **Implementation Plan — Prompt Creation v2 & Prompt Card Enhancements (Web)**

## 0 · Scope Recap

You already have fully-working **Prompt CRUD** (header + version tables) and a **ManualPromptForm** that stores *title, purpose, models, tools, tags, body*. Next we will:

1. **Enrich Manual Prompt Form** with **Tools, Platform, Purpose-as-Tags** UX.
2. **Persist new lookup values** (models, tools, platforms, tags) automatically.
3. **Display richer Prompt Cards** (tags, version badge) and a **Prompt Detail / Edit modal**.
4. **Add client-side filtering** by Model, Tool, Purpose.

---

## 1 · Backend Changes

| Area                         | Action                                                                                                                                                                                                                                                                                                                                                      |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Schema**                   | ① **Add `platforms`** column (`TEXT[]`) to `prompt_versions` and corresponding Pydantic/ORM models — they currently lack it.<br>② Create three **lookup tables**:<br>`models_lookup(id UUID PK, value TEXT UNIQUE)`<br>`tools_lookup(id, value)`<br>`platforms_lookup(id, value)`.<br>③ Optional: `purposes_lookup` for tag suggestions (low-priority now). |
| **Migrations**               | Alembic revision: `add_platforms_and_lookups`.                                                                                                                                                                                                                                                                                                              |
| **Models (Pydantic + SQLA)** | • Extend `PromptBase`, `PromptCreate`, `PromptVersion` with `platforms: Optional[List[str]]` and make `purpose: Optional[List[str]]` (array) instead of single string.<br>• Add ORM + CRUD helpers for new lookup tables.                                                                                                                                   |
| **Service Layer**            | • **create\_prompt**: upsert new lookup values before write; include `platforms` & tag-array payloads.<br>• **get\_lookups(type)** endpoint to feed dropdowns.<br>• **filter\_prompts(models, tools, purpose\_tags)** query helper (SQL `&&` overlaps operator).                                                                                            |
| **API Routes**               | `POST /api/v1/lookups/{type}` – add value.<br>`GET /api/v1/lookups/{type}` – list.<br>Update `POST /prompts` & `GET /prompts?model=…&tool=…&purpose=…`.                                                                                                                                                                                                     |

---

## 2 · Frontend / UX Changes (Next.js + shadcn/ui + Tailwind)

| Component                       | Work                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ManualPromptForm.tsx**        | • Replace existing `<Select>` with **`@tanstack/react-select` + `CreatableSelect`** in **multi-select** mode for **Models, Tools, Platforms**.<br>• Use `react-hook-form` Controller to manage arrays.<br>• Implement **Purpose Tags** with `@pathofdev/react-tag-input` (or headlessUI Combobox) to allow free typing; each confirmed tag becomes a colored badge.<br>• On `onCreateOption`, call `POST /lookups/{type}` then add to local cache. |
| **PromptCard.tsx**              | • Add `<Badge>` list for tags under title.<br>• Add small **version chip** bottom-left (e.g., `v1`). Use `Tooltip` to indicate “select version (coming soon)”.                                                                                                                                                                                                                                                                                     |
| **PromptDetailModal.tsx** (NEW) | • Opens when a card is clicked (reuse shadcn `<Dialog>`).<br>• Shows read-only form in two-column layout.<br>• **Edit** button toggles fields to editable & **Save** button (MVP overwrites v1).<br>• Keep placeholder **“Save as new version”** toggle (disabled).                                                                                                                                                                                |
| **PromptListFilters.tsx** (NEW) | • Sticky top bar with three multi-select filters that read lookup lists and push query params.<br>• `useDebounce` and `router.push` to refresh list via `/api/prompts?...`.                                                                                                                                                                                                                                                                        |
| **State / Context**             | • Extend `PromptContext` with `lookups` and `filters` slices.<br>• `loadLookups()` on app start; `createPrompt()` dispatch updates lists.                                                                                                                                                                                                                                                                                                          |

---

## 3 · Testing Strategy

| Layer       | Tool         | Tests                                                                                                                             |
| ----------- | ------------ | --------------------------------------------------------------------------------------------------------------------------------- |
| Unit        | Vitest + RTL | • Tag input converts space→badge.<br>• CreatableSelect fires `onCreateOption` & updates form state.                               |
| Integration | RTL          | • create prompt flow writes arrays.<br>• Card click ⇒ Detail modal populated; Edit→Save updates list.                             |
| E2E         | Cypress      | • Filter prompts by Model & Tag and assert reduced card count.<br>• Add new Tool via select → appears in future dropdown options. |

---

## 4 · Documentation & ADRs

* **ADR 004\_lookup\_strategy.md** – why separate tables vs enum.
* **OpenAPI** – regenerate & commit TS types (`openapi-typescript`).
* **README** – local script `pnpm db:migrate && pnpm dev`.
* **Storybook** – add PromptCard variants (with/without tags).

---

## 5 · Observability

* **Sentry breadcrumb** `prompt.create.lookup_miss` when user adds new option.
* **Prometheus** `prompt_lookup_add_total{type="tool"}`.

---

## 6 · Risks & Mitigations

| Risk                         | Impact                 | Mitigation                                                                            |
| ---------------------------- | ---------------------- | ------------------------------------------------------------------------------------- |
| Lookup tables grow unbounded | Dropdown perf degrades | Paginate server-side; cache in SWR; add “archived” flag later.                        |
| Tag UX confusing on mobile   | Form abandonment       | Include helper text + auto-complete suggestions.                                      |
| Editing overwrites history   | Loss of data fidelity  | Display “Save as new version” disabled switch; implement full versioning next sprint. |

---

## 7 · Work Breakdown & Estimates

| Task                              | Owner    | ETA                     |
| --------------------------------- | -------- | ----------------------- |
| DB migration & models             | BE Agent | 0.5 d                   |
| Lookup CRUD routes + tests        | BE Agent | 1 d                     |
| CreatableSelect wrapper component | FE Agent | 0.5 d                   |
| TagInput component                | FE Agent | 0.5 d                   |
| ManualPromptForm refactor         | FE Agent | 1 d                     |
| PromptCard enhancements           | FE Agent | 0.5 d                   |
| PromptDetailModal                 | FE Agent | 1 d                     |
| Filter bar + query wiring         | FE Agent | 0.5 d                   |
| Cypress paths                     | QA Agent | 0.5 d                   |
| Docs & ADR                        | Arch     | 0.25 d                  |
| **Total**                         |          | **6.25 d (\~1 sprint)** |

---

## 8 · Next Sprint Seeds

* **WP-PRM-VSN-003** – true version branching & diff viewer.
* **WP-PRM-AI-004** – enable AI-Automated button & chain to Prompt Engine.
* **SEARCH-005** – full-text & semantic prompt search with pgvector.

With this plan, MeatyPrompts gains **rich metadata, clean UX, and groundwork for upcoming version control** while re-using proven libraries and maintaining a lean code surface.
