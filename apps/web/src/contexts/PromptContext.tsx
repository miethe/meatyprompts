import { createContext, useReducer, useEffect, FC, ReactNode, useContext } from 'react';
import { fetchPrompts } from '@/lib/api/fetchPrompts';
import { createPrompt as createPromptApi } from '@/lib/api/createPrompt';
import { Prompt, ManualPromptInput } from '@/types/Prompt';

interface PromptState {
  prompts: Prompt[];
}

type PromptAction =
  | { type: 'LOAD'; payload: Prompt[] }
  | { type: 'CREATE'; payload: Prompt };

interface PromptContextType {
  state: PromptState;
  dispatch: React.Dispatch<PromptAction>;
  createPrompt: (prompt: ManualPromptInput) => Promise<void>;
}

interface PromptProviderProps {
  children: ReactNode;
}

export const PromptContext = createContext<PromptContextType | undefined>(undefined);

function promptReducer(state: PromptState, action: PromptAction): PromptState {
  switch (action.type) {
    case 'LOAD':
      return { ...state, prompts: action.payload };
    case 'CREATE':
      return { ...state, prompts: [action.payload, ...state.prompts] };
    default:
      return state;
  }
}

export const PromptProvider: FC<PromptProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(promptReducer, { prompts: [] });

  useEffect(() => {
    fetchPrompts().then(data => dispatch({ type: 'LOAD', payload: data }));
  }, []);

  const createPrompt = async (prompt: ManualPromptInput) => {
    const newPrompt = await createPromptApi(prompt);
    dispatch({ type: 'CREATE', payload: newPrompt });
  };

  return (
    <PromptContext.Provider value={{ state, dispatch, createPrompt }}>
      {children}
    </PromptContext.Provider>
  );
};

export const usePrompt = () => {
  const context = useContext(PromptContext);
  if (context === undefined) {
    throw new Error('usePrompt must be used within a PromptProvider');
  }
  return context;
};
