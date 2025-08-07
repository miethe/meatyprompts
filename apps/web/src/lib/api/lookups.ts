import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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
    const response = await axios.get(`${API_BASE_URL}/api/v1/lookups/${backendType}`);
    return response.data;
  } catch (error) {
    console.error(`Failed to fetch ${type}:`, error);
    return [];
  }
};

export const createLookup = async (type: LookupType, value: string): Promise<Lookup | null> => {
  try {
    const backendType = lookupTypeMap[type] || type;
    const response = await axios.post(`${API_BASE_URL}/api/v1/lookups/${backendType}`, { value });
    return response.data;
  } catch (error) {
    console.error(`Failed to create ${type}:`, error);
    return null;
  }
};
