import React from 'react';
import { View, Text } from 'react-native';
import FAB from '../components/FAB';

const Dashboard = ({ navigation }) => {
  return (
    <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
      <Text>Dashboard</Text>
      <FAB onPress={() => navigation.navigate('PromptWizard')} />
    </View>
  );
};

export default Dashboard;
