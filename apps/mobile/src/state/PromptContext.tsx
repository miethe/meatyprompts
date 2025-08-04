import React, { createContext, useReducer, useEffect, FC } from 'react';
import { Prompt } from '../types/Prompt';
import { fetchPrompts } from '../api/fetchPrompts';

interface PromptState {
  prompts: Prompt[];
}

type PromptAction = { type: 'LOAD'; payload: Prompt[] };

export const PromptContext = createContext<{
  state: PromptState;
  dispatch: React.Dispatch<PromptAction>;
} | undefined>(undefined);

const promptReducer = (state: PromptState, action: PromptAction): PromptState => {
  switch (action.type) {
    case 'LOAD':
      return { ...state, prompts: action.payload };
    default:
      return state;
  }
};

export const PromptProvider: FC = ({ children }) => {
  const [state, dispatch] = useReducer(promptReducer, { prompts: [] });

  useEffect(() => {
    fetchPrompts().then(data => dispatch({ type: 'LOAD', payload: data }));
  }, []);

  return (
    <PromptContext.Provider value={{ state, dispatch }}>
      {children}
    </PromptContext.Provider>
  );
};
