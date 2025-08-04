import 'react-native-gesture-handler';
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { PromptProvider } from './src/state/PromptContext';
import AppNavigator from './src/navigation/AppNavigator';
import { PaperProvider } from 'react-native-paper';
import { darkTheme } from './src/theme/colors';
import './src/global.css';

export default function App() {
  return (
    <PaperProvider theme={darkTheme}>
      <PromptProvider>
        <NavigationContainer>
          <AppNavigator />
        </NavigationContainer>
      </PromptProvider>
    </PaperProvider>
  );
}
