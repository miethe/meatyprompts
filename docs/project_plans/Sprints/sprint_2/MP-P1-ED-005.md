# User Story MP-P1-ED-005 — **Markdown Editor with Split Preview & Autosave**

> **Epic:** Phase 1 — Manual MVP
> **As a** creator storing prompts, **I want** a markdown editor with split preview, autosave, and keyboard shortcuts **so that** I can draft and refine prompts quickly and confidently without losing work.&#x20;

---

## 1 · Narrative

*As a* power user, *I want* a split-pane editor (markdown input + live preview) with a minimal toolbar, autosave/dirty-state, and shortcuts (⌘S to save, ⌘/ to toggle preview), *so that* editing is fast, reliable, and consistent with the rest of MeatyPrompts’ MVP flows.&#x20;

---

## 2 · Acceptance Criteria

| # | Behaviour                                                                                           | Measure / Test                                                                                     |
| - | --------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| 1 | Editor shows two panes (input + preview) with resizable splitter; preview updates within 250ms.     | RTL test: mount editor, type “**bold**”; assert preview contains `<strong>`; measure render time.  |
| 2 | Toolbar allows: bold, italic, headings, links, code block, ordered/unordered lists, inline code.    | Click toolbar buttons and assert markdown inserted & preview reflects.                             |
| 3 | Autosave: changes persist on page refresh after idle 1.5s (debounced) or blur; dirty badge visible. | E2E: type, wait, reload → GET `/prompts/:id` returns updated body; dirty badge toggles.            |
| 4 | Keyboard shortcuts: ⌘S triggers immediate save; ⌘/ toggles preview; Esc blurs editor.               | Unit: simulate keydown; assert save handler called, preview hidden/shown.                          |
| 5 | Validation errors surface inline (title/body required).                                             | Create/update with empty body ⇒ 400; UI shows inline error from schema.                            |
| 6 | Security: preview sanitizes HTML (no script execution); links/images render safely.                 | Inject `<script>` in body ⇒ preview neutralizes; image/link markdown renders.                      |
| 7 | Telemetry fired: `prompt_edited` on save; include prompt\_id, bytes, elapsed\_ms.                   | Assert event enqueue on save; OTel trace includes attributes.                                      |
| 8 | Performance: typing does not drop below 45 FPS for ≤5k chars; preview diff incremental.             | Perf test in CI with Lighthouse/JS profiler; meets P95 budget.                                     |

---

## 3 · Context & Dependencies

**Depends on:**

* **MP-P1-AUTH-001** (sessions/JWT) to call protected endpoints.&#x20;
* **MP-P1-DB-002** (schema & indexes) to persist prompt bodies.&#x20;
* **MP-P1-API-003** (Prompts CRUD) for `GET/PUT /prompts/:id`.&#x20;

**Forward hooks / future features:**

* Model-aware front-matter & copy variants rely on the same body field/preview (Phase 1).&#x20;
* Phase-2 TipTap/Blocks composer should be able to swap into the editor container via adapter.&#x20;

---

## 4 · Architecture & Implementation Details

## 4.1 Database & Schema

* **No new DB tables** required. Reuse prompt “body” field in the existing `prompt_versions` (or equivalent) store. UI treats it as markdown (`body_md` nomenclature in PRD). &#x20;
* **Note:** PRD vs current code diverge in normalization (`prompts` + `prompt_versions` in code). This story does not change schema; it only reads/writes the `body`. &#x20;

## 4.2 API Endpoints

* Use existing endpoints:

  * `GET /prompts/:id` to hydrate editor initial state.
  * `PUT /prompts/:id` to save edits (autosave + manual save).&#x20;
* Keep payload minimal for this story: `{ title, body }` (+ any fields already in our Pydantic model). Validation for body required per PRD.&#x20;

## 4.3 Backend Services & Tasks

* No new services. Ensure `prompt_service.update_prompt` supports idempotent updates and returns updated entity for optimistic UI. (Routes file already defines PUT.)&#x20;
* Add telemetry hook in the service to emit `prompt_edited` with duration and payload size.&#x20;

## 4.4 Frontend (Next.js / React)

**Current state (evidence):**

* We have `ManualPromptForm` using a `CodeEditor` and `LanguageSelect` for the body and JSON samples. No preview pane exists yet. &#x20;
* `PromptDetailModal` also renders a `CodeEditor` when editing.&#x20;

**Planned additions:**

* **Components (web/src/components/editor/):**

  * `MarkdownEditorPane.tsx` – wraps existing `CodeEditor` with markdown extensions/shortcuts.
  * `MarkdownPreviewPane.tsx` – renders sanitized preview (e.g., `react-markdown` + `rehype-sanitize`).
  * `EditorToolbar.tsx` – buttons for bold/italic/headings/links/lists/code.
  * `SplitView.tsx` – resizable splitter container (keyboard accessible).
