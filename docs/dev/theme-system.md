# Theme System

All visual tokens are centralized within `apps/web/src/theme`. Themes export color palettes and sizing tokens which are applied through the `ThemeProvider`. Components consume these values via the `useTheme` hook to ensure consistent styling. To add a new theme, create a file in `theme/themes` and extend the `themes` object in `theme/index.ts`.
