import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface FieldHelp {
  target_models: string;
  providers: string;
  integrations: string;
}

export const getFieldHelp = async (): Promise<FieldHelp> => {
  const response = await axios.get(`${API_BASE_URL}/api/v1/metadata/fields`);
  return response.data;
};
