# User Story MP-PRM-UI-005 — **Sidebar “New Prompt” Button Relocation & Centralized Theme Styling**

> **Epic:** PRM (Prompt Management) – UI/UX Enhancements
> **As a** User, **I want** the “New Prompt” button moved to the bottom of the sidebar with attractive, modern styling and a central location for theme styling, **so that** I can easily find the button while benefiting from consistent visual design across dynamic themes.

---

## 1 · Narrative

*As a* **User**,
*I want* the "New Prompt" button positioned at the bottom of the sidebar, centered, with a rounded "+" icon and descriptive text below it, styled attractively according to the current theme,
*so that* it is easily discoverable, aesthetically pleasing, and always consistent with the rest of the application regardless of whether I am using Light Mode, Dark Mode, High Contrast, or other future themes.

---

## 2 · Acceptance Criteria

| # | Behaviour                                                                                                             | Measure / Test                                                                                     |
| - | --------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| 1 | “New Prompt” button is **removed** from its current position and **added** to the bottom of the sidebar, centered.    | UI snapshot test: Button appears in the correct position in the DOM & visually centered in layout. |
| 2 | Button displays a **rounded** background with a "+" icon and text **below** the icon (“New Prompt”).                  | Cypress visual regression & DOM assertions on icon, label, and rounded border radius.              |
| 3 | Button styling (colors, hover states, typography) **changes dynamically** based on active theme.                      | Switch theme → assert button colors match theme palette from central theme config.                 |
| 4 | All global styles (colors, fonts, spacing, border radii, shadows) are **managed from a central theme configuration**. | Theme config file updates → assert changes propagate across button and other UI elements.          |
| 5 | Button click behavior remains unchanged — navigates to “Create Prompt” flow.                                          | E2E: Click → route changes to `/prompts/new` and loads ManualPromptForm.                           |

---

## 3 · Context & Dependencies

* **Depends on:**

  * `MP-THEME-001` — Establish central theme configuration for Tailwind/Nativewind.
  * Existing “Create Prompt” route and form (`/prompts/new`) already implemented.
* **Forward hooks / future features:**

  * **Sprint +2** — Theme switching UI toggle in user settings.
  * **Sprint +3** — Custom user-defined themes persisted in DB.

---

## 4 · Architecture & Implementation Details

## 4.1 Theme Architecture

We already use **Tailwind/Nativewind** via `className` bindings.
The goal is to **abstract colors, spacing, typography, and iconography** into a **central theme object** so we can dynamically swap themes.

**Directory Structure Proposal:**

```
/src/theme/
  index.ts              // central theme export
  themes/
    light.ts
    dark.ts
    highContrast.ts
  tailwind.config.js    // reads from theme tokens
```

Example `theme/index.ts`:

```ts
import light from './themes/light';
import dark from './themes/dark';
import highContrast from './themes/highContrast';

export const themes = { light, dark, highContrast };
export type ThemeName = keyof typeof themes;

// Default theme
export let currentTheme: ThemeName = 'light';

// Function to change theme
export const setTheme = (theme: ThemeName) => {
  currentTheme = theme;
};
```

Example `themes/light.ts`:

```ts
export default {
  colors: {
    primary: '#3B82F6', // Tailwind blue-500
    primaryHover: '#2563EB',
    background: '#FFFFFF',
    text: '#111827',
  },
  borderRadius: '9999px', // Fully rounded
};
```

**Tailwind Config (`tailwind.config.js`):**

* Extend colors dynamically from `theme/index.ts` for build-time mapping.
* Use `data-theme` attribute on `<html>` or `<body>` to swap classes at runtime.

---

## 4.2 UI / Component Updates

**File:** `src/components/Sidebar.tsx`

* Remove current “New Prompt” button placement.
* Add a flex container at the bottom (`flex-col justify-end items-center`).
* Place a `<ThemedButton>` component for "New Prompt" in that container.

**File:** `src/components/common/ThemedButton.tsx`

* Accept `theme` prop or consume from ThemeContext.
* Apply Tailwind classes from theme tokens:

```tsx
<button
  className={`
    flex flex-col items-center justify-center
    bg-[${theme.colors.primary}]
    hover:bg-[${theme.colors.primaryHover}]
    text-[${theme.colors.text}]
    rounded-full
    p-4 shadow-md
    transition-all
  `}
  onClick={onClick}
>
  <PlusIcon size={24} />
  <span className="mt-1 text-sm font-medium">New Prompt</span>
</button>
```

---

## 4.3 Navigation

* Keep current route for new prompt creation: `router.push('/prompts/new')`.

---

## 4.4 Project Structure Impact

* New `/src/theme` directory for centralized theme handling.
* Update all shared UI components to read colors/spacings from the theme object rather than hard-coded Tailwind classes.

---

## 5 · Testing Strategy

| Layer           | Tool          | New Tests / Assertions                                              |
| --------------- | ------------- | ------------------------------------------------------------------- |
| **Unit**        | Jest + RTL    | ThemedButton applies correct colors and typography for each theme.  |
| **Integration** | Cypress       | Button click navigates to `/prompts/new`.                           |
| **E2E**         | Cypress       | Change theme → verify button updates visually & via DOM attributes. |
| **Visual**      | Percy / Happo | Sidebar renders correctly with relocated button in all themes.      |

---

## 6 · Documentation & Artifacts

| File / Location               | Update / Create                                                   |
| ----------------------------- | ----------------------------------------------------------------- |
| `docs/ux/sidebar-layout.md`   | New placement and styling screenshots for “New Prompt” button.    |
| `docs/dev/theme-system.md`    | How to add/edit themes and apply theme tokens in components.      |
| Figma (`/docs/ux/figma.html`) | Update sidebar mockups for light, dark, and high contrast themes. |

---

## 7 · Risks & Mitigations

| Risk                                                 | Impact | Mitigation                                                   |
| ---------------------------------------------------- | ------ | ------------------------------------------------------------ |
| Theme tokens not matching Tailwind build-time colors | Medium | Use Tailwind config extension & `data-theme` runtime mapping |
| Overflow in smaller sidebar widths                   | Low    | Use responsive flex & ensure min-width on button container   |

---

## 8 · Future Considerations & Placeholders

* **Theme Switcher in Settings:** User can toggle between light/dark/high contrast directly in the UI.
* **Custom Theme Creation:** Persisted per-user in backend.
* **Themed Animations:** Transition colors smoothly when switching themes.

---

If you want, I can **also provide the Figma-ready design spec** so the AI agent has exact pixel sizes, spacing, and hover effects for the “New Prompt” button in all themes. That way, they have both the **architectural plan** and the **visual design** in one package.