* **Integration points:**

  * In `ManualPromptForm` “basic” tab, replace the single `CodeEditor` body block with `SplitView` (`EditorPane` + `PreviewPane`), preserving LanguageSelect for non-markdown modes later.&#x20;
  * Add autosave: `useDebouncedCallback`(1500ms) that calls `PUT /prompts/:id` when editing an existing prompt; for **new prompts** (create flow), persist draft to `localStorage` (key: `draft:prompt:new`) until user submits. PRD only requires “edits persist” — local drafts meet that for create; API autosave for edit.&#x20;
  * Shortcuts: bind ⌘S (preventDefault → call save), ⌘/ (toggle preview), Esc (blur).&#x20;
* **Styling & A11y:** Tailwind + Radix; toolbar buttons have `aria-pressed` state; preview region labeled and focusable. (Consistent with PRD stack).&#x20;

## 4.5 Observability & Logging

* **Tracing:** `editor.render`, `editor.autosave.start/end` with attributes `{prompt_id, body_len, debounce_ms}`.
* **Metrics:** histogram `editor_autosave_latency_ms`, counter `editor_autosave_errors_total`.
* **Logging:** structured JSON on save with sanitized size counts. (Telemetry capture mandated in PRD.)&#x20;

---

## 5 · Testing Strategy

| Layer           | Tool                | New Tests / Assertions                                                                |
| --------------- | ------------------- | ------------------------------------------------------------------------------------- |
| **Unit**        | Jest/RTL            | Toolbar actions mutate text; shortcut handlers; preview sanitization; debounce logic. |
| **Integration** | FastAPI TestClient  | PUT `/prompts/:id` happy/invalid (empty body) paths; ensure response echoes updates.  |
| **E2E**         | Cypress             | Create → edit → autosave → refresh shows persisted body; toggle preview; keyboard.    |
| **Perf/A11y**   | Lighthouse CI / axe | FPS budget on typing; WCAG for toolbar/buttons; focus order & ARIA for split panes.   |

**Test cases:**

1. Draft in create flow is restored from `localStorage` after reload; submitting clears draft.
2. Invalid markdown (unclosed backticks) still saves; preview remains stable (no crashes).
3. Autosave error path shows non-blocking toast and retry/backoff.

---

## 6 · Documentation & Artifacts

| File / Location                   | Update / Create                                           |
| --------------------------------- | --------------------------------------------------------- |
| `docs/adr/003_markdown_editor.md` | TipTap vs CodeMirror decision + preview library choice.   |
| `docs/guides/editor.md`           | User guide: toolbar, shortcuts, autosave, draft recovery. |
| `docs/api.md`                     | Confirm PUT payload example for editor saves.             |
| `docs/telemetry/events.md`        | Define `prompt_edited` schema & sampling.                 |

---

## 7 · Risks & Mitigations

| Risk                                        | Impact               | Mitigation                                                              |
| ------------------------------------------- | -------------------- | ----------------------------------------------------------------------- |
| Preview XSS via raw HTML in markdown        | Security breach      | Use strict sanitize preset; disallow raw HTML by default.               |
| Autosave contention with manual save        | Data races/overwrite | Use last-write wins with `updated_at` check; surface conflict toast.    |
| PRD vs current schema mismatch (normalized) | Rework later         | Keep a thin adapter in service layer; no schema changes in this story.  |

---

## 8 · Future Considerations & Placeholders

* **Blocks/DSL:** Keep editor surface pluggable for future “Prompt Blocks” without replacing the container.&#x20;
* **Model-aware hints:** Non-functional here, but toolbar can house provider-specific snippets later.
* **Real-time collaboration:** Reserve split container for presence cursors; not in MVP.

---

## 9 · Pseudocode & Developer Notes (minimal)

```ts
// useEditorAutosave.ts
const useEditorAutosave = (promptId?: string) => {
  const saveNow = useCallback(async (body: string) => api.put(`/prompts/${promptId}`, { body }), [promptId]);
  const debounced = useDebouncedCallback(saveNow, 1500);

  return {
    onChange: (body: string) => promptId ? debounced(body) : localStorage.setItem('draft:prompt:new', body),
    flush: async (body: string) => promptId ? saveNow(body) : null,
  };
};
```

---

# Notes on Current Code Touchpoints

* **ManualPromptForm** currently renders the body with `CodeEditor` and `LanguageSelect`; we will refactor this area to host the split preview and autosave hooks.&#x20;
* **PromptDetailModal** also uses `CodeEditor` when toggled to edit mode; wire the same split/toolbar into the modal’s edit view for consistency.&#x20;
* **New Prompt flow** is launched from Sidebar → `NewPromptModal` → `ManualPromptForm`; draft persistence activates here. &#x20;

---

## Dev Checklist (DoD)

* [ ] Editor renders split-pane with preview and toolbar.&#x20;
* [ ] Autosave + dirty badge + shortcut handlers implemented and tested. &#x20;
* [ ] PUT/GET integration verified against current prompts API.&#x20;
* [ ] Telemetry events & traces emitted on save.&#x20;
* [ ] Docs updated; ADR merged (editor tech choice).&#x20;

**This completes MP-P1-ED-005 and aligns with Phase-1 MVP scope while staying future-ready for Blocks/Model-aware features.**&#x20;
