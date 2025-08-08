import { apiRequest } from './api_client';

export interface FieldHelp {
  target_models: string;
  providers: string;
  integrations: string;
}

export const getFieldHelp = async (): Promise<FieldHelp> => {
  return apiRequest<FieldHelp>({
    endpoint: '/api/v1/metadata/fields',
    method: 'GET',
  });
};
