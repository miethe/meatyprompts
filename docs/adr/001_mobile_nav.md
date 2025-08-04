# ADR 001: Mobile Navigation Strategy

## Status

Accepted

## Context

We need to implement a navigation structure for the MeatyPrompts mobile app that is intuitive, scalable, and aligns with common mobile UI patterns. The initial requirements include a main dashboard, a list of prompts, and a way to create new prompts.

## Decision

We will use a combination of a Drawer Navigator and a Stack Navigator from the `react-navigation` library.

- **Drawer Navigator:** The primary navigation will be a collapsible drawer, providing access to the main screens: "Dashboard" and "Prompts". This is a common and easily discoverable navigation pattern on mobile devices.
- **Stack Navigator:** A stack navigator will be used to handle modal screens, such as the "PromptWizard" for creating new prompts. This allows us to present screens on top of the current context without losing the navigation state of the underlying screen.

## Consequences

### Positive

- **Intuitive User Experience:** This approach provides a familiar and easy-to-use navigation system for mobile users.
- **Scalability:** The drawer and stack navigators can be easily extended to accommodate new screens and features as the app grows.
- **Clear Separation of Concerns:** The navigation logic is centralized in the `AppNavigator.tsx` file, making it easy to manage and maintain.

### Negative

- **Library Dependency:** We will be dependent on the `react-navigation` library. Any breaking changes in the library will require us to update our code.
- **Gesture Conflicts:** There is a potential for gesture conflicts between the drawer and other components, such as the Floating Action Button (FAB). This will require careful configuration and testing.
