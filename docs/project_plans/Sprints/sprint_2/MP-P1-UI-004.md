# User Story MP-P1-UI-004 — **Vault List/Grid + Prompt Cards**

> **Epic:** Phase 1 — Manual MVP
> **As a** signed-in creator, **I want** a responsive vault view with **prompt cards** and a lightweight detail modal, **so that** I can quickly scan, open, and copy my prompts with minimal friction.

---

## 1 · Narrative

*As a* **user**, *I want* a **Prompts** page that shows my prompts as responsive cards (title, first line of body, tags, version badge, quick copy), with basic filters and a detail modal, *so that* I can find and reuse content fast. Cards and the detail modal should reflect the Phase-1 metadata and UX notes, without over-scoping features reserved for later sprints. &#x20;

---

## 2 · Acceptance Criteria

| # | Behaviour                                                                                                  | Measure / Test                                                                                             |
| - | ---------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| 1 | Vault shows a **responsive grid** of Prompt Cards (1/2/3 cols at sm/md/lg).                                | Viewport resize → cards reflow; Lighthouse/RTL snapshot matches breakpoints.                               |
| 2 | Each card shows **title**, **first line of body (truncated)**, **up to 4 tags (+ …)**, **version badge**.  | Render sample prompt → verify truncation and tag capping; version “vX” visible.                            |
| 3 | Each card includes a **quick copy** button that copies the body and toasts success.                        | Click copy → clipboard has body; toast appears. (Copy variants menu is out-of-scope here.)                 |
| 4 | Clicking a card opens a **Prompt Detail Modal** with read-only view and “Edit” toggle using the same form. | Open → detail shows body/tags/link/sample IO; toggle Edit → reuse ManualPromptForm fields.                 |
| 5 | **Filters** drawer lets user filter by **model, tool, purpose**; applying updates the list.                | Select a filter → list updates via API or context; “Clear” resets. (Tag/favorite/archive in later story.)  |
| 6 | **Empty state** appears when no prompts match; provides CTA to “New Prompt.”                               | With empty dataset or no matches → empty state + CTA present.                                              |
| 7 | **Perf**: initial list render **<200 ms p95** at up to 5k prompts (virtualized if needed).                 | Web vitals & perf tests meet budget.                                                                       |
| 8 | **A11y**: keyboard focus, roles, names/labels; meets WCAG 2.1 AA for new UI.                               | Axe checks pass; manual keyboard nav verified.                                                             |

> Scope note: Favorites, Archive badges/filters, Copy variants menu, Collections chips are follow-up stories per PRD timeline.&#x20;

---

## 3 · Context & Dependencies

* **Depends on**

  * **MP-P1-API-003** (Prompts CRUD list/get) for data hydration of cards & modal.&#x20;
  * **MP-P1-DB-002** baseline schema (metadata fields shown on card) already defined in PRD.&#x20;
* **Forward hooks / future features**

  * **Search/Tags/Favorites/Archived** filters & sort in SRCH story (Sprint 2).&#x20;
  * **Copy variants** menu (Sprint 2), **Collections** (Sprint 3).&#x20;

---

## 4 · Architecture & Implementation Details

### 4.1 Frontend Structure

* **Pages & Containers**

  * `web/src/pages/prompts/index.tsx` (PromptsPage): fetch list (API or PromptContext), render grid, attach filters & modal. *(Current scaffold exists: renders grid of `PromptCard`, integrates `PromptListFilters`, opens `PromptDetailModal` on card click—wire to live data and refactor as needed.)*
* **Components**

  * `web/src/components/PromptCard.tsx`: ensure props include `id,title,body,tags[],version`; clamp to 4 tags, truncate preview, include **Copy** button.
  * `web/src/components/PromptDetailModal.tsx`: view-only by default; “Edit” toggles **ManualPromptForm** with Code editor + sample input/output panes; include Copy button near body.
  * `web/src/components/filters/PromptListFilters.tsx`: Sheet with single-select **model/tool/purpose**; on **Apply**, refetch or filter context.
  * `web/src/components/modals/NewPromptModal.tsx`: CTA target for empty state and Sidebar.
  * `web/src/components/layout/Sidebar.tsx`: **New Prompt** button pinned at bottom; no UI change required for this story.
