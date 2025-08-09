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

function getCookie(name: string): string | undefined {
  if (typeof document === 'undefined') return undefined;
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? decodeURIComponent(match[2]) : undefined;
}

export const FieldHelpProvider = ({ children }: { children: ReactNode }) => {
  const [help, setHelp] = useState<FieldHelp>(defaultHelp);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHelp = async () => {
      // Only fetch if session cookie is present
      const session = getCookie('session') || getCookie('meatyprompts_session');
      if (!session) {
        setLoading(false);
        return;
      }
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
