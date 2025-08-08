# User Story MP-P1-COPY-008 — **Copy Variants (Card & Detail)**

> **Epic:** Phase 1 — Manual MVP
> **As a** prompt user, **I want** to copy a prompt in different formats from the card and the detail modal, **so that** I can quickly reuse it in editors, config files, and programmatic workflows.

---

## 1 · Narrative

*As a* **builder/PM/marketer**, *I want* **a one-click copy and a small menu to choose variants (body only, body + front-matter, JSON)** *so that* **I can paste the right format into my tool without manual reformatting**. The PRD explicitly calls for copy variations and a confirming toast, with telemetry on copy actions【turn22file13†Phase1\_prd.md†L3-L6】【turn22file5†Phase1\_prd.md†L9-L12】.

---

## 2 · Acceptance Criteria

| # | Behaviour                                                                                                                                                                                                    | Measure / Test                                                                                                                                                                                                 |                         |                         |                                                                                                                   |
| - | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- | ----------------------- | ----------------------------------------------------------------------------------------------------------------- |
| 1 | A **quick copy** button is visible on each Prompt Card and in the Prompt Detail modal near the body.                                                                                                         | Card and modal render a clickable control; RTL test asserts presence and enabled state. UI spec per PRD “Card: … quick copy button”【turn22file13†Phase1\_prd.md†L42-L45】.                                      |                         |                         |                                                                                                                   |
| 2 | Clicking quick copy **copies the prompt body** to clipboard and shows a success toast within 200ms.                                                                                                          | Mock `navigator.clipboard.writeText` and assert called with `prompt.body`; assert toast text; Cypress E2E stubs clipboard. PRD AC: “One-click copy (body); toast confirms”【turn22file2†Phase1\_prd.md†L8-L12】. |                         |                         |                                                                                                                   |
| 3 | A **chevron/menu** next to the copy button exposes **Copy body**, **Copy body + front-matter**, **Copy JSON**.                                                                                               | RTL: open menu and assert three options. PRD “Copy menu … variants”【turn22file13†Phase1\_prd.md†L45-L46】.                                                                                                      |                         |                         |                                                                                                                   |
| 4 | **Front-matter** format: valid YAML between `---` fences, includes: `title`, `tags`, `target_models`, `providers`, `link`, `version`, `updated_at`, `access_control`; then a blank line, then body.          | Unit tests validate YAML serialization shape against Prompt fields (from API model)【turn21file2†prompt.py†L54-L62】【turn21file12†prompt\_service.py†L96-L102】.                                                  |                         |                         |                                                                                                                   |
| 5 | **JSON** format: a stable, programmatic shape mirroring the `Prompt` API response (id, prompt\_id, version, title, body, tags, use\_cases, target\_models, providers, link, created\_at, updated\_at, etc.). | Unit test serializes a Prompt fixture to JSON and deep-equals expected keys; aligns to current model【turn21file2†prompt.py†L54-L62】.                                                                           |                         |                         |                                                                                                                   |
| 6 | Copy actions **emit telemetry** `prompt_copied` with attributes: `prompt_id`, `variant` (\`body                                                                                                              | front\_matter                                                                                                                                                                                                  | json`), `source` (`card | detail`), `timestamp\`. | Mock analytics client; assert event payload. Telemetry event required by PRD【turn21file7†Phase1\_prd.md†L10-L12】. |
| 7 | **Graceful fallback** when clipboard API unavailable: select-all + `document.execCommand('copy')` path; toast still shows.                                                                                   | Jest/RTL simulate unsupported clipboard; assert fallback branch executed.                                                                                                                                      |                         |                         |                                                                                                                   |
| 8 | **A11y**: Buttons have `aria-label` and focus ring; menu items keyboard navigable.                                                                                                                           | axe check passes; keyboard tests for arrow/enter activation.                                                                                                                                                   |                         |                         |                                                                                                                   |

---

## 3 · Context & Dependencies

* **Depends on:**

  * MP-P1-UI-001/002 (Prompt list & card scaffold) — copy controls attach to existing card layout【turn22file13†Phase1\_prd.md†L42-L45】.
  * MP-P1-UI-003 (Prompt Detail Modal / Editor) — copy controls appear beside body editor/preview【turn22file4†PromptDetailModal.tsx†L18-L23】【turn22file12†PromptDetailModal.tsx†L73-L93】.
  * MP-P1-API-001/002 (Prompt model exposed via API) — ensures the JSON variant shape matches existing `Prompt` schema【turn21file4†prompts.py†L18-L26】【turn21file2†prompt.py†L54-L62】.

* **Forward hooks / future features:**

  * **Export** story: library export should reuse the same JSON serializer to avoid drift【turn21file1†Phase1\_prd.md†L16-L20】.
  * **Share link (flag)**: toast may offer “Create share link” CTA later; tracked but not implemented now【turn21file1†Phase1\_prd.md†L21-L24】.
  * **Blocks / embedding fields** reserved — include placeholders in YAML comments, but do not output data yet【turn22file7†Phase1\_prd.md†L1-L7】.

---

## 4 · Architecture & Implementation Details

## 4.1 Frontend (React)

* **Components**

  * `components/common/CopyMenu.tsx` (new): dropdown with three actions; accepts `prompt: Prompt` and `source: 'card'|'detail'`. Uses Radix Dropdown or shadcn menu.
  * **Integrations**

    * **Prompt Card**: add Copy button + chevron. Quick copy triggers `variant='body'`.
      (Card layout already includes CopyIconButton in modal example; mirror on card)【turn22file12†PromptDetailModal.tsx†L92-L93】.
    * **Prompt Detail Modal**: replace the inline `CopyIconButton` with `CopyMenu` next to language select; preserve quick-copy default【turn22file12†PromptDetailModal.tsx†L73-L93】.

* **Utilities**

  * `lib/clipboard.ts` (new): `copyText(text: string): Promise<void>` with `navigator.clipboard` primary and `execCommand` fallback.
  * `lib/formatters/promptCopy.ts` (new):

    * `toFrontMatter(prompt: Prompt): string`
    * `toJson(prompt: Prompt): string`
    * `toBody(prompt: Prompt): string`
  * **Formatting rules:**

    * **YAML front-matter** (fields from PRD & model):
      `title, tags, target_models, providers, link, access_control, version, updated_at`【turn21file2†prompt.py†L54-L62】【turn22file13†Phase1\_prd.md†L1-L6】.
      Output:

      ```
      ---\n
      title: "<title>"\n
      tags: [tag1, tag2]\n
      target_models: [gpt-4o, ...]\n
      providers: [openai, ...]\n
      link: "<url-or-empty>"\n
      access_control: "private|unlisted"\n
      version: "<string-version>"\n
      updated_at: "<ISO8601>"\n
      ---\n\n
      <body>
      ```
    * **JSON**: mirror `Prompt` response from API (`id`, `prompt_id`, `version`, `title`, `body`, `use_cases`, `access_control`, arrays, `link`, timestamps, `tags`)【turn21file2†prompt.py†L54-L62】. Keep snake\_case to match backend.

* **Telemetry**

  * `lib/analytics.ts`: `track('prompt_copied', { prompt_id, variant, source })`. Required by PRD core events【turn22file7†Phase1\_prd.md†L33-L41】.

* **Toasts**

  * Use existing toast system (shadcn `useToast` or equivalent): “Copied {variantLabel}”.

* **A11y/i18n**

  * `aria-label`s for buttons, menu items; strings routed through `i18n` keys (`copy.body`, `copy.frontMatter`, `copy.json`, `toast.copied`).

## 4.2 API / Backend

* **No new endpoints** needed; copy occurs client-side.
* **Contract source of truth** for JSON is the **existing `Prompt` schema**; ensure FE formatter consumes same shape as the FastAPI GET/PUT responses【turn21file4†prompts.py†L18-L26】【turn21file12†prompt\_service.py†L76-L84】【turn21file0†prompt\_service.py†L18-L27】.

## 4.3 Data / Schema

* **No DB changes**. Uses existing fields that are already present in `Prompt` ORM/Pydantic model (title, body, tags, target\_models, providers, access\_control, link, version, timestamps)【turn21file2†prompt.py†L54-L62】【turn21file8†prompt.py†L45-L66】.

## 4.4 Observability & Logging

* **Tracing**: span `copy_variant.start` → `copy_variant.success|error` with attributes `{prompt_id, variant, source}`.
* **Metrics**: FE counter per variant; backend unaffected. Aligns with PRD telemetry requirements【turn21file13†Phase1\_prd.md†L33-L41】.
* **Logging**: Debug log in dev when fallback path used.

---

## 5 · Testing Strategy

| Layer         | Tool                  | New Tests / Assertions                                                                                                                 |
| ------------- | --------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| **Unit (FE)** | Jest                  | `toFrontMatter()` produces valid YAML with required keys; `toJson()` deep-equals shape; `copyText()` handles primary & fallback paths. |
| **Component** | React Testing Library | Card renders quick copy + menu; clicking options calls formatter and clipboard; toast appears with correct label.                      |
| **E2E**       | Cypress               | From Vault grid: open menu → copy each variant → paste into a sandbox textarea and assert exact text. Modal path mirrors card.         |
| **Perf/A11y** | Lighthouse/axe        | No regressions; menu navigable by keyboard; buttons have labels.                                                                       |
| **Contract**  | Schema snapshot       | JSON variant schema snapshot matches `Prompt` API return (keys and casing)【turn21file2†prompt.py†L54-L62】.                             |

(Testing categories and best practices per template【turn22file3†user\_stories.md†L50-L58】.)

---

## 6 · Documentation & Artifacts

| File / Location                | Update / Create                                                                                        |
| ------------------------------ | ------------------------------------------------------------------------------------------------------ |
| `docs/guides/copy_variants.md` | New — screenshots, examples of each format, and tips.                                                  |
| `docs/api.md`                  | Note: JSON copy mirrors `GET /prompts` response; no new endpoints【turn21file5†Phase1\_prd.md†L63-L71】. |
| `docs/adr/0xx_copy_formats.md` | ADR — choose YAML front-matter + JSON contract from existing model as canonical.                       |
| `docs/ux/figma.md`             | Link to copy menu design and toast spec.                                                               |

(Documentation table pattern per template【turn22file8†user\_stories.md†L11-L17】.)

---

## 7 · Risks & Mitigations

| Risk                      | Impact                      | Mitigation                                                                              |
| ------------------------- | --------------------------- | --------------------------------------------------------------------------------------- |
| JSON drift from API model | Downstream tools break      | Treat `Prompt` Pydantic as source; add schema snapshot test.                            |
| Clipboard API blocked     | Users can’t copy            | Fallback to `execCommand` + selection; show error toast if both fail.                   |
| YAML parsing issues       | Front-matter consumers fail | Keep flat keys, avoid complex nested structures in P1; unit test YAML parse round-trip. |

---

## 8 · Future Considerations & Placeholders

* Extend **front-matter** with `input_schema`, `llm_parameters`, `sample_input/output` when we stabilize those UIs (already in model, but keep P1 YAML minimal)【turn22file3†ManualPromptForm.tsx†L51-L58】【turn21file2†prompt.py†L39-L44】.
* Add **“Copy as Markdown code block”** variant if requested.
* When **Share (flag)** is enabled, provide toast CTA “Create unlisted link” (does nothing in P1)【turn21file1†Phase1\_prd.md†L21-L24】.

---

## 9 · Developer Notes

* **Where to hook in UI today:**

  * `PromptDetailModal.tsx` — replace existing `CopyIconButton` with `CopyMenu` near the language select and body area【turn22file12†PromptDetailModal.tsx†L79-L93】.
  * Prompt Card component — add same `CopyMenu`. (Follow modal pattern.)
* **JSON contract:** use exactly the `Prompt` response fields from our FastAPI routes to keep parity【turn21file4†prompts.py†L18-L26】【turn21file12†prompt\_service.py†L76-L84】.
* **i18n keys:** `copy.quick`, `copy.menu.title`, `copy.body`, `copy.frontMatter`, `copy.json`, `toast.copied`.

---

**Definition of Done**

* All ACs pass with unit/component/E2E coverage.
* Analytics event `prompt_copied` visible in dev console/mock and wired to prod sink later (P1 stores client-side only if no backend).
* Docs merged (guide + ADR), screenshots added.
* a11y and Lighthouse checks clean; no TypeScript errors; CI green.

**References**: PRD sections for Copy variants, acceptance criteria, telemetry, and UX notes【turn22file13†Phase1\_prd.md†L3-L6】【turn22file2†Phase1\_prd.md†L8-L12】【turn21file7†Phase1\_prd.md†L10-L12】; Implementation Plan AC-3 and UX outputs【turn22file6†impl-plan-p1.md†L12-L21】【turn22file6†impl-plan-p1.md†L27-L35】; Existing Prompt model and API routes used to define JSON shape【turn21file2†prompt.py†L54-L62】【turn21file4†prompts.py†L18-L26】.
