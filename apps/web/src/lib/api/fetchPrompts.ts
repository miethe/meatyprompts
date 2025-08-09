import { Prompt } from '@/types/Prompt';
import { apiRequest } from './api_client';

export interface PromptFilters {
  model?: string;
  tool?: string;
  purpose?: string;
}

export const fetchPrompts = async (
  filters: PromptFilters = {}
): Promise<Prompt[]> => {
  const params = new URLSearchParams();
  if (filters.model) params.set('model', filters.model);
  if (filters.tool) params.set('tool', filters.tool);
  if (filters.purpose) params.set('purpose', filters.purpose);
  const query = params.toString();
  return apiRequest<Prompt[]>({
    endpoint: `/api/v1/prompts${query ? `?${query}` : ''}`,
    method: 'GET',
  });
};
