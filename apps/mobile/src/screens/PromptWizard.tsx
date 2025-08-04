import React, { useState } from 'react';
import { View, Text, Button } from 'react-native';

const PromptWizard = ({ navigation }) => {
  const [model, setModel] = useState(null);
  const [task, setTask] = useState(null);

  return (
    <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
      <Text>Prompt Wizard</Text>
      {/* Implement dropdowns and task picker here */}
      <Button title="Next" onPress={() => { /* Handle next step */ }} />
      <Button title="Close" onPress={() => navigation.goBack()} />
    </View>
  );
};

export default PromptWizard;
