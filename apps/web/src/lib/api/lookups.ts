import { apiRequest } from './api_client';

type LookupType = 'target_models' | 'providers' | 'integrations' | 'use_cases';

interface Lookup {
  id: string;
  value: string;
}

const lookupTypeMap: Record<LookupType, string> = {
  target_models: 'models',
  providers: 'platforms',
  integrations: 'tools',
  use_cases: 'purposes',
};

export const getLookups = async (type: LookupType): Promise<Lookup[]> => {
  try {
    const backendType = lookupTypeMap[type] || type;
    return await apiRequest<Lookup[]>({
      endpoint: `/api/v1/lookups/${backendType}`,
      method: 'GET',
    });
  } catch (error) {
    console.error(`Failed to fetch ${type}:`, error);
    return [];
  }
};

export const createLookup = async (type: LookupType, value: string): Promise<Lookup | null> => {
  try {
    const backendType = lookupTypeMap[type] || type;
    return await apiRequest<Lookup>({
      endpoint: `/api/v1/lookups/${backendType}`,
      method: 'POST',
      body: { value },
    });
  } catch (error) {
    console.error(`Failed to create ${type}:`, error);
    return null;
  }
};
