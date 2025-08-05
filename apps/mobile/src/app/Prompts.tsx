import React, { useContext } from 'react';
import { View, Text, FlatList } from 'react-native';
import { PromptContext } from '../state/PromptContext';
import PromptCard from '../components/PromptCard';

export default function Prompts() {
  const { state } = useContext(PromptContext) ?? { state: { prompts: [] } };
  return (
    <View>
      <Text>Prompts</Text>
      <FlatList
        data={state.prompts}
        renderItem={({ item }) => <PromptCard prompt={item} />}
        keyExtractor={item => item.id}
      />
    </View>
  );
}
