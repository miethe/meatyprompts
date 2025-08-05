import 'react-native-gesture-handler';
import { Slot } from 'expo-router';
import React from 'react';
import { PaperProvider, MD3DarkTheme } from 'react-native-paper';
import { PromptProvider } from './src/state/PromptContext';

export default function App() {
  return (
    <PaperProvider theme={MD3DarkTheme}>
      <PromptProvider>
        <Slot />
      </PromptProvider>
    </PaperProvider>
  );
}
