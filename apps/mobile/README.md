# MeatyPrompts Mobile App

This is the mobile application for MeatyPrompts, built with React Native and Expo.

## Setup

1. **Install Dependencies:**
   ```bash
   npm install
   ```

2. **Run the app:**
   ```bash
   npm start
   ```

## Project Structure

- **`src/api`**: Contains the API client and mock functions for fetching data.
- **`src/components`**: Contains reusable components used throughout the app.
- **`src/navigation`**: Contains the navigation setup, including the drawer and stack navigators.
- **`src/screens`**: Contains the main screens of the app.
- **`src/state`**: Contains the state management logic, including the `PromptContext`.
- **`src/theme`**: Contains the color palettes and theming configuration.
- **`src/types`**: Contains the TypeScript type definitions.

## How it Works

The app is built around a central `PromptProvider` that manages the state of the prompts. The `AppNavigator` sets up the navigation structure, with a drawer for the main screens and a stack for modal screens. The screens then consume the data from the `PromptContext` and display it to the user.

## Making Updates

- **Adding a new screen:** Create a new component in the `src/screens` directory and add it to the `AppNavigator`.
- **Adding a new component:** Create a new component in the `src/components` directory and import it where needed.
- **Updating the theme:** Modify the color palettes in `src/theme/colors.ts`.
- **Updating the API:** Modify the API client in `src/api/fetchPrompts.ts`.
