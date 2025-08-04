import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Prompt } from '../types/Prompt';

interface PromptCardProps {
  prompt: Prompt;
}

const PromptCard: React.FC<PromptCardProps> = ({ prompt }) => {
  return (
    <View style={styles.card}>
      <Text style={styles.title}>{prompt.title}</Text>
      <Text style={styles.subtitle}>{prompt.model}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    padding: 20,
    marginVertical: 10,
    backgroundColor: '#1E1E1E',
    borderRadius: 10,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  subtitle: {
    fontSize: 14,
    color: '#A9A9A9',
  },
});

export default PromptCard;
