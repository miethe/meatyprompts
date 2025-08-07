# User Story MP-PRM-UI-003 — **Enhance PromptDetailModal with Editable CodeMirror Fields and Copy Icon**

> **Epic:** PRM (Prompt Management)
> **As a** Power User, **I want** the Prompt Detail modal to display and let me edit all prompt fields using CodeMirror, and to copy the prompt body with a single click, **so that** I can quickly review, tweak, and reuse prompts without context-switching between components.

---

## 1 · Narrative

*As a* **Power User**, *I want* the Prompt Detail modal to **show every Prompt field** (including Name, Description, Body, Sample Input, Sample Output, Tags, and Access Control), *and* to **edit them inline** using the same CodeMirror-backed form as the ManualPromptForm, *so that* I have a consistent, efficient UI for viewing and updating prompts, and can **copy the prompt body** to my clipboard with one click.

---

## 2 · Acceptance Criteria

| # | Behaviour                                                                                                        | Measure / Test                                                                                                    |
| - | ---------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| 1 | When opening PromptDetailModal (view-only mode), **all fields** render in a slimmed-down ManualPromptForm.       | E2E: Open modal → assert presence of each field label and value; no editable cursors visible                      |
| 2 | Clicking “Edit” transforms view-only fields into editable CodeMirror editors for Body, Sample Input/Output.      | Integration: Modal in edit state → CodeMirror instances mount for those three fields; initial content matches API |
| 3 | Changes made in CodeMirror editors and other inputs are saved on “Save” and reflected in list & backend.         | Unit: mock PUT `/api/prompts/{id}` → assert payload includes updated fields; UI updates card display              |
| 4 | A copy icon appears next to Body in both PromptCard and PromptDetailModal; clicking it copies text to clipboard. | E2E: Click copy icon → verify clipboard contains the exact prompt body; toast notification appears                |
| 5 | Validation errors (e.g. empty Body) display inline and prevent save.                                             | Unit: leave Body empty → click Save → assert error message under CodeMirror and no API call triggered             |

---

## 3 · Context & Dependencies

* **Depends on:**

  * `MP-PRM-API-002` – Ensure PUT `/api/prompts/{id}` supports all fields (Body, Sample Input/Output).
  * `MP-PRM-DB-001` – Database migration adding `sample_input` and `sample_output` columns (if not already present).
* **Forward hooks / future features:**

  * **Sprint 5** – Add version history carousel beneath the modal (attach CodeMirror to each version).
  * **Sprint 6** – Introduce real-time collaborative editing via WebSocket.

---

## 4 · Architecture & Implementation Details

## 4.1 Database & Schema

* **Migration file:** `backend/alembic/versions/20250810_add_sample_io_fields.py`

  ```python
  op.add_column('prompts', sa.Column('sample_input', sa.Text(), nullable=True))
  op.add_column('prompts', sa.Column('sample_output', sa.Text(), nullable=True))
  ```
* **Model update (`core/models.py`):**

  ```python
  class Prompt(Base):
      __tablename__ = 'prompts'
      …
      sample_input = Column(Text, nullable=True)
      sample_output = Column(Text, nullable=True)
  ```

## 4.2 API Endpoints

* **Schema (`api/schemas/prompts.py`):**

  ```python
  class PromptUpdateSchema(BaseModel):
      name: str
      description: Optional[str]
      body: str
      sample_input: Optional[str]
      sample_output: Optional[str]
      tags: List[str]
      access_control: str
  ```
* **Handler (`api/routes/prompts.py`):**

  ```python
  @router.put("/{id}", response_model=PromptResponseSchema)
  async def update_prompt(id: int, payload: PromptUpdateSchema):
      return await prompt_service.update(id, payload.dict())
  ```

## 4.3 Backend Services & Tasks

* **`prompt_service.update()`** must merge updated fields and trigger cache invalidation in Redis.

## 4.4 Frontend (React / Next.js)

* **ManualPromptForm** (`web/src/components/ManualPromptForm/`)

  * Replace `<textarea>` for Body, Sample Input, Sample Output with `<CodeMirrorEditor>` component.
  * Accept `readOnly` prop to render view-only styling (no gutter cursor).
* **PromptDetailModal** (`web/src/components/PromptDetailModal/`)

  * Import `ManualPromptForm`, passing `readOnly: true` initially.
  * Toggle `readOnly=false` on “Edit” click; show Save/Cancel buttons.
  * Place a `<CopyIconButton>` beside the Body editor; onClick → navigator.clipboard.writeText(body).
* **PromptCard** (`web/src/components/PromptCard/`)

  * Add `<CopyIconButton>` next to truncated body preview.
* **Component Library**

  * `<CopyIconButton>` in `web/src/components/common/CopyIconButton.tsx`.

## 4.5 Observability & Logging

* **Tracing:** Add span `PromptDetailModal.render` and `PromptDetailModal.save` with attributes `prompt_id` and `field_count`.
* **Metrics:** Increment Prometheus counter `prompt_ui_edits_total` on successful save.

---

## 5 · Testing Strategy

| Layer           | Tool              | New Tests / Assertions                                                  |
| --------------- | ----------------- | ----------------------------------------------------------------------- |
| **Unit**        | Jest + React TL   | ManualPromptForm renders CodeMirror; CopyIconButton copies correct text |
| **Integration** | React Query Mocks | Modal save triggers PUT with full payload; UI updates on success        |
| **E2E**         | Cypress           | Full flow: view-only → edit → save → verify changes + clipboard copy    |
| **Perf/A11y**   | Lighthouse CI     | Modal loads <200 ms; CodeMirror accessible via keyboard                 |

* **Test cases:**

  1. Modal toggles between read-only and edit states without unmounting.
  2. Copy icon works in both card and modal contexts.
  3. Validation prevents empty body save.

---

## 6 · Documentation & Artifacts

| File / Location                   | Update / Create                                  |
| --------------------------------- | ------------------------------------------------ |
| `docs/ux/prompt-detail-modal.md`  | Annotate new modal states, CodeMirror usage      |
| `docs/guides/ManualPromptForm.md` | Document `readOnly` prop, CodeMirror editor tips |
| `docs/api.md`                     | Update PUT `/api/prompts/{id}` payload schema    |
| Figma (`docs/ux/figma.html`)      | Add view-only vs edit-state screens              |

---

## 7 · Risks & Mitigations

| Risk                                         | Impact | Mitigation                                          |
| -------------------------------------------- | ------ | --------------------------------------------------- |
| CodeMirror integration increases bundle size | Medium | Lazy-load CodeMirror only for relevant routes       |
| Clipboard API unsupported in older browsers  | Low    | Fallback: select+execCommand('copy') on unsupported |
| API schema mismatch leading to data loss     | High   | Contract tests between frontend and backend schemas |

---

## 8 · Future Considerations & Placeholders

* **Real-Time Collaboration:** wire up CodeMirror with Y-js for multi-user edits.
* **Version Diff View:** integrate diff viewer beneath the modal.
* **Offline Drafting:** cache edits locally and sync when online.