* **State & Data**

  * **Option A (recommended for now):** use **PromptContext** for local cache and filter application; context delegates to API for list & get.
  * **Option B:** use TanStack Query for `/prompts` with queryKey `[prompts, filters]` and infinite/virtualized list; keep context as façade.

### 4.2 API Usage (read-only paths for this story)

* `GET /prompts?model=&tool=&purpose=` — drives the grid.
* `GET /prompts/{id}` — hydrates the detail modal on open.
  (Contracts provided by **MP-P1-API-003**; ensure consistent shape for `title, body, tags, version, link, sample_input/output`.)&#x20;

### 4.3 UI/UX Requirements Mapped to PRD

* **Card content**: title, first line of body, tags, quick copy, version badge (favorite star & model icons deferred).&#x20;
* **Vault**: responsive grid; sort placeholder (default updated\_at desc) visible but disabled until SRCH story lands.&#x20;
* **Empty states**: with CTA and brief “starter templates” pointer (if seeded later).&#x20;

### 4.4 Performance, A11y, Observability

* **Perf**: virtualize grid (e.g., `react-virtualized`/`@tanstack/virtual`) if list > 250 items on screen; lazy-render tags; debounce filter apply.
* **A11y**: button roles on copy; keyboard open/close for modal; focus trap & return.
* **Telemetry hooks** (no blocking): fire `prompt_copied` and `search_performed` events when available in TEL story.&#x20;

---

## 5 · Testing Strategy

| Layer           | Tool                | New Tests / Assertions                                                                                                                            |
| --------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Unit**        | Vitest/Jest + RTL   | PromptCard renders title/preview/tags/version; copy fires clipboard & toast; tag clamp logic.                                                     |
| **Integration** | RTL + MSW           | PromptsPage fetches and renders list; applying filters triggers refetch and updates cards; opening a card fetches detail and shows modal content. |
| **A11y**        | jest-axe/axe-core   | No violations on Cards, Filters sheet, Detail modal; keyboard tab order & focus return verified.                                                  |
| **Perf checks** | Web vitals + custom | p95 initial render < 200 ms with 5k prompts (mocked); verify virtualization threshold.                                                            |

---

## 6 · Documentation & Artifacts

* **Storybook** entries for `PromptCard`, `PromptDetailModal`, `PromptListFilters` with knobs for different densities (few/many tags, long titles).
* **docs/ui/vault.md** — screenshots of grid breakpoints; a11y notes; copy behavior; empty states.
* **Changelog**: “MP-P1-UI-004 — Vault list/grid + cards.”

---

## 7 · Risks & Mitigations

| Risk                                              | Impact              | Mitigation                                                  |
| ------------------------------------------------- | ------------------- | ----------------------------------------------------------- |
| Inconsistent API payloads (missing tags/version)  | Broken card layouts | Align with API-003 response shape; add defensive defaults.  |
| Scope creep (favorites, collections, model icons) | Delays and rework   | Keep within MVP wall; defer to Sprint 2/3 stories.          |
| Render perf on large lists                        | Jank, missed p95    | Virtualize + memoize + windowing; test with 5k items.       |

---

## 8 · Open Questions (TBD)

* **Icons for target models** on the card — do we include in P1 or defer to Sprint 2? (PRD mentions icons on cards.)&#x20;
* **Starter templates** on empty state — do we seed now or later?&#x20;
* **Filter taxonomy** — confirm **model/tool/purpose** values and mapping from lookups vs. tags until Search story lands.&#x20;

---

## 9 · Definition of Done (DoD)

* All ACs met; Storybook updated; a11y & perf checks pass; code reviewed and merged; docs/screenshots attached; light telemetry hooks gated behind feature flags (no-op until TEL story).&#x20;

> **Note on source:** You referenced “impl-plan-p1.md.md”. The available artifact appears as **impl-plan-p1.md**; this story aligns with that and the **Phase1\_prd.md** UX/acceptance sections. If there’s a newer doc variant, share it and I’ll reconcile deltas.&#x20;
