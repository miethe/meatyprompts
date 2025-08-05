import React, { useState } from 'react';
import { View, Text, Button } from 'react-native';

export default function PromptWizard() {
  const [step, setStep] = useState(0);
  return (
    <View>
      <Text>Prompt Wizard - Step {step}</Text>
      <Button title="Next" onPress={() => setStep(step + 1)} />
    </View>
  );
}
