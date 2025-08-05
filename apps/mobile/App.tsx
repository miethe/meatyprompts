import 'react-native-reanimated';
import 'react-native-gesture-handler';
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { PromptProvider } from './src/state/PromptContext';
import AppNavigator from './src/navigation/AppNavigator';
import { PaperProvider, MD3DarkTheme } from 'react-native-paper';

export default function App() {
  return (
    <PaperProvider theme={MD3DarkTheme}>
      <PromptProvider>
        <NavigationContainer>
          <AppNavigator />
        </NavigationContainer>
      </PromptProvider>
    </PaperProvider>
  );
}
