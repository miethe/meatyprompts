# **User Story WP-PRM-UI-002 — Prompt Creation (Manual + AI-Automated Scaffolding)**

**Epic:** Prompt Vault — Core CRUD & Versioning

---

## 1 · Narrative

As a **MeatyPrompts** web user, I want a “New Prompt” modal that lets me pick between **Manual** or **AI Automated** creation. While AI-Automated is *coming soon*, Manual creation should already let me fill in every attribute (title, purpose, model, tools, etc.) and paste the full prompt text, so I can start curating my personal vault right away and see the entry appear in the Prompts list.

---

## 2 · Acceptance Criteria

(The table format re-uses the pattern established in WP-APP-UI-001.)

| #  | Behaviour / Scenario                                                                                                                                                                    | Measure / Test (RTL / Cypress)                                                                                    |
| :- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| 1  | Clicking **“New Prompt”** opens a modal with two buttons (“Manual”, “AI Automated”).                                                                                                    | Modal renders; “AI Automated” button has `aria-disabled="true"`.                                                  |
| 2  | Selecting **Manual** loads a multi-step form (or single scroll form on ≥768 px) with validated inputs: Title, Purpose, Model(s), Tool(s), Tags, Visibility, **Prompt Text** (textarea). | Each field is required unless marked optional; invalid form blocks Submit; unit tests cover Yup/Zod schema.       |
| 3  | Each dropdown includes an **“Other…”** option that reveals a free-text input.                                                                                                           | Selecting “Other…” toggles additional input; a11y tested via jest-axe.                                            |
| 4  | Clicking **Cancel** closes the modal with no side-effects.                                                                                                                              | Cypress: open → cancel → no new network requests; context state unchanged.                                        |
| 5  | Clicking **Submit** sends a `POST /api/v1/prompts` request; on success the modal closes and the new prompt card appears at the top of **Prompts** page.                                 | Network interception asserts 201 status; UI re-renders with new item.                                             |
| 6  | The system auto-assigns **version 1**; subsequent edits will increment version (future story hook).                                                                                     | Response payload contains `"version":1`; DB row created in `prompt_versions` table (verified via mocked service). |
| 7  | CI passes ESLint/TS, Vitest, and Cypress suites.                                                                                                                                        | GitHub Action green build.                                                                                        |

---

## 3 · Context & Dependencies

**Depends on**

* WP-APP-UI-001 — Web foundation: sidebar, dashboard, prompt list modal trigger.
* MP-WEB-CHD-000 — Repo scaffold with Next.js, Tailwind, Vitest.

**Forward hooks / future work**

* `WP-PRM-API-003` — Full Prompt Versioning & Diff view.
* `WP-PRM-AI-004` — Enable AI-Automated button & backend service.
* `MP-AUTH-SEC-001` — Route & mutation protection.

---

## 4 · Architecture & Implementation Details

### 4.1 Database & Schema

Add **two** tables (SQL DDL draft):

```sql
-- existing prompts meta
CREATE TABLE prompts (
  id                UUID PRIMARY KEY,
  slug              TEXT UNIQUE,
  latest_version_id UUID REFERENCES prompt_versions(id),
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  created_by        UUID REFERENCES users(id)
);

-- immutable versions
CREATE TABLE prompt_versions (
  id          UUID PRIMARY KEY,
  prompt_id   UUID REFERENCES prompts(id) ON DELETE CASCADE,
  version     INT  NOT NULL,
  title       TEXT NOT NULL,
  purpose     TEXT,
  models      TEXT[] NOT NULL,
  tools       TEXT[] NULL,
  tags        TEXT[] NULL,
  body        TEXT NOT NULL,
  visibility  TEXT DEFAULT 'private',
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX ON prompt_versions(prompt_id, version);
```

> **Why two tables?** Clean audit history and branching support later on. The placeholder `prompts` table from WP-APP-UI-001 is now split into a header + versions.

### 4.2 API Endpoints (v1)

