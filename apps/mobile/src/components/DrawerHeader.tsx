import React from 'react';
import { View, Text, Image } from 'react-native';

const DrawerHeader = () => {
  return (
    <View style={{ padding: 20, alignItems: 'center' }}>
      <Image
        source={{ uri: 'https://www.meatyprompts.com/logo.png' }} // Replace with actual logo
        style={{ width: 100, height: 100, marginBottom: 10 }}
      />
      <Text style={{ fontSize: 18, fontWeight: 'bold' }}>MeatyPrompts</Text>
    </View>
  );
};

export default DrawerHeader;
