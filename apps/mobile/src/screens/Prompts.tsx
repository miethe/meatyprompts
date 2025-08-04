import React, { useContext } from 'react';
import { View, Text, FlatList } from 'react-native';
import { PromptContext } from '../state/PromptContext';
import PromptCard from '../components/PromptCard';

const Prompts = () => {
  const { state } = useContext(PromptContext);

  return (
    <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
      {state.prompts.length > 0 ? (
        <FlatList
          data={state.prompts}
          renderItem={({ item }) => <PromptCard prompt={item} />}
          keyExtractor={item => item.id}
        />
      ) : (
        <Text>No prompts yet.</Text>
      )}
    </View>
  );
};

export default Prompts;