| Method   | Path                           | Purpose                        |
| -------- | ------------------------------ | ------------------------------ |
| **POST** | `/api/v1/prompts`              | Create prompt (version 1)      |
| GET      | `/api/v1/prompts`              | List prompts (latest versions) |
| GET      | `/api/v1/prompts/:id`          | Fetch latest details           |
| GET      | `/api/v1/prompts/:id/versions` | List all versions (scaffold)   |

*FastAPI* models leverage **Pydantic**; service layer publishes `prompt.created` event to Redis Pub/Sub for telemetry.

### 4.3 Services & Modules

`template_version_service` is introduced next to existing Prompt Engine modules to encapsulate CRUD & diff ops — aligning with the planned **Template & Version Service** module.

### 4.4 Frontend (Next.js / App Router)

```
web/src/
 ├─ components/
 │   ├─ buttons/NewPromptButton.tsx
 │   ├─ modals/NewPromptModal.tsx       # parent modal shell
 │   └─ forms/ManualPromptForm.tsx      # extracted for testing
 ├─ lib/api/createPrompt.ts             # typed fetch wrapper
 ├─ contexts/PromptContext.tsx          # add createPrompt action
 └─ types/Prompt.ts (extend with version, visibility)
```

* **State Management:** extend existing `PromptContext` with `createPrompt()` reducer branch.
* **UI Library:** continue using shadcn/ui `Dialog`, `Select`, `Textarea` for rapid dev.
* **Form lib:** React-Hook-Form + Zod schema for declarative validation.

### 4.5 Observability & Logging

* Add Sentry span `prompts.create`.
* Increment Prometheus counter `prompts_created_total{method="manual"}`.

---

## 5 · Testing Strategy

| Layer       | Tool                            | Tests                                                     |
| ----------- | ------------------------------- | --------------------------------------------------------- |
| Unit        | Vitest + @testing-library/react | Form validation, context reducer, disabled AI button.     |
| Integration | RTL                             | Submit flow mocks fetch; prompt list updates.             |
| E2E         | Cypress                         | user → “New Prompt” → Manual → fill → Submit → sees card. |
| Perf/A11y   | Lighthouse, jest-axe            | Modal contrast & focus trap compliance.                   |

---

## 6 · Documentation & Artifacts

| File                                | Action                                             |
| ----------------------------------- | -------------------------------------------------- |
| `docs/adr/003_prompt_versioning.md` | **NEW** – rationale for dual-table version scheme. |
| `docs/api/prompts.md`               | Expand with new endpoints & examples.              |
| `web/README.md`                     | Add “Prompt Creation” local dev instructions.      |
| Figma                               | Flow for Manual creation + greyed AI button.       |

---

## 7 · Risks & Mitigations

| Risk                   | Impact                   | Mitigation                                                |
| ---------------------- | ------------------------ | --------------------------------------------------------- |
| Form bloat / poor UX   | Users abandon creation   | Use multi-step wizard after 6+ fields; collect telemetry. |
| Version table growth   | DB storage & query perf  | Partition by prompt\_id; prune old minors in future.      |
| API schema drift vs FE | Compile-time types break | Share OpenAPI-generated TS types via `openapi-ts`.        |

---

## 8 · Future Considerations & Placeholders

* **AI Automated Creation:** disable button now, but include feature flag & route guard.
* **Branching / Diff UI:** show side-by-side version compare.
* **Import from GitHub:** attach commit hash to `prompt_versions`.
* **Public/Team visibility:** extend `visibility` enum; hook into RBAC.

---

## 9 · Pseudocode & Developer Notes

```typescript
// lib/api/createPrompt.ts
export async function createPrompt(data: ManualPromptInput) {
  const res = await fetch('/api/v1/prompts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Prompt creation failed');
  return (await res.json()) as Prompt;
}
```

> The story delivers an end-to-end Manual prompt creation flow, establishes the **versioning backbone**, and lays stubs for the upcoming AI-Automated path — keeping the product aligned with the broader Prompt Vault vision.
