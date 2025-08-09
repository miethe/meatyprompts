import { Prompt } from '@/types/Prompt';
import { apiRequest } from './api_client';

/**
 * Duplicate an existing prompt by its identifier.
 * @param promptId - Identifier of the prompt to duplicate.
 * @returns The newly created prompt version.
 */
export async function duplicatePrompt(promptId: string): Promise<Prompt> {
  return apiRequest<Prompt>({
    endpoint: `/api/v1/prompts/${promptId}/duplicate`,
    method: 'POST',
  });
}
