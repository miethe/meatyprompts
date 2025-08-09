import { createContext, useReducer, useEffect, FC, ReactNode, useContext } from 'react';
import { fetchPrompts, PromptFilters } from '@/lib/api/fetchPrompts';
import { createPrompt as createPromptApi } from '@/lib/api/createPrompt';
import { duplicatePrompt as duplicatePromptApi } from '@/lib/api/duplicatePrompt';
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
  filterPrompts: (filters: PromptFilters) => Promise<void>;
  duplicatePrompt: (promptId: string) => Promise<void>;
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

function getCookie(name: string): string | undefined {
  if (typeof document === 'undefined') return undefined;
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? decodeURIComponent(match[2]) : undefined;
}

export const PromptProvider: FC<PromptProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(promptReducer, { prompts: [] });

  useEffect(() => {
    // Only fetch prompts if session cookie is present
    const session = getCookie('session') || getCookie('meatyprompts_session');
    if (!session) return;
    fetchPrompts().then(data => dispatch({ type: 'LOAD', payload: data }));
  }, []);

  const createPrompt = async (prompt: ManualPromptInput) => {
    const newPrompt = await createPromptApi(prompt);
    dispatch({ type: 'CREATE', payload: newPrompt });
  };

  const filterPrompts = async (filters: PromptFilters) => {
    const data = await fetchPrompts(filters);
    dispatch({ type: 'LOAD', payload: data });
  };

  const duplicatePrompt = async (promptId: string) => {
    const newPrompt = await duplicatePromptApi(promptId);
    dispatch({ type: 'CREATE', payload: newPrompt });
  };

  return (
    <PromptContext.Provider value={{ state, dispatch, createPrompt, filterPrompts, duplicatePrompt }}>
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
