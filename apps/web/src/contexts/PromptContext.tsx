import { createContext, useReducer, useEffect, FC, ReactNode } from 'react';
import { fetchPrompts } from '@/lib/api/fetchPrompts';
import { Prompt } from '@/types/Prompt';

interface PromptState {
  prompts: Prompt[];
}

interface PromptAction {
  type: 'LOAD';
  payload: Prompt[];
}

interface PromptProviderProps {
  children: ReactNode;
}

export const PromptContext = createContext<{
  state: PromptState;
  dispatch: React.Dispatch<PromptAction>;
} | undefined>(undefined);

function promptReducer(state: PromptState, action: PromptAction): PromptState {
  switch (action.type) {
    case 'LOAD':
      return { ...state, prompts: action.payload };
    default:
      return state;
  }
}

export const PromptProvider: FC<PromptProviderProps> = ({ children }) => {
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
