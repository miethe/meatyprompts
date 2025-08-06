# **User Story WP-APP-UI-001 — Web App Foundation (Sidebar + Dashboard + Prompts + Wizard)**

**Epic:** APP — Web Application Core

As a MeatyPrompts web user, I want a collapsible sidebar with Dashboard and Prompts pages and a “+” button that opens a Prompt Wizard, so that I can intuitively browse, create and manage prompts from my browser.

---

**1 · Narrative**

As a content-creator at my desk, I want an elegant, dark-themed web interface with core pages (Dashboard, Prompts) and a Prompt Wizard launched from a primary button, so that I immediately understand where to see existing prompts and how to create a new one, while the team can easily extend the app later.

---

**2 · Acceptance Criteria**

| # | Behaviour / Scenario | Measure / Test (RTL / Cypress) |
| :--- | :--- | :--- |
| 1 | Collapsible Sidebar renders logo & links (Dashboard, Prompts) | Sidebar exists; clicking a link navigates to the correct page & highlights the active link. |
| 2 | Sidebar is responsive and adapts to viewport size | The sidebar collapses to an icon-only view on smaller screens and expands on larger ones; verified via responsive snapshot comparison. |
| 3 | Dashboard shows placeholder + a clearly visible “New Prompt” button | Button is visible; a click event opens the PromptWizard modal. |
| 4 | Prompts page lists prompt cards when data is present | Fetch stub returns >0 ⇒ `<PromptCard>` component count matches the data length. |
| 5 | Prompts page shows an empty-state placeholder when no data exists | Fetch stub returns []; placeholder text is rendered. |
| 6 | Prompt Wizard modal includes Model dropdown, Task picker, and Next CTA | Form fields render; selections are stored in local component state. |
| 7 | Dark theme is applied globally; future light mode toggle is stubbed | Snapshots include expected CSS color variables/tokens. |
| 8 | Routing and component structure passes ESLint/TypeScript checks | The CI pipeline job passes successfully. |

---

**3 · Context & Dependencies**

**Depends on:**
*   `MP-WEB-CHD-000` – Repository bootstrap (Next.js/Vite, TypeScript, ESLint, Vitest)
*   Draft Figma mockups for the web interface (attached)

**Forward hooks / future features:**
*   `MP-AUTH-SEC-001` – Auth guard on routes
*   `MP-PRM-API-002` – Real prompt CRUD API integration
*   `MP-APP-UI-003` – Light-mode theme & system toggle
*   Sprint X – Analytics instrumentation for navigation events

---

**4 · Architecture & Implementation Details**

**4.1 Database & Schema (placeholder)**
No migration required yet; stubs only. Future table: `prompts` (id, title, content, model, created_at, updated_at).

**4.2 API Endpoints (future contract)**
| Method | Path | Purpose | Status |
| :--- | :--- | :--- | :--- |
| GET | `/api/v1/prompts` | List prompts | Stub |
| POST | `/api/v1/prompts` | Create prompt | Stub |

**4.3 Backend Services & Tasks**
None for this story — UI consumes a stubbed mock service.

**4.4 Frontend (React / Next.js)**

```
web/
 └── src/
     ├── app/                 # Or 'pages/'
     │   ├── (main)/
     │   │   ├── dashboard/page.tsx
     │   │   ├── prompts/page.tsx
     │   │   └── layout.tsx     # Root layout with Sidebar
     │   └── layout.tsx         # Root app layout
     ├── lib/api/             # fetchPrompts.ts ← mocked return []
     ├── components/          # Sidebar.tsx, PromptCard.tsx, NewPromptButton.tsx
     ├── components/modals/   # PromptWizard.tsx
     ├── contexts/            # PromptContext.tsx
     ├── styles/              # globals.css, tailwind.config.js
     └── types/               # Prompt.ts
```

*   **Routing:**
    *   Next.js App Router or React Router for page navigation.
    *   The `PromptWizard` will be a client-rendered modal dialog.
