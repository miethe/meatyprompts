import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { getLookups, createLookup } from '../lib/api/lookups';

type LookupType = 'target_models' | 'providers' | 'integrations' | 'use_cases';

interface Option {
  value: string;
  label: string;
}

interface LookupState {
  target_models: Option[];
  providers: Option[];
  integrations: Option[];
  use_cases: Option[];
  loading: boolean;
}

interface LookupContextType {
  lookups: LookupState;
  addLookup: (type: LookupType, value: string) => Promise<void>;
}

const LookupContext = createContext<LookupContextType | undefined>(undefined);

export const LookupProvider = ({ children }: { children: ReactNode }) => {
  const [lookups, setLookups] = useState<LookupState>({
    target_models: [],
    providers: [],
    integrations: [],
    use_cases: [],
    loading: true,
  });

  useEffect(() => {
    const fetchAllLookups = async () => {
      try {
        const [target_models, providers, integrations, use_cases] = await Promise.all([
          getLookups('target_models'),
          getLookups('providers'),
          getLookups('integrations'),
          getLookups('use_cases'),
        ]);

        setLookups({
          target_models: target_models.map(m => ({ value: m.value, label: m.value })),
          providers: providers.map(t => ({ value: t.value, label: t.value })),
          integrations: integrations.map(p => ({ value: p.value, label: p.value })),
          use_cases: use_cases.map(p => ({ value: p.value, label: p.value })),
          loading: false,
        });
      } catch (error) {
        console.error("Failed to fetch all lookups", error);
        setLookups(prev => ({ ...prev, loading: false }));
      }
    };
    fetchAllLookups();
  }, []);

  const addLookup = async (type: LookupType, value: string) => {
    const newValue = await createLookup(type, value);
    if (newValue) {
      const newOption = { value: newValue.value, label: newValue.value };
      setLookups(prev => ({
        ...prev,
        [type]: [...prev[type], newOption],
      }));
    }
  };

  return (
    <LookupContext.Provider value={{ lookups, addLookup }}>
      {children}
    </LookupContext.Provider>
  );
};

export const useLookups = () => {
  const context = useContext(LookupContext);
  if (context === undefined) {
    throw new Error('useLookups must be used within a LookupProvider');
  }
  return context;
};
