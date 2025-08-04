import React from 'react';
import { FAB as PaperFAB } from 'react-native-paper';
import { StyleSheet } from 'react-native';

const FAB = ({ onPress }) => {
  return (
    <PaperFAB
      style={styles.fab}
      icon="plus"
      onPress={onPress}
    />
  );
};

const styles = StyleSheet.create({
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
  },
});

export default FAB;
