import React from 'react';
import { createDrawerNavigator } from '@react-navigation/drawer';
import { NavigationContainer } from '@react-navigation/native';
import { PromptProvider } from '../src/state/PromptContext';
import Dashboard from './Dashboard';
import Prompts from './Prompts';
import PromptWizard from './PromptWizard';

const Drawer = createDrawerNavigator();

export default function Layout() {
  return (
    <PromptProvider>
      <NavigationContainer>
        <Drawer.Navigator initialRouteName="Dashboard">
          <Drawer.Screen name="Dashboard" component={Dashboard} />
          <Drawer.Screen name="Prompts" component={Prompts} />
          <Drawer.Screen name="PromptWizard" component={PromptWizard} />
        </Drawer.Navigator>
      </NavigationContainer>
    </PromptProvider>
  );
}
