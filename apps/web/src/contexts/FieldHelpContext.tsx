import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { getFieldHelp, FieldHelp } from '../lib/api/metadata';

interface FieldHelpContextType {
  help: FieldHelp;
  loading: boolean;
}

const defaultHelp: FieldHelp = {
  target_models: '',
  providers: '',
  integrations: '',
};

const FieldHelpContext = createContext<FieldHelpContextType | undefined>(undefined);

export const FieldHelpProvider = ({ children }: { children: ReactNode }) => {
  const [help, setHelp] = useState<FieldHelp>(defaultHelp);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHelp = async () => {
      try {
        const data = await getFieldHelp();
        setHelp(data);
      } catch (err) {
        console.error('Failed to fetch field help', err);
      } finally {
        setLoading(false);
      }
    };
    fetchHelp();
  }, []);

  return (
    <FieldHelpContext.Provider value={{ help, loading }}>
      {children}
    </FieldHelpContext.Provider>
  );
};

export const useFieldHelp = (): FieldHelpContextType => {
  const context = useContext(FieldHelpContext);
  if (!context) {
    throw new Error('useFieldHelp must be used within a FieldHelpProvider');
  }
  return context;
};
