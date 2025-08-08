import { Prompt } from '@/types/Prompt';
import { apiRequest } from './api_client';

export const fetchPrompts = async (): Promise<Prompt[]> => {
  return apiRequest<Prompt[]>({
    endpoint: '/api/v1/prompts',
    method: 'GET',
  });
};
