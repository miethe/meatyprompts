import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { getLookups, createLookup } from '../lib/api/lookups';

type LookupType = 'models' | 'tools' | 'platforms' | 'purposes';

interface Option {
  value: string;
  label: string;
}

interface LookupState {
  models: Option[];
  tools: Option[];
  platforms: Option[];
  purposes: Option[];
  loading: boolean;
}

interface LookupContextType {
  lookups: LookupState;
  addLookup: (type: LookupType, value: string) => Promise<void>;
}

const LookupContext = createContext<LookupContextType | undefined>(undefined);

export const LookupProvider = ({ children }: { children: ReactNode }) => {
  const [lookups, setLookups] = useState<LookupState>({
    models: [],
    tools: [],
    platforms: [],
    purposes: [],
    loading: true,
  });

  useEffect(() => {
    const fetchAllLookups = async () => {
      try {
        const [models, tools, platforms, purposes] = await Promise.all([
          getLookups('models'),
          getLookups('tools'),
          getLookups('platforms'),
          getLookups('purposes'),
        ]);

        setLookups({
          models: models.map(m => ({ value: m.value, label: m.value })),
          tools: tools.map(t => ({ value: t.value, label: t.value })),
          platforms: platforms.map(p => ({ value: p.value, label: p.value })),
          purposes: purposes.map(p => ({ value: p.value, label: p.value })),
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
