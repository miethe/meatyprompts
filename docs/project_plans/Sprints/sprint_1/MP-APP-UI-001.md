# User Story MP-APP-UI-001 — **Mobile App Foundation (Sidebar + Dashboard + Prompts + Wizard)**

> **Epic:** **APP** — Mobile Application Core
> **As a** mobile MeatyPrompts user, **I want** a collapsible sidebar with Dashboard and Prompts screens and a “+” button that opens a Prompt Wizard, **so that** I can intuitively browse, create and manage prompts from day one.

---

## 1 · Narrative

*As a* **content-creator on the go**, *I want* an **elegant, dark-themed mobile shell** with core screens (Dashboard, Prompts) and a **Prompt Wizard** launched from a floating action button, *so that* **I immediately understand where to see existing prompts and how to create a new one, while the team can easily extend the app later**.

---

## 2 · Acceptance Criteria

| # | Behaviour / Scenario                                               | Measure / Test (RTL / Detox)                                     |
| - | ------------------------------------------------------------------ | ---------------------------------------------------------------- |
| 1 | Collapsible Drawer renders logo & routes (Dashboard, Prompts)      | Drawer exists; tapping item navigates & highlights active route  |
| 2 | Drawer remains functional in portrait & landscape                  | Responsive snapshot comparison                                   |
| 3 | Dashboard shows placeholder + centered floating “+” (FAB)          | FAB visible; press event opens PromptWizard modal                |
| 4 | Prompts screen lists prompt cards when data present                | Fetch stub returns >0 ⇒ `<PromptCard>` count matches data length |
| 5 | Prompts screen shows empty-state placeholder when no data          | Fetch stub returns \[]; placeholder text rendered                |
| 6 | Prompt Wizard modal includes Model dropdown, Task picker, Next CTA | Form fields render; selection values stored in local state       |
| 7 | Dark theme applied globally; future light mode toggle stubbed      | Snapshot includes expected color tokens                          |
| 8 | Navigation stack passes ESLint/TypeScript checks                   | CI job passes                                                    |

---

## 3 · Context & Dependencies

* **Depends on:**

  * `MP-APP-CHD-000` – Repository bootstrap (Expo/TypeScript, ESLint, Jest)
  * Draft Figma mockups (attached)

* **Forward hooks / future features:**

  * `MP-AUTH-SEC-001` – Auth guard on routes
  * `MP-PRM-API-002` – Real prompt CRUD API integration
  * `MP-APP-UI-003` – Light-mode theme & system toggle
  * `Sprint X` – Analytics instrumentation for navigation events

---

## 4 · Architecture & Implementation Details

## 4.1 Database & Schema (placeholder)

No migration required yet; **stubs only**.
Future table: `prompts (id, title, content, model, created_at, updated_at)`.

## 4.2 API Endpoints (future contract)

| Method | Path              | Purpose       | Status |
| ------ | ----------------- | ------------- | ------ |
| `GET`  | `/api/v1/prompts` | List prompts  | Stub   |
| `POST` | `/api/v1/prompts` | Create prompt | Stub   |

## 4.3 Backend Services & Tasks

*None for this story — UI consumes stubbed mock service.*

## 4.4 Frontend (React Native / Expo)

```
mobile/
 └── src/
     ├── api/           fetchPrompts.ts     ← mocked return []
     ├── components/    DrawerHeader.tsx, PromptCard.tsx, FAB.tsx
     ├── navigation/    AppNavigator.tsx    ← Drawer + Stack (modal)
     ├── screens/       Dashboard.tsx, Prompts.tsx, PromptWizard.tsx
     ├── state/         PromptContext.tsx
     ├── theme/         colors.ts, tailwind.config.js
     └── types/         Prompt.ts
 App.tsx                ← NavigationContainer + providers
```

* **Navigation:**

  * **DrawerNavigator** (`react-navigation/drawer`) → Dashboard, Prompts
  * **StackNavigator** (modal) → PromptWizard

* **Styling / Theming:**

  * **NativeWind** (Tailwind-in-RN) or **React Native Paper**
  * Global dark palette; light palette placeholder in `colors.ts`.

* **State Management:**

  * `PromptContext` (React Context) → `{ prompts: Prompt[] }`
  * Actions: `loadPrompts`, `addPrompt`, `selectPrompt`

* **Key Components:**

  * `FAB.tsx` — floating action button using `react-native-paper`
  * `PromptCard.tsx` — title, subtitle, onPress → (future detail view)

## 4.5 Observability & Logging

* **Tracing:** wrap `loadPrompts()` in `expo-sentry` span (`prompts.load`)
* **Metrics:** *placeholder* counter for prompt list render time
* **Logging:** structured console logs (`@sentry/react-native` breadcrumb)

---

## 5 · Testing Strategy

| Layer           | Tool                                                     | Tests / Assertions                                  |
| --------------- | -------------------------------------------------------- | --------------------------------------------------- |
| **Unit**        | Jest + RTL                                               | Context reducer, PromptCard props                   |
| **Integration** | RTL (Drawer & Stack navigation)                          | Drawer item press → route renders expected screen   |
| **E2E**         | Detox (iOS & Android)                                    | Launch app → open FAB → assert PromptWizard visible |
| **Perf/A11y**   | Expo profile + `@testing-library/jest-native` a11y roles | Color-contrast assertions (WCAG AA)                 |

---

## 6 · Documentation & Artifacts

| File / Location              | Action                               |
| ---------------------------- | ------------------------------------ |
| `docs/adr/001_mobile_nav.md` | NEW – decision to use Drawer + modal |
| `mobile/README.md`           | Setup & run instructions             |
| `docs/api.md`                | Add stub `/prompts` endpoints        |
| `docs/ux/mockups/`           | Snapshot of current Figma frames     |

---

## 7 · Risks & Mitigations

| Risk                            | Impact                            | Mitigation                                |
| ------------------------------- | --------------------------------- | ----------------------------------------- |
| Gesture clashes with Drawer FAB | FAB press triggers drawer gesture | Follow RN best-practice gesture config    |
| Drawer performance on low-end   | Lag on animation                  | Lazy-load screens; keep icon assets small |
| Style drift as features add up  | Inconsistent UI                   | Central Tailwind tokens; style-lint in CI |

---

## 8 · Future Considerations & Placeholders

* **Auth Guard:** protect PromptWizard for signed-in users only.
* **Offline Cache:** cache prompts with MMKV for flight mode usage.
* **Deep Links:** open `/wizard?model=…` from notifications.
* **Web PWA shell:** reuse navigation pattern in React web build.

---

## 9 · Pseudocode & Developer Notes

```ts
// src/state/PromptContext.tsx
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
    fetchPrompts().then(data => dispatch({ type: 'LOAD', payload: data }));
  }, []);

  return (
    <PromptContext.Provider value={{ state, dispatch }}>
      {children}
    </PromptContext.Provider>
  );
};
```

---

This story, when completed, delivers a **production-ready navigation scaffold**—fully tested, themed, and structured—on which all future MeatyPrompts mobile features can confidently iterate.