*   **Styling / Theming:**
    *   Tailwind CSS using the `class` strategy for dark mode.
    *   A global `colors.ts` or CSS variables file will define the theme palettes.
*   **State Management:**
    *   `PromptContext` (React Context) to manage `{ prompts: Prompt[] }`.
    *   Actions: `loadPrompts`, `addPrompt`, `selectPrompt`.
*   **Key Components:**
    *   `NewPromptButton.tsx` — A primary call-to-action button.
    *   `PromptCard.tsx` — Displays title, subtitle; `onClick` will eventually lead to a detail view.

**4.5 Observability & Logging**
*   **Tracing:** Wrap `loadPrompts()` in a `@sentry/nextjs` span (`prompts.load`).
*   **Metrics:** Placeholder counter for prompt list render time.
*   **Logging:** Use structured console logs that are captured as breadcrumbs by Sentry.

---

**5 · Testing Strategy**

| Layer | Tool | Tests / Assertions |
| :--- | :--- | :--- |
| Unit | Vitest + RTL | Context reducer logic, `PromptCard` props rendering. |
| Integration | RTL | Clicking a sidebar link renders the expected page component. |
| E2E | Cypress | Launch app → click "New Prompt" → assert that the `PromptWizard` modal is visible. |
| Perf/A11y | Lighthouse + jest-axe | Color-contrast assertions meet WCAG AA standards. |

---

**6 · Documentation & Artifacts**

| File / Location | Action |
| :--- | :--- |
| `docs/adr/002_web_nav.md` | **NEW** – Decision to use a responsive sidebar and modal wizard. |
| `web/README.md` | Add setup and run instructions for the web application. |
| `docs/api.md` | Update with stub `/prompts` endpoints if not already present. |
| `docs/ux/mockups/` | Snapshot of current Figma frames for the web UI. |

---

**7 · Risks & Mitigations**

| Risk | Impact | Mitigation |
| :--- | :--- | :--- |
| Cross-browser compatibility | UI appears broken or functions incorrectly on certain browsers (e.g., Safari). | Test on major modern browsers (Chrome, Firefox, Safari); use tools like Autoprefixer for CSS. |
| SEO implications of CSR | Initial pages may not be indexed well if fully client-side rendered. | Use Next.js for its SSR/SSG capabilities to ensure core content is crawlable. |
| Style drift as features are added | The UI becomes inconsistent across different parts of the application. | Enforce the use of central Tailwind tokens and component libraries; add style-linting to the CI pipeline. |

---

**8 · Future Considerations & Placeholders**

*   **Auth Guard:** Protect the `PromptWizard` and `Prompts` page, accessible only to signed-in users.
*   **Offline Cache:** Use IndexedDB and a Service Worker to cache prompts for PWA functionality.
*   **URL-driven State:** Allow linking directly to the wizard with pre-filled data, e.g., `/prompts/new?model=...`.
*   **PWA Enhancements:** Add a web app manifest and full service worker support for "Add to Home Screen" and offline capabilities.

---

**9 · Pseudocode & Developer Notes**

```typescript
// src/contexts/PromptContext.tsx
import { createContext, useReducer, useEffect, FC } from 'react';

// ... (PromptState, PromptAction types)

export const PromptContext = createContext<PromptState | undefined>(undefined);

function promptReducer(state: PromptState, action: PromptAction): PromptState {
  switch (action.type) {
    case 'LOAD':
      return { ...state, prompts: action.payload };
    default:
      return state;
  }
}

export const PromptProvider: FC = ({ children }) => {
  const [state, dispatch] = useReducer(promptReducer, { prompts: [] });

  useEffect(() => {
    // fetchPrompts is a mock/stubbed API call
    fetchPrompts().then(data => dispatch({ type: 'LOAD', payload: data }));
  }, []);

  return (
    <PromptContext.Provider value={{ state, dispatch }}>
      {children}
    </PromptContext.Provider>
  );
};
```

This story, when completed, delivers a production-ready web navigation scaffold—fully tested, themed, and structured—on which all future MeatyPrompts web features can confidently iterate.