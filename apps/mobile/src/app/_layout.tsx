import { Drawer } from 'expo-router';
import React from 'react';
import { PromptProvider } from '../state/PromptContext';

export default function Layout() {
  return (
    <PromptProvider>
      <Drawer>
        {/* Drawer screens will be auto-included from src/app/*.tsx */}
      </Drawer>
    </PromptProvider>
  );
}
