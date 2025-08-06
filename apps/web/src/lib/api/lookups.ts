import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type LookupType = 'models' | 'tools' | 'platforms' | 'purposes';

interface Lookup {
  id: string;
  value: string;
}

export const getLookups = async (type: LookupType): Promise<Lookup[]> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/v1/lookups/${type}`);
    return response.data;
  } catch (error) {
    console.error(`Failed to fetch ${type}:`, error);
    return [];
  }
};

export const createLookup = async (type: LookupType, value: string): Promise<Lookup | null> => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/v1/lookups/${type}`, { value });
    return response.data;
  } catch (error) {
    console.error(`Failed to create ${type}:`, error);
    return null;
  }
};
