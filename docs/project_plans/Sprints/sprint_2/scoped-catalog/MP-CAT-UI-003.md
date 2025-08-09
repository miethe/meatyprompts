# MP-CAT-UI-003 — **Models Dropdown (Official/Yours) & “Add New” Dialog**

> **Epic:** Catalogs & Metadata
> **As a** user, **I want** a models dropdown that sections “Official” and “Yours,” plus an inline “Add New” flow, **so that** I can quickly pick from the curated list or add a private entry without leaving the form.

---

## 1 · Narrative

*As a* prompt author, *I want* a fast, accessible dropdown with grouped sections and an inline add-new dialog, *so that* setup is frictionless and my custom entries appear instantly under “Yours.”

---

## 2 · Acceptance Criteria

| # | Behaviour                                                                                                 | Measure / Test                                                           |
| - | --------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| 1 | Dropdown fetches `GET /catalog/models?effective=true` and renders grouped sections “Official” and “Yours” | UI test sees both groups; items sorted stable by display\_name           |
| 2 | “Add New” opens modal; validates provider+name+display\_name; POSTs; closes on success                    | New entry appears immediately under “Yours” (optimistic, then confirmed) |
| 3 | Accessibility: keyboard navigation, ARIA roles, focus trap in modal                                       | axe rules pass; keyboard selects + enters items                          |
| 4 | Empty/Loading/Error states are implemented                                                                | Playwright assertions for all states                                     |
| 5 | Conflicts show friendly inline message (from 409)                                                         | Duplicate add → inline error                                             |
| 6 | Client respects ETag/304 from API transparently                                                           | Network asserts 304 on repeat open; no UI jank                           |
| 7 | Component exported reusable as `CatalogDropdown`                                                          | Used by Prompt Create/Edit forms; QA verifies integration                |

---

## 3 · Context & Dependencies

* **Depends on:** MP-CAT-API-002 live.
* **Forward hooks / future:** expose “Workspace” section when scope is enabled; alias UI; deprecation badges.

---

## 4 · Architecture & Implementation Details

## 4.1 Database & Schema

No DB changes; consumes API.&#x20;

## 4.2 API Endpoints

Consumes `GET/POST /catalog/models` from MP-CAT-API-002.&#x20;

## 4.3 Backend Services & Tasks

None (UI-only).

## 4.4 Frontend (Web)

* **Folder:** `web/src/components/catalog/`

  * `CatalogDropdown.tsx` (generic)
  * `AddModelDialog.tsx`
* **Stack:** Next.js + Tailwind; Headless UI/Radix Select; React Query for data.&#x20;
* **Hook (data-fetch):**

  ````ts
  const useModels = () =>
    useQuery(['catalog','models','effective'], () =>
      api.get('/catalog/models', { params:{ effective:true } })
    );
  ``` :contentReference[oaicite:23]{index=23}
  ````
* **UI Outline:**

  * Sections labeled “Official” / “Yours”; subtle lock icon on official.
  * “Add New” CTA at list end → opens dialog (provider, name, display\_name, optional meta JSON).
  * States: loading skeleton, empty states, inline error banners.
  * Integrated into Prompt Create/Edit forms (models multiselect as needed).&#x20;

## 4.5 Observability & Logging

* Spans: `ui.catalog.models.load`, `ui.catalog.models.create`.
* Basic counters via web analytics; error boundaries capture failures.&#x20;

---

## 5 · Testing Strategy

| Layer           | Tool           | New Tests / Assertions                                                             |
| --------------- | -------------- | ---------------------------------------------------------------------------------- |
| **Unit**        | Jest/RTL       | Render sections; selection callback; optimistic add                                |
| **Integration** | RTL + MSW      | 409 conflict path; 500 error path; loading/empty                                   |
| **E2E**         | Playwright     | Open dropdown → select official; add new → appears in “Yours”; keyboard nav & a11y |
| **Perf/A11y**   | Lighthouse/axe | 60 FPS open/close; a11y rules pass                                                 |

Use the standard testing matrix and a11y checks.&#x20;

---

## 6 · Documentation & Artifacts

| File / Location               | Update / Create                        |
| ----------------------------- | -------------------------------------- |
| `docs/ux/catalog_dropdown.md` | Usage, states, a11y notes, screenshots |
| `docs/api.md`                 | Link to used endpoints                 |
| `docs/guides/catalogs.md`     | Add UI integration examples            |

Follow the shared docs table.&#x20;

---

## 7 · Risks & Mitigations

| Risk                           | Impact       | Mitigation                               |   |
| ------------------------------ | ------------ | ---------------------------------------- | - |
| Visual clutter with many items | Hard to scan | Group headers, search/filter in dropdown |   |
| Latency on first load          | Janky UX     | React Query cache, ETag/304              |   |
| A11y regressions               | Exclusion    | RTL + axe in CI                          |   |

---

## 8 · Future Considerations & Placeholders

* Add “Workspace” section when multi-user lands
* Private aliases (`alias_of_id`)
* Deprecation badges & replacement suggestions

---

## 9 · Pseudocode & Developer Notes

```tsx
function AddModelDialog({onCreated}) {
  const m = useMutation((payload) => api.post('/catalog/models', payload), {
    onSuccess: (res) => { queryClient.invalidateQueries(['catalog','models','effective']); onCreated?.(res.data); }
  });
  // form + validation…
}
```
