import { ManualPromptInput, Prompt } from '@/types/Prompt';
import { apiRequest } from './api_client';

export async function createPrompt(data: ManualPromptInput): Promise<Prompt> {
  return apiRequest<Prompt>({
    endpoint: '/api/v1/prompts',
    method: 'POST',
    body: data,
  });
}
